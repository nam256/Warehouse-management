"""Xuất PDF/CSV theo bố cục báo cáo chuẩn — căn lề A4, bảng có viền, tiếng Việt."""

from __future__ import annotations

from io import BytesIO
from typing import Sequence

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.timezone import to_vn_display, utc_now
from app.services.audit import short_ref
from app.services.inventory_report import (
    PERIOD_NOTE,
    STOCK_FORMULA_NOTE,
    InventoryBatchRow,
    InventoryRow,
    IssueRow,
    PeriodInventoryRow,
)
from app.services.pdf_fonts import register_pdf_fonts

# Căn lề báo cáo (theo chuẩn in A4 thông dụng tại VN)
MARGIN_LEFT = 2.5 * cm
MARGIN_RIGHT = 2 * cm
MARGIN_TOP = 2.5 * cm
MARGIN_BOTTOM = 2 * cm


def _fonts() -> tuple[str, str]:
    return register_pdf_fonts()


def _styles() -> dict[str, ParagraphStyle]:
    body, bold = _fonts()
    base = getSampleStyleSheet()
    return {
        "company": ParagraphStyle(
            "company",
            parent=base["Normal"],
            fontName=bold,
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "title": ParagraphStyle(
            "title",
            parent=base["Normal"],
            fontName=bold,
            fontSize=13,
            leading=16,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["Normal"],
            fontName=body,
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12,
        ),
        "meta": ParagraphStyle(
            "meta",
            parent=base["Normal"],
            fontName=body,
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
            spaceAfter=10,
        ),
        "cell": ParagraphStyle(
            "cell",
            parent=base["Normal"],
            fontName=body,
            fontSize=9,
            leading=11,
        ),
        "cell_bold": ParagraphStyle(
            "cell_bold",
            parent=base["Normal"],
            fontName=bold,
            fontSize=9,
            leading=11,
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            fontName=body,
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#64748b"),
        ),
    }


def _footer(canvas, doc) -> None:
    body, _ = _fonts()
    canvas.saveState()
    canvas.setFont(body, 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    page = f"Trang {canvas.getPageNumber()}"
    canvas.drawCentredString(A4[0] / 2, 1.2 * cm, page)
    canvas.restoreState()


def _company_block(title: str, form_code: str | None = None) -> list:
    st = _styles()
    items = [
        Paragraph("CÔNG TY OXEYNS — CHI NHÁNH LONG AN", st["company"]),
        Paragraph(title.upper(), st["title"]),
        Paragraph("Hệ thống quản lý kho &amp; sản xuất tinh dầu (prototype TTTN)", st["subtitle"]),
    ]
    if form_code:
        items.append(Paragraph(f"<b>Loại hồ sơ:</b> {form_code}", st["meta"]))
    items.append(
        Paragraph(f"<b>Ngày lập:</b> {to_vn_display(utc_now())}", st["meta"]),
    )
    items.append(Spacer(1, 0.15 * cm))
    return items


def _kv_table(rows: Sequence[tuple[str, str]], label_width: float = 5.5 * cm) -> Table:
    st = _styles()
    body, _ = _fonts()
    data = [
        [Paragraph(f"<b>{label}</b>", st["cell_bold"]), Paragraph(str(value), st["cell"])]
        for label, value in rows
    ]
    table = Table(data, colWidths=[label_width, A4[0] - MARGIN_LEFT - MARGIN_RIGHT - label_width])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), body),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
            ]
        )
    )
    return table


def _data_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    col_widths: Sequence[float],
    alignments: Sequence[str] | None = None,
) -> Table:
    st = _styles()
    body, _ = _fonts()
    aligns = alignments or ["LEFT"] * len(headers)
    header_row = [Paragraph(f"<b>{h}</b>", st["cell_bold"]) for h in headers]
    body_rows = []
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            align = aligns[i] if i < len(aligns) else "LEFT"
            style = ParagraphStyle(
                f"c{i}",
                parent=st["cell"],
                alignment={"LEFT": TA_LEFT, "RIGHT": TA_RIGHT, "CENTER": TA_CENTER}.get(align, TA_LEFT),
            )
            cells.append(Paragraph(str(cell), style))
        body_rows.append(cells)

    table = Table([header_row, *body_rows], colWidths=list(col_widths), repeatRows=1)
    cmds = [
        ("FONTNAME", (0, 0), (-1, -1), body),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]
    for i, align in enumerate(aligns):
        if align == "RIGHT":
            cmds.append(("ALIGN", (i, 1), (i, -1), "RIGHT"))
        elif align == "CENTER":
            cmds.append(("ALIGN", (i, 1), (i, -1), "CENTER"))
    table.setStyle(TableStyle(cmds))
    return table


