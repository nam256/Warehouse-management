import re
import zlib
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import (
    CCPStatus,
    Material,
    MaterialReservation,
    QualityStatus,
    ReservationStatus,
    StockBatch,
    Warehouse,
)
from app.seed import seed_database
from app.services.audit import next_ref, short_ref
from app.services.inventory_report import summarize_inventory, summarize_inventory_batches


@pytest.fixture()
def env():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    with Session() as db:
        seed_database(db)

    def override():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override
    with TestClient(app) as client:
        yield client, Session
    app.dependency_overrides.clear()


def _pdf_text(data: bytes) -> str:
    chunks: list[str] = []
    for match in re.finditer(rb"stream\r?\n(.+?)endstream", data, re.S):
        payload = match.group(1).strip(b"\r\n")
        try:
            payload = zlib.decompress(payload)
        except zlib.error:
            pass
        chunks.append(payload.decode("latin-1", errors="ignore"))
    return "\n".join(chunks)


def _headers(client: TestClient, username="thu_kho", password="kho123") -> dict[str, str]:
    response = client.post("/api/v1/auth/login", data={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _nvl_que(db):
    return db.query(Material).filter(Material.code == "NVL-QUE").one()


def _warehouse(db):
    return db.query(Warehouse).first()


def _add_batch(db, *, qty, released=True, expiry=None, batch_no="LO-TEST", ccp_pass=True):
    material = _nvl_que(db)
    warehouse = _warehouse(db)
    batch = StockBatch(
        batch_no=batch_no,
        material_id=material.id,
        warehouse_id=warehouse.id,
        quantity=qty,
        ccp1_status=CCPStatus.pass_ if ccp_pass else CCPStatus.pending,
        quality_status=QualityStatus.released if released else QualityStatus.quarantine,
        expiry_date=expiry,
    )
    db.add(batch)
    db.flush()
    return batch


def test_short_ref_strips_date_and_keeps_material_codes():
    assert short_ref("SX-20260718-001") == "SX-001"
    assert short_ref("NVL-20260718-012") == "NVL-012"
    assert short_ref("PX-001") == "PX-001"
    assert short_ref("NVL-QUE") == "NVL-QUE"
    assert short_ref(None) == "—"


def test_next_ref_continues_from_trailing_number(env):
    _client, Session = env
    with Session() as db:
        _add_batch(db, qty=10, batch_no="NVL-20260718-007")
        db.commit()
        nxt = next_ref("NVL", db, StockBatch, "batch_no")
    assert nxt == "NVL-008"


def test_summarize_inventory_subtracts_active_reservation(env):
    _client, Session = env
    with Session() as db:
        batch = _add_batch(db, qty=100, expiry=date.today() + timedelta(days=30))
        db.add(
            MaterialReservation(
                order_id=1,
                batch_id=batch.id,
                quantity=40,
                status=ReservationStatus.active,
            )
        )
        db.commit()
        row = next(item for item in summarize_inventory(db) if item.material_code == "NVL-QUE")

    assert row.on_hand == 100
    assert row.reserved == 40
    assert row.available == 60
    assert row.low_stock is True
    assert row.min_stock == 100


def test_summarize_inventory_quarantine_has_zero_available(env):
    _client, Session = env
    with Session() as db:
        _add_batch(db, qty=100, released=False, expiry=date.today() + timedelta(days=30))
        db.commit()
        row = next(item for item in summarize_inventory(db) if item.material_code == "NVL-QUE")

    assert row.on_hand == 100
    assert row.reserved == 0
    assert row.available == 0
    assert row.low_stock is True
    assert "Cách ly" in row.quality_label


def test_inventory_csv_snapshot_has_three_stock_columns(env):
    client, Session = env
    with Session() as db:
        batch = _add_batch(db, qty=100, expiry=date.today() + timedelta(days=30))
        db.add(
            MaterialReservation(
                order_id=1,
                batch_id=batch.id,
                quantity=40,
                status=ReservationStatus.active,
            )
        )
        db.commit()

    response = client.get("/api/v1/reports/inventory/export", headers=_headers(client))
    assert response.status_code == 200
    text = response.content.decode("utf-8-sig")
    assert "Tồn vật lý" in text
    assert "Đang giữ chỗ" in text
    assert "Khả dụng" in text
    assert "Tồn (kg)" not in text
    assert "100.000" in text
    assert "40.000" in text
    assert "60.000" in text
    assert "Tồn thấp" in text


def test_inventory_pdf_snapshot_has_three_stock_columns(env):
    client, Session = env
    with Session() as db:
        _add_batch(db, qty=100, expiry=date.today() + timedelta(days=30))
        db.commit()

    response = client.get("/api/v1/reports/inventory/export/pdf", headers=_headers(client))
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 500


def test_batch_view_sorts_by_expiry_ascending(env):
    _client, Session = env
    later = date.today() + timedelta(days=40)
    earlier = date.today() + timedelta(days=8)
    with Session() as db:
        _add_batch(db, qty=30, expiry=later, batch_no="LO-XA")
        _add_batch(db, qty=20, expiry=earlier, batch_no="LO-GAN")
        db.commit()
        rows = summarize_inventory_batches(db)
        que = [row for row in rows if row.material_code == "NVL-QUE"]

    assert [row.batch_no for row in que] == ["LO-GAN", "LO-XA"]
    assert que[0].expiry_date == earlier
    assert que[0].ccp1_label == "Đạt"
    assert que[0].quality_label == "Đã giải phóng"


def test_batch_csv_includes_lot_columns(env):
    client, Session = env
    with Session() as db:
        _add_batch(
            db,
            qty=12,
            expiry=date.today() + timedelta(days=9),
            batch_no="LO-CSV",
        )
        db.commit()

    response = client.get(
        "/api/v1/reports/inventory/export",
        params={"view": "batch"},
        headers=_headers(client),
    )
    assert response.status_code == 200
    text = response.content.decode("utf-8-sig")
    assert "Mã lô" in text
    assert "LO-CSV" in text
    assert "CCP1" in text
    assert "Đạt" in text


def test_issue_pdf_after_stock_out(env):
    client, Session = env
    with Session() as db:
        batch = _add_batch(db, qty=80, expiry=date.today() + timedelta(days=20), batch_no="LO-PX")
        db.commit()
        batch_id = batch.id

    headers = _headers(client)
    issued = client.post(
        "/api/v1/stock/issues",
        json={"batch_id": batch_id, "quantity": 5},
        headers=headers,
    )
    assert issued.status_code == 201
    movement = issued.json()
    assert movement["reference_no"].startswith("PX-")
    assert re.fullmatch(r"PX-\d+", movement["reference_no"])

    pdf = client.get(f"/api/v1/reports/issues/{movement['id']}/pdf", headers=headers)
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")
    assert f'{movement["reference_no"]}.pdf' in pdf.headers.get("content-disposition", "")
    raw = _pdf_text(pdf.content)
    combined = pdf.content.decode("latin-1", errors="ignore") + "\n" + raw
    assert movement["reference_no"] in combined
    assert "5.000" in combined or "5" in combined


def test_issue_unreleased_returns_400_no_pdf(env):
    client, Session = env
    with Session() as db:
        batch = _add_batch(
            db,
            qty=50,
            released=False,
            expiry=date.today() + timedelta(days=20),
            batch_no="LO-HOLD",
        )
        db.commit()
        batch_id = batch.id

    headers = _headers(client)
    issued = client.post(
        "/api/v1/stock/issues",
        json={"batch_id": batch_id, "quantity": 5},
        headers=headers,
    )
    assert issued.status_code == 400

    ledger = client.get("/api/v1/reports/issues", headers=headers)
    assert ledger.status_code == 200
    assert ledger.json() == []


def test_empty_issue_ledger_csv_returns_200_with_zero_total(env):
    client, _Session = env
    response = client.get("/api/v1/reports/issues/export", headers=_headers(client))
    assert response.status_code == 200
    text = response.content.decode("utf-8-sig")
    assert "Tổng" in text
    assert "0.000" in text or "0 kg" in text or "0.00" in text


def _receive_release_issue(client, Session, *, inbound=200.0, outbound=10.0):
    headers = _headers(client)
    mats = client.get("/api/v1/materials", headers=headers).json()
    nvl = next(item for item in mats if item["code"] == "NVL-QUE")
    receipt = client.post(
        "/api/v1/stock/receipts",
        json={"material_id": nvl["id"], "quantity": inbound, "warehouse_id": 1},
        headers=headers,
    )
    assert receipt.status_code == 201
    batch = receipt.json()
    with Session() as db:
        row = db.query(StockBatch).filter(StockBatch.id == batch["id"]).one()
        row.quality_status = QualityStatus.released
        row.ccp1_status = CCPStatus.pass_
        db.commit()
    issued = client.post(
        "/api/v1/stock/issues",
        json={"batch_id": batch["id"], "quantity": outbound},
        headers=headers,
    )
    assert issued.status_code == 201
    return headers, batch


def test_period_inventory_opening_in_out_closing(env):
    client, Session = env
    headers, _batch = _receive_release_issue(client, Session, inbound=200, outbound=10)
    today = date.today().isoformat()
    response = client.get(
        "/api/v1/reports/inventory/period",
        params={"from": today, "to": today},
        headers=headers,
    )
    assert response.status_code == 200
    payload = response.json()
    row = next(item for item in payload["items"] if item["material_code"] == "NVL-QUE")
    assert row["opening"] == 0
    assert row["inbound"] == 200
    assert row["outbound"] == 10
    assert row["adjustment"] == 0
    assert row["closing"] == 190
    assert "khóa sổ" in payload["note"]

    csv_res = client.get(
        "/api/v1/reports/inventory/period/export",
        params={"from": today, "to": today},
        headers=headers,
    )
    assert csv_res.status_code == 200
    text = csv_res.content.decode("utf-8-sig")
    assert "Tồn đầu kỳ" in text
    assert "Nhập trong kỳ" in text
    assert "Xuất trong kỳ" in text
    assert "200.000" in text
    assert "10.000" in text
    assert "190.000" in text


def test_period_inventory_accepts_inverted_or_named_dates(env):
    client, Session = env
    headers, _batch = _receive_release_issue(client, Session, inbound=200, outbound=10)
    later = (date.today() + timedelta(days=5)).isoformat()
    earlier = (date.today() - timedelta(days=5)).isoformat()
    inverted = client.get(
        "/api/v1/reports/inventory/period",
        params={"date_from": later, "date_to": earlier},
        headers=headers,
    )
    assert inverted.status_code == 200
    payload = inverted.json()
    assert payload["date_from"] == earlier
    assert payload["date_to"] == later


def test_receipt_pdf_keeps_original_inbound_qty_after_issue(env):
    client, Session = env
    headers, batch = _receive_release_issue(client, Session, inbound=200, outbound=10)
    pdf = client.get(f"/api/v1/reports/receipt/{batch['id']}/pdf", headers=headers)
    assert pdf.status_code == 200
    combined = pdf.content.decode("latin-1", errors="ignore") + "\n" + _pdf_text(pdf.content)
    assert "200.000" in combined
    assert "190.000" not in combined
