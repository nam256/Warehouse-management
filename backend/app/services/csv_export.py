"""Xuất CSV chuẩn báo cáo — UTF-8 BOM, tiêu đề công ty, căn cột số."""

from __future__ import annotations

import csv
from io import StringIO

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


def _csv_writer() -> tuple[StringIO, csv.writer]:
    output = StringIO()
    writer = csv.writer(output, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)
    return output, writer


def _header(writer: csv.writer, title: str, form_code: str | None = None) -> None:
    writer.writerow(["CÔNG TY OXEYNS — CHI NHÁNH LONG AN"])
    writer.writerow([title])
    if form_code:
        writer.writerow([f"Loại hồ sơ: {form_code}"])
    writer.writerow([f"Ngày lập: {to_vn_display(utc_now())}"])
    writer.writerow([])


def inventory_csv_rows(
    rows: list[InventoryRow] | list[InventoryBatchRow],
    *,
    view: str = "material",
) -> str:
    """Trả về nội dung CSV (có BOM) cho báo cáo tồn kho."""
    output, writer = _csv_writer()
    title = "BÁO CÁO TỒN KHO THEO LÔ" if view == "batch" else "BÁO CÁO TỒN KHO ĐỊNH KỲ"
    _header(writer, title, "Báo cáo tồn kho hiện tại")

    if view == "batch":
        writer.writerow(
            [
                "STT",
                "Mã lô",
                "Mã vật tư",
                "Tên vật tư",
                "Loại",
                "Đơn vị tính",
                "Tồn vật lý (kg)",
                "Đang giữ chỗ (kg)",
                "Khả dụng (kg)",
                "HSD",
                "CCP1",
                "Trạng thái chất lượng",
            ]
        )
        for i, row in enumerate(rows, start=1):
            assert isinstance(row, InventoryBatchRow)
            writer.writerow(
                [
                    i,
                    short_ref(row.batch_no),
                    row.material_code,
                    row.material_name,
                    row.material_type_label,
                    row.unit,
                    f"{row.on_hand:.3f}",
                    f"{row.reserved:.3f}",
                    f"{row.available:.3f}",
                    row.expiry_date.strftime("%d/%m/%Y") if row.expiry_date else "—",
                    row.ccp1_label,
                    row.quality_label,
                ]
            )
    else:
        writer.writerow(
            [
                "STT",
                "Mã vật tư",
                "Tên vật tư",
                "Loại",
                "Đơn vị tính",
                "Tồn vật lý",
                "Đang giữ chỗ",
                "Khả dụng",
                "HSD gần nhất",
                "Trạng thái chất lượng",
                "Tồn tối thiểu (kg)",
                "Cảnh báo",
            ]
        )
        for i, row in enumerate(rows, start=1):
            assert isinstance(row, InventoryRow)
            writer.writerow(
                [
                    i,
                    row.material_code,
                    row.material_name,
                    row.material_type_label,
                    row.unit,
                    f"{row.on_hand:.3f}",
                    f"{row.reserved:.3f}",
                    f"{row.available:.3f}",
                    row.nearest_expiry.strftime("%d/%m/%Y") if row.nearest_expiry else "—",
                    row.quality_label,
                    f"{row.min_stock:.3f}",
                    row.alert_label,
                ]
            )

    writer.writerow([])
    writer.writerow([STOCK_FORMULA_NOTE])
    writer.writerow(["Ghi chú: File mã hóa UTF-8 — mở bằng Excel hoặc LibreOffice Calc."])
    return "\ufeff" + output.getvalue()


def issues_csv_rows(rows: list[IssueRow]) -> str:
    output, writer = _csv_writer()
    _header(writer, "SỔ XUẤT KHO", "Sổ xuất kho")
    writer.writerow(
        [
            "STT",
            "Số phiếu PX",
            "Thời gian VN",
            "Lô",
            "Vật tư",
            "SL (kg)",
            "Loại",
            "Mã mẻ",
            "Người lập",
            "Ghi chú",
        ]
    )
    total = 0.0
    for i, row in enumerate(rows, start=1):
        total += row.quantity
        writer.writerow(
            [
                i,
                short_ref(row.reference_no),
                to_vn_display(row.created_at),
                short_ref(row.batch_no),
                f"{row.material_code} — {row.material_name}",
                f"{row.quantity:.3f}",
                row.issue_kind,
                short_ref(row.order_no) if row.order_no else "—",
                row.created_by_name or "—",
                row.notes or "",
            ]
        )
    writer.writerow([])
    writer.writerow(["Tổng", "", "", "", "", f"{total:.3f}", "", "", "", ""])
    writer.writerow([])
    writer.writerow(["Ghi chú: File mã hóa UTF-8 — mở bằng Excel hoặc LibreOffice Calc."])
    return "\ufeff" + output.getvalue()


def period_inventory_csv_rows(
    rows: list[PeriodInventoryRow],
    *,
    date_from: str,
    date_to: str,
) -> str:
    output, writer = _csv_writer()
    _header(writer, "BÁO CÁO TỒN KHO THEO KỲ", "Báo cáo tồn kho theo kỳ")
    writer.writerow([f"Kỳ báo cáo: {date_from} → {date_to}"])
    writer.writerow([])
    writer.writerow(
        [
            "STT",
            "Mã vật tư",
            "Tên vật tư",
            "Loại",
            "Đơn vị tính",
            "Tồn đầu kỳ",
            "Nhập trong kỳ",
            "Xuất trong kỳ",
            "Hoàn tồn / điều chỉnh",
            "Tồn cuối kỳ",
        ]
    )
    for i, row in enumerate(rows, start=1):
        writer.writerow(
            [
                i,
                row.material_code,
                row.material_name,
                row.material_type_label,
                row.unit,
                f"{row.opening:.3f}",
                f"{row.inbound:.3f}",
                f"{row.outbound:.3f}",
                f"{row.adjustment:.3f}",
                f"{row.closing:.3f}",
            ]
        )
    writer.writerow([])
    writer.writerow([PERIOD_NOTE])
    writer.writerow(["Ghi chú: File mã hóa UTF-8 — mở bằng Excel hoặc LibreOffice Calc."])
    return "\ufeff" + output.getvalue()
