import csv
import hashlib
import io
import json
import math
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import CCPStatus, GcImport, LabTest, StockBatch
from app.services.capa import create_capa_for_failure
from app.services.ccp import evaluate_ccp1, evaluate_ccp2

MAX_FILE_SIZE = 1024 * 1024
MAX_ROWS = 1000
REQUIRED_COLUMNS = {"batch_no", "analyte", "value", "unit"}
OPTIONAL_COLUMNS = {"tested_at"}
ALLOWED_ANALYTES = {"C14", "tCA"}


class GcImportValidationError(ValueError):
    def __init__(self, errors: list[str]):
        super().__init__("Tệp CSV không hợp lệ")
        self.errors = errors


@dataclass(frozen=True)
class ParsedGcRow:
    line: int
    batch: StockBatch
    analyte: str
    value: float
    tested_at: datetime | None


@dataclass(frozen=True)
class GcImportResult:
    imported: int
    duplicate: bool
    sha256: str
    row_count: int


def import_gc_csv(
    db: Session,
    *,
    content: bytes,
    filename: str,
    imported_by_id: int,
) -> GcImportResult:
    if len(content) > MAX_FILE_SIZE:
        raise GcImportValidationError(["Tệp vượt quá giới hạn 1 MB."])
    if not content:
        raise GcImportValidationError(["Tệp CSV không có dữ liệu."])

    digest = hashlib.sha256(content).hexdigest()
    existing = db.query(GcImport).filter(GcImport.sha256 == digest).first()
    if existing:
        return GcImportResult(
            imported=0,
            duplicate=True,
            sha256=digest,
            row_count=existing.row_count,
        )

    rows = _parse_and_validate(db, content)
    tests: list[tuple[LabTest, ParsedGcRow]] = []
    for row in rows:
        if row.analyte == "C14":
            status = CCPStatus(evaluate_ccp1(row.value))
            test = LabTest(
                batch_id=row.batch.id,
                test_type="C14",
                gc_data=_gc_data(row),
                c14=row.value,
                result_status=status,
                created_by_id=imported_by_id,
                created_at=row.tested_at,
            )
            row.batch.ccp1_c14 = row.value
            row.batch.ccp1_status = status
        else:
            status = CCPStatus(evaluate_ccp2(None, row.value))
            test = LabTest(
                order_id=row.batch.source_order_id,
                batch_id=row.batch.id,
                test_type="tCA",
                gc_data=_gc_data(row),
                t_ca_percent=row.value,
                result_status=status,
                created_by_id=imported_by_id,
                created_at=row.tested_at,
            )
        db.add(test)
        tests.append((test, row))

    db.flush()
    for test, _ in tests:
        if test.result_status == CCPStatus.fail:
            create_capa_for_failure(
                db,
                "lab_test",
                test.id,
                created_by_id=imported_by_id,
            )

    db.add(
        GcImport(
            filename=(filename or "gc.csv")[-255:],
            sha256=digest,
            row_count=len(rows),
            imported_by_id=imported_by_id,
        )
    )
    db.flush()
    return GcImportResult(
        imported=len(rows),
        duplicate=False,
        sha256=digest,
        row_count=len(rows),
    )


def _parse_and_validate(db: Session, content: bytes) -> list[ParsedGcRow]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise GcImportValidationError(
            ["Tệp phải sử dụng mã hóa UTF-8."]
        ) from exc

    reader = csv.DictReader(io.StringIO(text, newline=""))
    headers = reader.fieldnames
    if not headers:
        raise GcImportValidationError(["Thiếu dòng tiêu đề CSV."])
    normalized_headers = [header.strip() for header in headers]
    header_set = set(normalized_headers)
    if len(header_set) != len(normalized_headers):
        raise GcImportValidationError(["Tiêu đề CSV có cột bị trùng."])
    missing = REQUIRED_COLUMNS - header_set
    unknown = header_set - REQUIRED_COLUMNS - OPTIONAL_COLUMNS
    if missing or unknown:
        errors = []
        if missing:
            errors.append(f"Thiếu cột bắt buộc: {', '.join(sorted(missing))}.")
        if unknown:
            errors.append(f"Cột không được hỗ trợ: {', '.join(sorted(unknown))}.")
        raise GcImportValidationError(errors)
    reader.fieldnames = normalized_headers

    raw_rows: list[tuple[int, dict[str, str | None]]] = []
    for item in reader:
        if item.get(None):
            raw_rows.append((reader.line_num, item))
            continue
        if not any((value or "").strip() for value in item.values()):
            continue
        raw_rows.append((reader.line_num, item))
        if len(raw_rows) > MAX_ROWS:
            raise GcImportValidationError(["Tệp vượt quá giới hạn 1.000 dòng dữ liệu."])

    if not raw_rows:
        raise GcImportValidationError(["Tệp CSV không có dòng dữ liệu."])

    batch_numbers = {
        (item.get("batch_no") or "").strip()
        for _, item in raw_rows
        if (item.get("batch_no") or "").strip()
    }
    batches = (
        db.query(StockBatch).filter(StockBatch.batch_no.in_(batch_numbers)).all()
        if batch_numbers
        else []
    )
    batches_by_no = {batch.batch_no: batch for batch in batches}

    errors: list[str] = []
    parsed: list[ParsedGcRow] = []
    for line, item in raw_rows:
        row_errors: list[str] = []
        batch_no = (item.get("batch_no") or "").strip()
        analyte = (item.get("analyte") or "").strip()
        unit = (item.get("unit") or "").strip()
        value_text = (item.get("value") or "").strip()
        tested_at_text = (item.get("tested_at") or "").strip()

        batch = batches_by_no.get(batch_no)
        if not batch_no:
            row_errors.append("batch_no không được để trống")
        elif batch is None:
            row_errors.append(f"không tìm thấy lô {batch_no}")
        if analyte not in ALLOWED_ANALYTES:
            row_errors.append("analyte chỉ nhận C14 hoặc tCA")
        if unit != "%":
            row_errors.append("unit phải là %")

        try:
            value = float(value_text)
            if not math.isfinite(value):
                raise ValueError
        except ValueError:
            value = 0.0
            row_errors.append("value phải là số hữu hạn")

        tested_at = None
        if tested_at_text:
            try:
                tested_at = datetime.fromisoformat(tested_at_text.replace("Z", "+00:00"))
                if tested_at.tzinfo is not None:
                    tested_at = tested_at.replace(tzinfo=None)
            except ValueError:
                row_errors.append("tested_at phải theo định dạng ISO 8601")

        if row_errors:
            errors.append(f"Dòng {line}: {'; '.join(row_errors)}.")
        else:
            parsed.append(
                ParsedGcRow(
                    line=line,
                    batch=batch,
                    analyte=analyte,
                    value=value,
                    tested_at=tested_at,
                )
            )

    if errors:
        raise GcImportValidationError(errors)
    return parsed


def _gc_data(row: ParsedGcRow) -> str:
    return json.dumps(
        {
            "source": "gc_csv",
            "line": row.line,
            "analyte": row.analyte,
            "unit": "%",
        },
        ensure_ascii=False,
    )