def _build_form_pdf(
    title: str,
    form_code: str,
    rows: Sequence[tuple[str, str]],
    document_title: str | None = None,
) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=document_title or title,
    )
    story = _company_block(title, form_code)
    story.append(_kv_table(rows))
    story.append(Spacer(1, 1.2 * cm))
    st = _styles()
    story.append(Paragraph("Người lập biểu &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Người duyệt", st["meta"]))
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()


def _build_table_pdf(
    title: str,
    form_code: str | None,
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    col_widths: Sequence[float],
    alignments: Sequence[str] | None = None,
    note: str | None = None,
    pagesize=A4,
) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=pagesize,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=title,
    )
    story = _company_block(title, form_code)
    story.append(_data_table(headers, rows, col_widths, alignments))
    if note:
        st = _styles()
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(note, st["footer"]))
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()


_CCP_LABEL = {"pass": "Đạt", "fail": "Không đạt", "pending": "Chờ kiểm tra"}


def receipt_pdf(batch_no: str, material: str, qty: float, c14: float | None, ccp: str) -> bytes:
    return _build_form_pdf(
        "Phiếu nhập nguyên liệu",
        "Phiếu nhập nguyên liệu",
        [
            ("Mã lô", short_ref(batch_no)),
            ("Vật tư", material),
            ("Số lượng (kg)", f"{qty:.3f}"),
            ("Chỉ số C14 (dpm/gC)", f"{c14:.4f}" if c14 is not None else "—"),
            ("Kết quả CCP1", _CCP_LABEL.get(ccp, ccp)),
            ("Lưu ý", "Số lượng trên phiếu là SL lúc nhập, không phải tồn hiện tại."),
        ],
        document_title=f"{short_ref(batch_no)} {qty:.3f}kg",
    )


def operation_pdf(order_no: str, step: str, t_top: float | None, t_ca: float | None, ccp2: str) -> bytes:
    from app.services.audit_display import step_label

    return _build_form_pdf(
        "Biên bản vận hành — CCP2",
        "Biên bản vận hành chưng cất",
        [
            ("Mã mẻ sản xuất", short_ref(order_no)),
            ("Công đoạn", step_label(step)),
            ("Nhiệt độ đỉnh (°C)", f"{t_top:.2f}" if t_top is not None else "—"),
            ("Hàm lượng t-CA (%)", f"{t_ca:.3f}" if t_ca is not None else "—"),
            ("Kết quả CCP2", _CCP_LABEL.get(ccp2, ccp2)),
        ],
    )


def material_balance_pdf(order_no: str, inputs: list[tuple[str, float]], output: float, loss: float) -> bytes:
    rows: list[tuple[str, str]] = [("Mã mẻ sản xuất", short_ref(order_no))]
    for batch_no, qty in inputs:
        rows.append((f"Đầu vào — {short_ref(batch_no)}", f"{qty:.3f} kg"))
    rows.extend(
        [
            ("Đầu ra thành phẩm", f"{output:.3f} kg"),
            ("Hao hụt", f"{loss:.3f} kg"),
            ("Tỷ lệ hao hụt (%)", f"{(loss / sum(q for _, q in inputs) * 100) if inputs and sum(q for _, q in inputs) else 0:.2f}%"),
        ]
    )
    return _build_form_pdf("Bảng cân đối nguyên liệu", "Bảng cân đối nguyên liệu", rows)


def mixing_pdf(order_no: str, formula: str | None, mixed_qty: float) -> bytes:
    return _build_form_pdf(
        "Biên bản pha trộn",
        "Biên bản pha trộn",
        [
            ("Mã mẻ sản xuất", short_ref(order_no)),
            ("Công thức", formula or "—"),
            ("Khối lượng pha trộn (kg)", f"{mixed_qty:.3f}"),
        ],
    )


