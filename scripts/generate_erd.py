#!/usr/bin/env python3
"""Sinh sơ đồ ERD từ SQLAlchemy models (Mermaid + Graphviz DOT/PNG).

Chạy từ thư mục gốc dự án:
    python scripts/generate_erd.py

Đầu ra:
    docs/bao-cao/erd.mmd          — Mermaid (dán vào Word / VS Code / GitHub)
    docs/bao-cao/erd.dot           — Graphviz DOT
    docs/bao-cao/hinh-3-1-erd.png  — PNG (cần cài Graphviz: https://graphviz.org/download/)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
OUT_DIR = ROOT / "docs" / "bao-cao"

sys.path.insert(0, str(BACKEND))

from app.database import Base  # noqa: E402
from app import models  # noqa: E402, F401


def _col_label(col) -> str:
    parts = [col.name]
    if col.primary_key:
        parts.append("PK")
    if col.foreign_keys:
        parts.append("FK")
    return " ".join(parts)


TABLE_ORDER = [
    "users",
    "materials",
    "suppliers",
    "warehouses",
    "production_orders",
    "stock_batches",
    "stock_movements",
    "production_material_usages",
    "operation_records",
    "lab_tests",
    "mixing_reports",
    "purchase_requests",
    "audit_logs",
    "corrective_actions",
]


def _tables():
    meta = Base.metadata.tables
    for name in TABLE_ORDER:
        if name in meta:
            yield meta[name]
    for name, table in sorted(meta.items()):
        if name not in TABLE_ORDER:
            yield table


def generate_mermaid(max_cols: int = 6) -> str:
    lines = [
        "%% Hình 3.1 — Sơ đồ ERD tổng thể (14 bảng)",
        "%% Sinh tự động: python scripts/generate_erd.py",
        "erDiagram",
    ]

    for table in _tables():
        lines.append(f"    {table.name} {{")
        for col in list(table.columns)[:max_cols]:
            type_name = type(col.type).__name__.replace("VARCHAR", "string").lower()
            lines.append(f"        {type_name} {_col_label(col)}")
        if len(table.columns) > max_cols:
            lines.append("        string ...")
        lines.append("    }")

    seen: set[tuple[str, str, str]] = set()
    for table in _tables():
        for col in table.columns:
            for fk in col.foreign_keys:
                parent = fk.column.table.name
                child = table.name
                key = (parent, child, col.name)
                if key in seen:
                    continue
                seen.add(key)
                # Mermaid: parent ||--o{ child : label
                lines.append(f"    {parent} ||--o{{ {child} : {col.name}")

    return "\n".join(lines) + "\n"


def generate_dot() -> str:
    lines = [
        "digraph ERD {",
        '    graph [rankdir=LR, splines=ortho, fontname="Segoe UI"];',
        '    node [shape=record, fontname="Segoe UI", fontsize=10];',
        '    edge [fontname="Segoe UI", fontsize=9];',
        "",
    ]

    for table in _tables():
        cols = "|".join(_col_label(c) for c in table.columns)
        lines.append(f'    {table.name} [label="{{{table.name}|{cols}}}"];')

    lines.append("")
    for table in _tables():
        for col in table.columns:
            for fk in col.foreign_keys:
                parent = fk.column.table.name
                child = table.name
                lines.append(f'    {parent} -> {child} [label="{col.name}"];')

    # corrective_actions: quan hệ đa hình, không có FK cứng
    lines.extend(
        [
            "",
            '    corrective_actions_note [shape=note, label="corrective_actions\\nentity_type + entity_id\\n(polymorphic, no FK)"];',
            "}",
            "",
        ]
    )
    return "\n".join(lines)


def render_png(dot_path: Path, png_path: Path) -> bool:
    try:
        subprocess.run(
            ["dot", "-Tpng", str(dot_path), "-o", str(png_path)],
            check=True,
            capture_output=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"  [!] PNG skipped (install Graphviz): {exc}")
        return False


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    mmd = generate_mermaid()
    mmd_path = OUT_DIR / "erd.mmd"
    mmd_path.write_text(mmd, encoding="utf-8")
    print(f"  Mermaid : {mmd_path}")

    dot = generate_dot()
    dot_path = OUT_DIR / "erd.dot"
    dot_path.write_text(dot, encoding="utf-8")
    print(f"  DOT     : {dot_path}")

    png_path = OUT_DIR / "hinh-3-1-erd.png"
    if render_png(dot_path, png_path):
        print(f"  PNG     : {png_path}")

    fk_count = dot.count("->") - 1  # exclude note edge
    print(f"\n  {len(Base.metadata.tables)} tables, {fk_count} FK relations.")


if __name__ == "__main__":
    main()
