import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import main
from minimate.intent_baseline import IntentResult
from minimate.intent_hf import HFIntentClassifier, ClassifierError, LABELS
from minimate.task_manager import TaskManager, SessionState
from minimate.storage import SQLiteStore


class IntegrationTests(unittest.TestCase):
    def test_local_loader_once_and_mapping(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            labels = sorted(LABELS, reverse=True)
            (path / 'config.json').write_text(json.dumps({'id2label': dict(enumerate(labels))}))
            for name in ('tokenizer.json', 'tokenizer_config.json', 'model.safetensors'):
                (path / name).touch()
            torch, transformers = MagicMock(), MagicMock()
            scores = MagicMock()
            scores.argmax.return_value = 0
            scores.__getitem__.return_value = 0.87
            model = transformers.AutoModelForSequenceClassification.from_pretrained.return_value
            model.return_value.logits.softmax.return_value.__getitem__.return_value = scores
            with patch.dict(sys.modules, {'torch': torch, 'transformers': transformers}):
                classifier = HFIntentClassifier(path)
                for _ in range(2):
                    self.assertEqual(classifier.classify('Xin chào'), IntentResult(labels[0], 0.87, ()))
                self.assertEqual(classifier.classify(' ').name, 'out_of_scope')
                transformers.AutoModelForSequenceClassification.from_pretrained.assert_called_once_with(path, local_files_only=True)
                transformers.AutoTokenizer.from_pretrained.assert_called_once_with(path, local_files_only=True)
                classifier.tokenizer.assert_called_with('Xin chào', return_tensors='pt', truncation=True, max_length=32)
            with patch.dict(sys.modules, {'transformers': None}):
                with self.assertRaisesRegex(ClassifierError, 'Thiếu thư viện'):
                    HFIntentClassifier(path)

    def test_missing_model(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ClassifierError, 'thiếu file'):
                HFIntentClassifier(folder)

    def test_cli_default_and_keyword(self):
        with tempfile.TemporaryDirectory() as folder:
            for mode in ([], ['--classifier', 'keyword']):
                with patch.object(main, 'HFIntentClassifier') as hf, patch.object(sys, 'argv', ['main', '--db', str(Path(folder) / 'test.db'), '--text', 'xin chào'] + mode), contextlib.redirect_stdout(io.StringIO()) as output:
                    hf.return_value.classify.return_value = IntentResult('greeting', .8, ())
                    main.main()
                    self.assertIn('greet', output.getvalue())
                    self.assertEqual(hf.call_count, 0 if mode else 1)

    def test_model_routing_and_safety(self):
        classifier = MagicMock()
        store = SQLiteStore()
        self.addCleanup(store.close)
        manager = TaskManager(classifier, store)
        def handle(intent, text):
            classifier.classify.return_value = IntentResult(intent, .999, ())
            return manager.handle(text)
        self.assertEqual(handle('focus_session_control', 'Bật điều hòa giúp em').action, 'request_clarification')
        handle('focus_session_control', 'Bắt đầu học')
        self.assertEqual(handle('greeting', '25 phút').action, 'start_session')
        started = manager.session.started_at
        self.assertEqual(handle('focus_session_control', 'Bắt đầu học 10 phút').action, 'no_op')
        self.assertEqual(manager.session.started_at, started)
        self.assertEqual(handle('check_focus_session', 'Còn bao lâu?').action, 'report_remaining_time')
        self.assertEqual(handle('schedule_reminder', 'Tôi có lịch gì vào ngày mai?').action, 'list_reminders')
        self.assertEqual(handle('schedule_reminder', 'Xóa lời nhắc vừa tạo').action, 'reminder_not_found')
        handle('focus_session_control', 'Xóa lời nhắc vừa tạo')
        handle('schedule_reminder', 'Bật điều hòa giúp em')
        self.assertEqual(manager.session.state, SessionState.ACTIVE)
        self.assertEqual(store.upcoming_reminders(), [])
