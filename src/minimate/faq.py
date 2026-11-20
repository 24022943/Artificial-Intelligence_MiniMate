"""Small, offline FAQ used by MINIMATE's ``open_question`` intent."""

from __future__ import annotations

from .intent_baseline import normalize


FAQ_TOPICS: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("pomodoro",),
        "Pomodoro là cách học theo phiên ngắn: thường tập trung 25 phút rồi nghỉ 5 phút.",
    ),
    (
        ("tap trung", "mat tap trung"),
        "Để tập trung hơn, hãy chọn một việc nhỏ, tắt thông báo và học trong một phiên có thời lượng rõ ràng.",
    ),
    (
        ("nghi giai lao", "giai lao", "nghi ngoi"),
        "Sau mỗi phiên học, bạn nên nghỉ ngắn 5 đến 10 phút để mắt và não được hồi phục.",
    ),
    (
        ("lap ke hoach", "ke hoach hoc", "lich hoc"),
        "Hãy liệt kê việc cần học, ước lượng thời gian cho từng việc và ưu tiên việc gần hạn trước.",
    ),
    (
        ("tri hoan", "luoi hoc", "khong muon hoc"),
        "Khi bị trì hoãn, hãy bắt đầu bằng 5 phút đầu tiên của một việc nhỏ thay vì chờ có động lực hoàn hảo.",
    ),
)


def answer_faq(text: str) -> str | None:
    """Return an offline answer when a known study topic appears in *text*."""
    normalized = normalize(text)
    for keywords, answer in FAQ_TOPICS:
        if any(keyword in normalized for keyword in keywords):
            return answer
    return None
