from sqlalchemy import inspect

from app.models import (
    BatchStatusHistory,
    MaterialReservation,
    QualityApproval,
    StockBatch,
)


def test_digital_qms_models_are_mapped():
    columns = {item.key for item in inspect(StockBatch).mapper.column_attrs}
    assert {"quality_status", "mfg_date", "expiry_date"} <= columns
    assert BatchStatusHistory.__tablename__ == "batch_status_histories"
    assert QualityApproval.__tablename__ == "quality_approvals"
    assert MaterialReservation.__tablename__ == "material_reservations"
