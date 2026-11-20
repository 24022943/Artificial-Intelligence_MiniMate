from datetime import datetime, timedelta
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from minimate.intent_baseline import KeywordIntentClassifier
from minimate.task_manager import DeviceState, SessionState, TaskManager
from minimate.storage import SQLiteStore


class IntentBaselineTests(unittest.TestCase):
    def test_question_words_and_unsupported_commands(self) -> None:
        classifier = KeywordIntentClassifier()
        samples = {
            "Tại sao học lâu lại mệt?": "open_question",
            "Phiên học còn bao lâu?": "check_focus_session",
            "Ngày mai mình có lịch gì?": "schedule_reminder",
            "Bạn vừa nói gì vậy?": "repeat_response",
            "Xóa lời nhắc nộp bài": "out_of_scope",
            "Thêm 10 phút vào phiên học": "out_of_scope",
            "Mở camera giúp mình": "out_of_scope",
        }
        for text, intent in samples.items():
            with self.subTest(text=text):
                self.assertEqual(classifier.classify(text).name, intent)

    def test_recognizes_all_seven_intents(self) -> None:
        samples = {
            "xin chào minimate": "greeting",
            "bắt đầu học 25 phút": "focus_session_control",
            "còn bao lâu": "check_focus_session",
            "nhắc tôi đi thi sau 2 ngày lúc 8 giờ": "schedule_reminder",
            "nhắc lại": "repeat_response",
            "giải thích thuật toán này": "open_question",
            "ngày mai 8 giờ": "out_of_scope",
        }
        classifier = KeywordIntentClassifier()
        for text, intent in samples.items():
            self.assertEqual(classifier.classify(text).name, intent)


class TaskManagerTests(unittest.TestCase):
    def test_start_needs_duration_then_starts(self) -> None:
        manager = TaskManager()
        now = datetime(2026, 11, 6, 9, 0)
        clarification = manager.handle("bắt đầu học", now)
        self.assertEqual(clarification.device_state, DeviceState.CLARIFICATION)
        started = manager.handle("25 phút", now)
        self.assertEqual(started.action, "start_session")
        self.assertEqual(manager.session.state, SessionState.ACTIVE)

    def test_remaining_time(self) -> None:
        manager = TaskManager()
        now = datetime(2026, 11, 6, 9, 0)
        manager.handle("bắt đầu học 25 phút", now)
        response = manager.handle("còn bao lâu", now + timedelta(minutes=5))
        self.assertIn("20 phút", response.text)

    def test_persists_session_and_command_history(self) -> None:
        store = SQLiteStore()
        now = datetime(2026, 11, 6, 9, 0)
        manager = TaskManager(store=store)
        manager.handle("bắt đầu học 25 phút", now)
        restored_manager = TaskManager(store=store)
        self.assertEqual(restored_manager.session.state, SessionState.ACTIVE)
        self.assertEqual(restored_manager.session.duration_minutes, 25)
        self.assertEqual(store.command_count(), 1)

    def test_creates_reminder_from_relative_time(self) -> None:
        store = SQLiteStore()
        manager = TaskManager(store=store)
        now = datetime(2026, 11, 7, 9, 0)
        response = manager.handle("nhắc tôi đi thi sau 2 ngày lúc 8 giờ", now)
        self.assertEqual(response.intent, "schedule_reminder")
        self.assertEqual(response.action, "create_reminder")
        self.assertEqual(store.upcoming_reminders(now)[0]["content"], "đi thi")

    def test_cancel_session(self) -> None:
        manager = TaskManager()
        now = datetime(2026, 11, 7, 9, 0)
        manager.handle("bắt đầu học 25 phút", now)
        response = manager.handle("dừng học", now)
        self.assertEqual(response.action, "cancel_session")
        self.assertEqual(manager.session.state, SessionState.CANCELLED)

    def test_lists_only_upcoming_reminders(self) -> None:
        store = SQLiteStore()
        manager = TaskManager(store=store)
        now = datetime(2026, 11, 7, 9, 0)
        store.add_reminder("viec da qua", now - timedelta(days=1), now - timedelta(days=2))
        manager.handle("nhắc tôi nộp bài ngày mai lúc 8 giờ", now)
        response = manager.handle("xem lịch đã lưu", now)
        self.assertEqual(response.action, "list_reminders")
        self.assertIn("nộp bài", response.text)
        self.assertNotIn("viec da qua", response.text)

    def test_repeat_response_persists_in_store(self) -> None:
        store = SQLiteStore()
        now = datetime(2026, 11, 7, 9, 0)
        TaskManager(store=store).handle("xin chào", now)
        response = TaskManager(store=store).handle("nhắc lại", now)
        self.assertEqual(response.action, "repeat_response")
        self.assertIn("Chào bạn", response.text)

    def test_faq_and_unknown_open_question(self) -> None:
        manager = TaskManager()
        faq = manager.handle("Pomodoro là gì?", datetime(2026, 11, 7, 9, 0))
        self.assertEqual(faq.action, "answer_faq")
        self.assertIn("25 phút", faq.text)
        unknown = manager.handle("giải thích blockchain", datetime(2026, 11, 7, 9, 0))
        self.assertEqual(unknown.action, "faq_not_found")

    def test_out_of_scope_and_empty_input(self) -> None:
        manager = TaskManager()
        for text in ("", "ngày mai 8 giờ"):
            response = manager.handle(text, datetime(2026, 11, 7, 9, 0))
            self.assertEqual(response.intent, "out_of_scope")
            self.assertEqual(response.action, "request_clarification")


if __name__ == "__main__":
    unittest.main()