def gc_pdf(batch_no: str, c14: float | None, t_ca: float | None, result: str) -> bytes:
    return _build_form_pdf(
        "Kết quả sắc ký khí (GC)",
        "Kết quả sắc ký khí",
        [
            ("Lô / mẻ", short_ref(batch_no)),
            ("Chỉ số C14", f"{c14:.4f}" if c14 is not None else "—"),
            ("Hàm lượng t-CA (%)", f"{t_ca:.3f}" if t_ca is not None else "—"),
            ("Kết quả", _CCP_LABEL.get(result, result)),
        ],
    )


def release_certificate_pdf(
    batch_no: str,
    ccp_result: str,
    submitted_by: str,
    approved_by: str,
    signed_at,
) -> bytes:
    return _build_form_pdf(
        "Chứng nhận giải phóng lô",
        "Chứng nhận giải phóng lô",
        [
            ("Mã lô", short_ref(batch_no)),
            ("Kết quả CCP", _CCP_LABEL.get(ccp_result, ccp_result)),
            ("Người gửi phê duyệt", submitted_by),
            ("Người ATTP giải phóng", approved_by),
            ("Thời gian ký", to_vn_display(signed_at)),
            ("Quyết định", "Đã giải phóng"),
        ],
    )


def inventory_pdf(
    rows: list[InventoryRow] | list[InventoryBatchRow],
    *,
    view: str = "material",
) -> bytes:
    page = landscape(A4)
    usable = page[0] - MARGIN_LEFT - MARGIN_RIGHT
    if view == "batch":
        headers = ["Mã lô", "Mã VT", "Tên", "HSD", "CCP1", "CL", "Vật lý", "Giữ chỗ", "Khả dụng"]
        body = []
        for row in rows:
            assert isinstance(row, InventoryBatchRow)
            body.append(
                (
                    short_ref(row.batch_no),
                    row.material_code,
                    row.material_name,
                    row.expiry_date.strftime("%d/%m/%Y") if row.expiry_date else "—",
                    row.ccp1_label,
                    row.quality_label,
                    f"{row.on_hand:,.3f}",
                    f"{row.reserved:,.3f}",
                    f"{row.available:,.3f}",
                )
            )
        widths = [usable * x for x in (0.12, 0.10, 0.18, 0.10, 0.08, 0.12, 0.10, 0.10, 0.10)]
        aligns = ["LEFT", "LEFT", "LEFT", "CENTER", "CENTER", "LEFT", "RIGHT", "RIGHT", "RIGHT"]
        title = "Báo cáo tồn kho theo lô"
    else:
        headers = ["Mã", "Tên", "Loại", "Vật lý", "Giữ chỗ", "Khả dụng", "HSD gần", "Chất lượng", "Cảnh báo"]
        body = []
        for row in rows:
            assert isinstance(row, InventoryRow)
            body.append(
                (
                    row.material_code,
                    row.material_name,
                    row.material_type_label,
                    f"{row.on_hand:,.3f}",
                    f"{row.reserved:,.3f}",
                    f"{row.available:,.3f}",
                    row.nearest_expiry.strftime("%d/%m/%Y") if row.nearest_expiry else "—",
                    row.quality_label,
                    row.alert_label,
                )
            )
        widths = [usable * x for x in (0.10, 0.20, 0.10, 0.09, 0.09, 0.09, 0.10, 0.13, 0.10)]
        aligns = ["LEFT", "LEFT", "CENTER", "RIGHT", "RIGHT", "RIGHT", "CENTER", "LEFT", "CENTER"]
        title = "Báo cáo tồn kho hiện tại"
    return _build_table_pdf(
        title,
        "Báo cáo tồn kho hiện tại",
        headers,
        body,
        widths,
        aligns,
        note=STOCK_FORMULA_NOTE,
        pagesize=page,
    )


def issue_voucher_pdf(row: IssueRow) -> bytes:
    expiry = row.expiry_date.strftime("%d/%m/%Y") if row.expiry_date else "—"
    return _build_form_pdf(
        "Phiếu xuất kho",
        "Phiếu xuất kho",
        [
            ("Số phiếu", short_ref(row.reference_no)),
            ("Thời gian xuất", to_vn_display(row.created_at)),
            ("Mã lô", short_ref(row.batch_no)),
            ("Vật tư", f"{row.material_code} — {row.material_name}"),
            ("Hạn dùng", expiry),
            ("Kết quả CCP1", row.ccp1_label),
            ("Trạng thái chất lượng", row.quality_label),
            ("Số lượng xuất (kg)", f"{row.quantity:.3f}"),
            ("Tồn lô hiện tại (kg)", f"{row.remaining_qty:.3f}"),
            ("Loại xuất", row.issue_kind),
            ("Người lập", row.created_by_name or "—"),
            ("Ghi chú", row.notes or "—"),
            ("Thời điểm in", to_vn_display(utc_now())),
            (
                "Lưu ý",
                "Biểu mẫu số hóa nội bộ prototype — không thay phiếu giấy pháp lý.",
            ),
        ],
        document_title=f"{short_ref(row.reference_no)} {row.quantity:.3f}kg",
    )


