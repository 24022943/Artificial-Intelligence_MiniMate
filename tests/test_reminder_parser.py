from datetime import datetime
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from minimate.reminder_parser import parse_reminder
from minimate.task_manager import TaskManager
from minimate.intent_baseline import IntentResult
from minimate.storage import SQLiteStore

class ReminderTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 20, 10)
        self.store = SQLiteStore()
        self.addCleanup(self.store.close)
        self.classifier = Mock()
        self.manager = TaskManager(self.classifier, self.store)

    def say(self, text, intent='schedule_reminder'):
        self.classifier.classify.return_value = IntentResult(intent, .99, ())
        return self.manager.handle(text, self.now)

    def test_word_orders(self):
        for text, content in [('Nhắc tôi 9 giờ sáng ngày mai làm bài kiểm tra', 'làm bài kiểm tra'), ('Nhắc tôi sáng mai 9  giờ đi học', 'đi học'), ('Nhắc tôi đi học ngày mai lúc 9 giờ', 'đi học')]:
            with self.subTest(text=text):
                slots = parse_reminder(text, self.now)
                self.assertEqual(slots.content, content)
                self.assertEqual(slots.clock, (9, 0))
                self.assertEqual(slots.day.day, 21)
                self.assertEqual(self.say(text).action, 'create_reminder')

    def test_multiclause_and_confirmation_alias(self):
        self.say('ngày mai tôi phải đi học, nhắc tôi vào lúc 2 giờ chiều')
        row = self.store.upcoming_reminders(self.now)[0]
        self.assertEqual(row['content'], 'đi học')
        self.assertIn('14:00', row['reminder_at'])
        self.say('9 giờ sáng ngày mai đi thi')
        self.assertEqual(self.say('đúng', 'focus_session_control').action, 'create_reminder')
        self.say('đúng', 'focus_session_control')
        self.assertEqual(len(self.store.upcoming_reminders(self.now)), 2)

    def test_delete_single_confirm_and_cancel(self):
        self.say('Nhắc tôi đi học ngày mai 9 giờ')
        self.assertEqual(self.say('Xóa lời nhắc đi học ngày mai').action, 'confirm_delete')
        self.assertEqual(len(self.store.upcoming_reminders(self.now)), 1)
        self.say('không', 'out_of_scope')
        self.assertEqual(len(self.store.upcoming_reminders(self.now)), 1)
        self.say('Xóa lời nhắc đi học ngày mai')
        self.assertEqual(self.say('đúng rồi', 'focus_session_control').action, 'delete_reminder')
        self.say('đồng ý', 'focus_session_control')
        self.assertEqual(len(self.store.upcoming_reminders(self.now)), 0)

    def test_delete_multiple_invalid_choice_and_selection(self):
        for hour in (9, 14):
            self.say(f'Nhắc tôi đi học ngày mai {hour} giờ')
        self.assertEqual(self.say('Xóa lời nhắc đi học ngày mai').action, 'select_reminder')
        self.say('đúng', 'focus_session_control')
        self.say('99', 'out_of_scope')
        self.assertEqual(len(self.store.upcoming_reminders(self.now)), 2)
        self.assertEqual(self.say('chọn 2', 'out_of_scope').action, 'confirm_delete')
        self.assertEqual(len(self.store.upcoming_reminders(self.now)), 2)
        self.say('ok', 'greeting')
        rows = self.store.upcoming_reminders(self.now)
        self.assertEqual(len(rows), 1)
        self.assertIn('09:00', rows[0]['reminder_at'])

    def test_delete_missing_negated_and_changed(self):
        self.assertEqual(self.say('Xóa lời nhắc đi học ngày mai').action, 'reminder_not_found')
        self.say('Nhắc tôi đi học ngày mai 9 giờ')
        self.say('Đừng xóa lời nhắc đi học ngày mai')
        self.assertEqual(len(self.store.upcoming_reminders(self.now)), 1)
        self.say('Xóa lời nhắc đi học ngày mai')
        with self.store.connection:
            self.store.connection.execute("UPDATE reminders SET content='nội dung khác'")
        self.assertEqual(self.say('đồng ý', 'out_of_scope').action, 'reminder_changed')
        self.assertEqual(len(self.store.upcoming_reminders(self.now)), 1)

    def test_pending_slots(self):
        self.assertEqual(self.say('Nhắc tôi đi học', 'repeat_response').action, 'request_reminder_details')
        self.assertEqual(self.say('Sáng mai lúc 9 giờ', 'out_of_scope').action, 'create_reminder')
        self.assertEqual(self.store.upcoming_reminders(self.now)[0]['content'], 'đi học')

    def test_pending_content(self):
        self.say('Nhắc tôi ngày mai lúc 9 giờ')
        self.assertEqual(self.say('làm bài kiểm tra', 'out_of_scope').action, 'create_reminder')

    def test_confirm_or_cancel(self):
        self.assertEqual(self.say('9 giờ sáng ngày mai đi học').action, 'confirm_reminder')
        self.assertEqual(self.store.upcoming_reminders(self.now), [])
        self.assertEqual(self.say('đồng ý', 'out_of_scope').action, 'create_reminder')
        self.say('Nhắc tôi ăn cơm')
        self.say('hủy', 'focus_session_control')
        self.assertIsNone(self.manager.pending_reminder)
        self.assertEqual(len(self.store.upcoming_reminders(self.now)), 1)

    def test_invalid_and_unsupported(self):
        for text in ('Nhắc tôi đi học ngày mai 25 giờ', 'Nhắc tôi đi học hôm nay 8 giờ', 'Nhắc tôi thức dậy 6 giờ sáng mỗi ngày', 'Đừng nhắc tôi đi học ngày mai 9 giờ', 'Xóa lời nhắc vừa tạo'):
            self.say(text)
        self.assertEqual(self.store.upcoming_reminders(self.now), [])

    def test_lookup_day_and_new_request(self):
        self.say('Nhắc tôi đi thi sau 2 ngày lúc 8 giờ')
        self.say('Nhắc tôi đi học ngày mai lúc 9 giờ')
        answer = self.say('Tra cứu những lịch nhắc ngày mai')
        self.assertEqual(answer.action, 'list_reminders')
        self.assertIn('đi học', answer.text)
        self.assertNotIn('đi thi', answer.text)
