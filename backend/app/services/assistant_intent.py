"""Phân intent câu hỏi trợ lý — cấm default tồn kho."""

from __future__ import annotations

import re

from app.services.report_kb import is_report_howto_question

Intent = str

_GREET = re.compile(
    r"^(xin chào|chào bạn|chào trợ lý|trợ lý ơi|chào|hello|hi|hey|alo)[\s!.,?]*$",
    re.IGNORECASE,
)
_THANKS = re.compile(
    r"^(cảm ơn( bạn)?|cam on|thanks|thank you|ok|oke|được rồi|duoc roi)[\s!.,?]*$",
    re.IGNORECASE,
)

GREET_REPLY = "Xin chào. Trợ lý chỉ đọc — hỏi tồn kho, phiếu xuất, hạn dùng hoặc CAPA."
THANKS_REPLY = "Không có gì. Hỏi thêm khi cần."
OUT_OF_SCOPE_REPLY = "Tôi chỉ hỗ trợ QMS: tồn kho, xuất kho, lô, hạn dùng, CAPA. Bấm gợi ý giúp."
CLARIFY_REPLY = "Thiếu mã lô (ví dụ TP-001) hoặc nói rõ: in phiếu xuất, xem tồn, hay thu hồi."

CANNED: dict[str, str] = {
    "greet": GREET_REPLY,
    "thanks": THANKS_REPLY,
    "out_of_scope": OUT_OF_SCOPE_REPLY,
    "clarify": CLARIFY_REPLY,
}


def normalize(question: str) -> str:
    return " ".join(question.lower().strip().split())


def classify_intent(question: str) -> Intent:
    text = normalize(question)
    if not text:
        return "clarify"
    if _GREET.fullmatch(text):
        return "greet"
    if _THANKS.fullmatch(text):
        return "thanks"
    if any(token in text for token in ("thu hồi", "thu hoi", "recall")):
        return "recall"
    if any(token in text for token in ("capa", "ncr", "khắc phục", "khac phuc")):
        return "capa"
    if is_report_howto_question(question):
        return "howto_report"
    if any(
        token in text
        for token in (
            "hết hạn",
            "het han",
            "hạn dùng",
            "han dung",
            "fefo",
            "expiry",
            "sắp hết hạn",
            "sap het han",
        )
    ):
        return "fefo"
    if any(
        token in text
        for token in (
            "trạng thái lô",
            "trang thai lo",
            "ccp1",
            "quarantine",
            "giải phóng",
            "giai phong",
        )
    ):
        return "batch"
    if any(
        token in text
        for token in ("tồn kho", "ton kho", "inventory", "còn bao nhiêu", "con bao nhieu")
    ):
        return "inventory"
    if len(text) < 40 and any(token in text for token in ("in giúp", "lô này", "cái đó", "lo nay")):
        return "clarify"
    return "out_of_scope"


def canned_reply(intent: Intent) -> str | None:
    return CANNED.get(intent)
