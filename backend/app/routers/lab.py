from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.database import get_db
from app.models import CCPStatus, LabTest, ProductionOrder, StockBatch, User, UserRole
from app.schemas import (
    GcImportResultOut,
    LabTestCreate,
    LabTestOut,
    SpcPointOut,
    SpcResultOut,
)
from app.services.audit import log_action
from app.services.capa import create_capa_for_failure
from app.services.ccp import evaluate_ccp1, evaluate_ccp2
from app.services.gc_import import (
    MAX_FILE_SIZE,
    GcImportValidationError,
    import_gc_csv,
)
from app.services.spc import calculate_spc

router = APIRouter(prefix="/lab", tags=["lab"])
GC_MIME_TYPES = {"text/csv", "application/vnd.ms-excel"}


@router.get("/tests", response_model=list[LabTestOut])
def list_tests(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    tests = db.query(LabTest).order_by(LabTest.created_at.desc()).limit(100).all()
    return [
        LabTestOut(
            id=t.id,
            order_id=t.order_id,
            batch_id=t.batch_id,
            test_type=t.test_type,
            gc_data=t.gc_data,
            c14=float(t.c14) if t.c14 else None,
            t_ca_percent=float(t.t_ca_percent) if t.t_ca_percent else None,
            result_status=t.result_status,
            created_at=t.created_at.isoformat(),
        )
        for t in tests
    ]


@router.post("/gc-import", response_model=GcImportResultOut)
async def gc_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.lab, UserRole.admin)),
):
    if file.content_type not in GC_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Chỉ chấp nhận tệp CSV (text/csv hoặc application/vnd.ms-excel).",
        )
    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Tệp CSV không được vượt quá 1 MB.")

    try:
        result = import_gc_csv(
            db,
            content=content,
            filename=file.filename or "gc.csv",
            imported_by_id=user.id,
        )
        if not result.duplicate:
            log_action(
                db,
                user,
                "GC_IMPORT",
                "gc_import",
                result.sha256,
                f"Nhập {result.imported} kết quả GC từ {file.filename or 'gc.csv'}",
            )
            db.commit()
        return GcImportResultOut(
            imported=result.imported,
            duplicate=result.duplicate,
            sha256=result.sha256,
            row_count=result.row_count,
        )
    except GcImportValidationError as exc:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Tệp CSV không hợp lệ.",
                "imported": 0,
                "errors": exc.errors,
            },
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Không thể lưu dữ liệu GC. Vui lòng thử lại.",
        ) from exc


@router.get("/spc", response_model=SpcResultOut)
def get_spc(
    analyte: str = Query(...),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(UserRole.lab, UserRole.attp, UserRole.ql_nm, UserRole.admin)
    ),
):
    if analyte not in {"C14", "tCA"}:
        raise HTTPException(status_code=422, detail="analyte chỉ nhận C14 hoặc tCA.")
    if not 10 <= limit <= 1000:
        raise HTTPException(status_code=422, detail="limit phải từ 10 đến 1.000.")

    value_column = LabTest.c14 if analyte == "C14" else LabTest.t_ca_percent
    records = (
        db.query(LabTest, StockBatch.batch_no)
        .outerjoin(StockBatch, StockBatch.id == LabTest.batch_id)
        .filter(value_column.isnot(None))
        .order_by(LabTest.created_at.desc(), LabTest.id.desc())
        .limit(limit)
        .all()
    )
    records.reverse()
    values = [
        float(test.c14 if analyte == "C14" else test.t_ca_percent)
        for test, _ in records
    ]
    result = calculate_spc(values)
    points = [
        SpcPointOut(
            value=point.value,
            tested_at=test.created_at,
            batch_no=batch_no or "—",
            out_of_control=point.out_of_control,
        )
        for point, (test, batch_no) in zip(result.points, records)
    ]
    return SpcResultOut(
        analyte=analyte,
        status=result.status,
        mean=result.mean,
        std_dev=result.std_dev,
        ucl=result.ucl,
        lcl=result.lcl,
        points=points,
    )


@router.post("/tests", response_model=LabTestOut, status_code=201)
def create_test(
    data: LabTestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.lab, UserRole.attp)),
):
    if not data.order_id and not data.batch_id:
        raise HTTPException(status_code=400, detail="Cần order_id hoặc batch_id")

    if data.order_id:
        order = db.query(ProductionOrder).filter(ProductionOrder.id == data.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Không tìm thấy mẻ SX")

    batch = None
    if data.batch_id:
        batch = db.query(StockBatch).filter(StockBatch.id == data.batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Không tìm thấy lô")

    if data.c14 is not None:
        status = CCPStatus(evaluate_ccp1(data.c14))
    elif data.t_ca_percent is not None:
        status = CCPStatus(evaluate_ccp2(None, data.t_ca_percent))
    else:
        status = CCPStatus.pending

    test = LabTest(
        order_id=data.order_id,
        batch_id=data.batch_id,
        test_type=data.test_type,
        gc_data=data.gc_data,
        c14=data.c14,
        t_ca_percent=data.t_ca_percent,
        result_status=status,
        created_by_id=user.id,
    )
    db.add(test)

    if batch and data.c14 is not None:
        batch.ccp1_c14 = data.c14
        batch.ccp1_status = status

    db.flush()
    if status == CCPStatus.fail:
        create_capa_for_failure(
            db,
            "lab_test",
            test.id,
            created_by_id=user.id,
        )
    ref_code = batch.batch_no if batch else None
    if not ref_code and data.order_id:
        order = db.query(ProductionOrder).filter(ProductionOrder.id == data.order_id).first()
        if order:
            ref_code = order.order_no
    desc_parts = []
    if batch:
        desc_parts.append(f"lô {batch.batch_no}")
    if data.order_id:
        order = db.query(ProductionOrder).filter(ProductionOrder.id == data.order_id).first()
        if order:
            desc_parts.append(f"mẻ {order.order_no}")
    test_label = {"GC": "Sắc ký khí", "C14": "Hàm lượng C14"}.get(data.test_type, data.test_type)
    log_action(
        db,
        user,
        "LAB_TEST",
        "lab_test",
        ref_code or str(test.id),
        test_label + (" — " + ", ".join(desc_parts) if desc_parts else ""),
    )
    db.commit()
    db.refresh(test)
    return LabTestOut(
        id=test.id,
        order_id=test.order_id,
        batch_id=test.batch_id,
        test_type=test.test_type,
        gc_data=test.gc_data,
        c14=float(test.c14) if test.c14 else None,
        t_ca_percent=float(test.t_ca_percent) if test.t_ca_percent else None,
        result_status=test.result_status,
        created_at=test.created_at.isoformat(),
    )
