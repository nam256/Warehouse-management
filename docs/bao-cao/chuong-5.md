# Chương 5 — Đề xuất giải pháp

---

## 5.1. Nguyên tắc thiết kế

1. Số hóa BM-xx — **không đổi đột ngột** quy trình GMP
2. Batch-centric — mọi phiếu gắn mã lô
3. CCP rule trên server — không chỉ UI
4. Audit trail đầy đủ
5. Triển khai từng module: **Kho trước**

---

## 5.2. Kiến trúc hệ thống

```text
[React SPA] ←HTTP/JWT→ [FastAPI] ←→ [PostgreSQL]
                              ↓
                        Audit / CCP services
```

- Client-server, REST API
- OpenAPI: `/docs`
- Chi tiết: `README.md`, `docs/data-flow.md`

---

## 5.3. Mô tả 4 module

### Module 1 — Quản lý kho

- Nhập/xuất/tồn NVL, BTP, TP theo lô
- BM-01/GMP01 digital, CCP1
- Cảnh báo tồn thấp, YCMH
- Truy xuất batch

### Module 2 — Quản lý sản xuất

- Production order, trạng thái mẻ
- Operation record (BM-01/GMP03), T/P/Ttop
- Link xuất kho; material balance (BM-01/GMP04)

### Module 3 — Lab & CCP

- GC data (BM-02/GMP05)
- Rule CCP1/CCP2; chặn release
- Log phục vụ thẩm tra HACCP

### Module 4 — Báo cáo & ATTP

- Dashboard tồn, SX, CCP
- Export CSV; audit viewer
- Tra cứu truy xuất 2 chiều

---

## 5.4. Thiết kế dữ liệu

- ERD: Product, Material, Batch, StockMovement, ProductionOrder, OperationRecord, QualityTest, AuditLog
- Quy tắc mã lô/phiếu: `docs/database-design.md`
- Traceability: NVL batch → PO → TP batch

---

## 5.5. Thiết kế API & phân quyền

- Draft endpoint: `docs/api-spec.md`
- Roles: admin, thu_kho, ky_thuat, lab, ql_nm, attp
- JWT + middleware audit

---

## 5.6. Luồng to-be

- Sơ đồ: `docs/process-to-be.md`
- State machine lô NVL và mẻ SX
- Sequence traceability: `docs/data-flow.md`

---

## 5.7. Wireframe giao diện

- ASCII sketch: `docs/wireframes/README.md`
- Màn hình: login, dashboard, nhập kho, sản xuất
- i18n tiếng Việt

---

## 5.8. Map biểu mẫu ↔ hệ thống

| BM | Chức năng |
|----|-----------|
| BM-01/GMP01 | `/stock-in` |
| BM-02/GMP01 | Reports inventory |
| BM-01/GMP03 | `/production` |
| BM-02/GMP05 | `/lab` |

Chi tiết field: `docs/bieu-mau/`

---

## 5.9. Lộ trình triển khai

| Giai đoạn | Thời gian (ước) | Deliverable |
|-----------|-----------------|-------------|
| 1 | Tuần 1–4 | Kho + auth + CCP1 |
| 2 | Tuần 5–8 | SX + CCP2 |
| 3 | Tuần 9–10 | Lab + dashboard |
| 4 | Tuần 11–12 | UAT, tài liệu, demo |
| 5 | Sau TTTN | PDF, mixing, go-live |

---

## 5.10. Lợi ích và rủi ro

### Lợi ích

- Giảm thời gian báo cáo tồn/tuần
- Truy xuất nhanh; CCP sớm
- Hồ sơ thẩm tra tập trung

### Rủi ro & giảm thiểu

| Rủi ro | Giảm thiểu |
|--------|-------------|
| Người dùng không adopt | Đào tạo 45p; giữ form quen thuộc |
| Lỗi phần mềm CCP | Validation 8.7; song song giấy |
| Quá tải IT | Phased rollout; dev chính + SV IT |

---

## 5.11. Tổng kết chương

- Giải pháp web 4 module khả thi cho Oxeyns
- Prototype minh họa Chương 6
