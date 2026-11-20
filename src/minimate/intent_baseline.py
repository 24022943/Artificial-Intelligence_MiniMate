"""A transparent Vietnamese keyword baseline for MINIMATE's seven intents."""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


@dataclass(frozen=True)
class IntentResult:
    name: str
    confidence: float
    matched_keywords: tuple[str, ...]


def normalize(text: str) -> str:
    """Lowercase and remove Vietnamese accents so rules handle ordinary typing."""
    text = text.lower().replace("đ", "d")
    text = "".join(
        char for char in unicodedata.normalize("NFD", text) if unicodedata.category(char) != "Mn"
    )
    return re.sub(r"\s+", " ", text).strip()


INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "greeting": ("xin chao", "chao", "hello", "hi minimate"),
    "focus_session_control": (
        "bat dau hoc", "bat dau phien hoc", "hoc trong", "bat dau pomodoro",
        "huy phien", "dung hoc", "ket thuc phien", "huy hoc",
    ),
    "check_focus_session": (
        "con bao lau", "con may phut", "thoi gian con lai",
        "trang thai phien", "dang hoc", "phien hoc the nao", "phien hoc con",
    ),
    "schedule_reminder": (
        "nhac toi", "dat loi nhac", "tao loi nhac", "lich da luu",
        "xem lich", "tra cuu lich", "co lich gi", "nhac minh", "nhac to",
    ),
    "repeat_response": ("nhac lai", "lap lai", "noi lai", "vua noi gi"),
    "open_question": (
        "giai thich", "giai nghia", "tai sao", "vi sao", "sao lai", "lam sao",
        "lam the nao", "cach nao", "la gi", "nghia la gi", "y la gi",
        "cho vi du", "vi du ve", "khac nhau the nao", "khac gi", "co nen",
        "nhu the nao", "ra sao", "dung de lam gi", "hoat dong the nao", "cho toi hoi",
        "pomodoro", "tap trung", "nghi giai lao", "giai lao", "lap ke hoach",
        "ke hoach hoc", "tri hoan", "luoi hoc", "khong muon hoc",
    ),
}


class KeywordIntentClassifier:
    """Classify text with longest-keyword matching and an out-of-scope fallback."""

    def classify(self, text: str) -> IntentResult:
        normalized = normalize(text)
        # These actions are outside the current supported feature set.
        unsupported = re.search(
            r"\b(?:xoa|huy|bo|sua|doi|doi gio|doi ngay)\b.{0,40}\b(?:loi nhac|lich nhac|reminder)\b"
            r"|\b(?:tam dung|tiep tuc|keo dai)\b.{0,30}\b(?:phien|dong ho|bo dem)\b"
            r"|\b(?:them|cong)\b.{0,30}\bphut\b.{0,30}\b(?:phien|dong ho|bo dem)\b"
            r"|\b(?:mo|bat)\s+camera\b",
            normalized,
        )
        if unsupported:
            return IntentResult("out_of_scope", 0.8, (unsupported.group(),))
        candidates: list[tuple[int, str, tuple[str, ...]]] = []
        for intent, keywords in INTENT_KEYWORDS.items():
            matches = tuple(keyword for keyword in keywords if keyword in normalized)
            if matches:
                candidates.append((max(len(keyword) for keyword in matches), intent, matches))
        if not candidates:
            return IntentResult("out_of_scope", 0.0, ())
        score, intent, matches = max(candidates, key=lambda item: item[0])
        return IntentResult(intent, round(min(0.95, 0.45 + score / 40), 2), matches)