def issue_ledger_pdf(rows: list[IssueRow]) -> bytes:
    page = landscape(A4)
    usable = page[0] - MARGIN_LEFT - MARGIN_RIGHT
    body = []
    total = 0.0
    for row in rows:
        total += row.quantity
        body.append(
            (
                short_ref(row.reference_no),
                to_vn_display(row.created_at),
                short_ref(row.batch_no),
                f"{row.material_code} — {row.material_name}",
                f"{row.quantity:,.3f}",
                row.issue_kind,
                short_ref(row.order_no) if row.order_no else "—",
                row.created_by_name or "—",
            )
        )
    if not body:
        body.append(("—", "—", "—", "Chưa có phiếu xuất trong kỳ", "0.000", "—", "—", "—"))
    else:
        body.append(("Tổng", "", "", "", f"{total:,.3f}", "", "", ""))
    return _build_table_pdf(
        "Sổ xuất kho",
        "Sổ xuất kho",
        ["Số phiếu PX", "Thời gian VN", "Lô", "Vật tư", "SL (kg)", "Loại", "Mã mẻ", "Người lập"],
        body,
        [usable * x for x in (0.12, 0.14, 0.12, 0.20, 0.08, 0.14, 0.10, 0.10)],
        ["LEFT", "CENTER", "LEFT", "LEFT", "RIGHT", "LEFT", "LEFT", "LEFT"],
        note="Chỉ liệt kê phiếu xuất (OUT). Hoàn tồn do hủy mẻ không hiện trên sổ này.",
        pagesize=page,
    )


def period_inventory_pdf(
    rows: list[PeriodInventoryRow],
    *,
    date_from: str,
    date_to: str,
) -> bytes:
    page = landscape(A4)
    usable = page[0] - MARGIN_LEFT - MARGIN_RIGHT
    body = [
        (
            row.material_code,
            row.material_name,
            row.material_type_label,
            f"{row.opening:,.3f}",
            f"{row.inbound:,.3f}",
            f"{row.outbound:,.3f}",
            f"{row.adjustment:,.3f}",
            f"{row.closing:,.3f}",
        )
        for row in rows
    ]
    if not body:
        body.append(("—", "Chưa có vật tư", "—", "0.000", "0.000", "0.000", "0.000", "0.000"))
    return _build_table_pdf(
        f"Báo cáo tồn kho theo kỳ ({date_from} → {date_to})",
        "Báo cáo tồn kho theo kỳ",
        ["Mã", "Tên", "Loại", "Đầu kỳ", "Nhập", "Xuất", "Hoàn tồn", "Cuối kỳ"],
        body,
        [usable * x for x in (0.10, 0.22, 0.10, 0.10, 0.12, 0.12, 0.12, 0.12)],
        ["LEFT", "LEFT", "CENTER", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT"],
        note=PERIOD_NOTE,
        pagesize=page,
    )


def haccp_audit_pdf(records: list[tuple[str, str, str, str]]) -> bytes:
    usable = A4[0] - MARGIN_LEFT - MARGIN_RIGHT
    body_rows = []
    for ts, kind, target, result in records:
        kind_label = "CCP1 — Nguyên liệu" if kind == "CCP1" else "CCP2 — Chưng cất"
        res = result
        for k, v in _CCP_LABEL.items():
            res = res.replace(k, v)
        body_rows.append((ts, kind_label, target, res))

    return _build_table_pdf(
        "Biên bản giám sát điểm kiểm soát (14 ngày)",
        None,
        ["Thời gian", "Loại CCP", "Đối tượng", "Kết quả"],
        body_rows,
        [usable * 0.22, usable * 0.22, usable * 0.36, usable * 0.20],
        ["CENTER", "LEFT", "LEFT", "CENTER"],
    )
