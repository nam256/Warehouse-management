"""Đăng ký font Unicode hỗ trợ tiếng Việt cho PDF."""

from __future__ import annotations

import os
import platform
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_FONT_BODY = "VN-Regular"
_FONT_BOLD = "VN-Bold"
_REGISTERED = False

# Font đóng gói kèm dự án (DejaVu — LGPL, có thể thêm thủ công vào app/fonts/)
_BUNDLED = Path(__file__).resolve().parent.parent / "fonts"


def _pairs() -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []

    bundled_r = _BUNDLED / "DejaVuSans.ttf"
    bundled_b = _BUNDLED / "DejaVuSans-Bold.ttf"
    if bundled_r.is_file() and bundled_b.is_file():
        pairs.append((bundled_r, bundled_b))

    if platform.system() == "Windows":
        win = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
        for regular, bold in [
            ("arial.ttf", "arialbd.ttf"),
            ("tahoma.ttf", "tahomabd.ttf"),
            ("segoeui.ttf", "segoeuib.ttf"),
        ]:
            pairs.append((win / regular, win / bold))

    for base in (
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/TTF",
        "/usr/local/share/fonts",
    ):
        root = Path(base)
        pairs.append((root / "DejaVuSans.ttf", root / "DejaVuSans-Bold.ttf"))

    return pairs


def register_pdf_fonts() -> tuple[str, str]:
    global _REGISTERED
    if _REGISTERED:
        return _FONT_BODY, _FONT_BOLD

    for regular, bold in _pairs():
        if regular.is_file() and bold.is_file():
            pdfmetrics.registerFont(TTFont(_FONT_BODY, str(regular)))
            pdfmetrics.registerFont(TTFont(_FONT_BOLD, str(bold)))
            pdfmetrics.registerFontFamily(
                "VN",
                normal=_FONT_BODY,
                bold=_FONT_BOLD,
                italic=_FONT_BODY,
                boldItalic=_FONT_BOLD,
            )
            _REGISTERED = True
            return _FONT_BODY, _FONT_BOLD

    # Fallback — thiếu dấu tiếng Việt
    import reportlab

    font_dir = Path(reportlab.__path__[0]) / "fonts"
    pdfmetrics.registerFont(TTFont(_FONT_BODY, str(font_dir / "Vera.ttf")))
    pdfmetrics.registerFont(TTFont(_FONT_BOLD, str(font_dir / "VeraBd.ttf")))
    _REGISTERED = True
    return _FONT_BODY, _FONT_BOLD
