# Sơ đồ Chương 3 — Oxeyns Kho & SX

File Mermaid dùng cho báo cáo TTTN. Render tại [mermaid.live](https://mermaid.live) hoặc VS Code extension Mermaid.

| File | Hình | Nội dung |
|------|------|----------|
| `hinh-3-h-as-is-to-be.mmd` | 3.H | Quy trình as-is / to-be |
| `../erd.mmd` | 3.1 | ERD 14 bảng (đầy đủ) |
| `hinh-3-2-use-case.mmd` | 3.2 | Use case tổng quát |
| `hinh-3-2b-use-case-module.mmd` | 3.2b | Use case phân rã |
| `sequences.mmd` | 3.3–3.16 | 14 sơ đồ tuần tự |
| `hinh-3-17-state.mmd` | 3.17 | State machine mẻ SX |
| `hinh-3-18-architecture.mmd` | 3.18 | Kiến trúc 3 tầng |

**Sinh ERD từ code:**

```powershell
.\backend\.venv\Scripts\python.exe scripts\generate_erd.py
```

**Xuất PNG (Graphviz):** cài [Graphviz](https://graphviz.org/download/) rồi `dot -Tpng erd.dot -o hinh-3-1-erd.png`

Nội dung đã nhúng trong `docs/bao-cao/noi-dung/chuong-3.md`.
