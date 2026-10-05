"""Đưa database về trạng thái ban đầu (chỉ master data, chưa sử dụng).

Chạy: py reset_db.py
"""

from sqlalchemy import inspect, text

from app.database import SessionLocal, engine
from app.seed import MASTER_MATERIAL_CODES, reset_database


def main() -> None:
    db = SessionLocal()
    try:
        reset_database(db)
    finally:
        db.close()

    insp = inspect(engine)
    db = SessionLocal()
    try:
        print("Đã reset DB về trạng thái ban đầu.\n")
        for name in sorted(insp.get_table_names()):
            if name == "alembic_version":
                continue
            count = db.execute(text(f'SELECT COUNT(*) FROM "{name}"')).scalar()
            print(f"  {name}: {count}")
        materials = db.execute(text('SELECT code, name FROM materials ORDER BY code')).fetchall()
        print("\nVật tư master:")
        for code, name in materials:
            flag = "OK" if code in MASTER_MATERIAL_CODES else "???"
            print(f"  [{flag}] {code} — {name}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
