# Quy trình nghiệp vụ To-Be (đề xuất)

> Hệ thống web **Oxeyns Kho & SX** — FastAPI + React, một nguồn dữ liệu tập trung.

---

## 1. Nguyên tắc to-be

1. **Số hóa BM-xx** — giữ quy trình GMP/HACCP, không đột ngột bỏ bước nghiệp vụ
2. **Batch traceability** — mọi phiếu gắn mã lô
3. **Rule CCP tự động** — pass/fail/pending + chặn release
4. **Audit log** — phục vụ FSSC thẩm tra
5. Triển khai **theo module**: Kho → SX → Lab → Báo cáo

---

## 2. Sơ đồ quy trình to-be

```mermaid
flowchart TD
    subgraph SYS["Hệ thống Oxeyns Kho & SX"]
        direction TB
        M1[Module 1 - Kho]
        M2[Module 2 - SX]
        M3[Module 3 - Lab & CCP]
        M4[Module 4 - Dashboard & Báo cáo]
    end

    subgraph USERS["Người dùng"]
        TK[Thủ kho]
        KT[Kỹ thuật]
        LB[Lab]
        QL[QL NM]
        AT[ATTP]
    end

    NCC[NCC giao hàng] --> TK
    TK -->|Phiếu nhập digital BM-01/GMP01| M1
    M1 -->|Tạo batch NVL pending CCP1| M3
    LB -->|Nhập GC C14| M3
    M3 -->|CCP1 pass| M1
    KT -->|Tạo mẻ SX + xuất NVL| M2
    M2 --> M1
    KT -->|Operation record BM-01/GMP03| M2
    LB -->|GC % t-CA BM-02/GMP05| M3
    M3 -->|CCP2 pass/fail| M2
    M2 -->|Hoàn thành mẻ + lô TP| M1
    M1 --> M4
    M2 --> M4
    M3 --> M4
    QL --> M4
    AT -->|Audit + CCP log| M4

    M4 --> OUT[Export CSV/PDF / Truy xuất lô]
```

---

## 3. Luồng trạng thái chính

### Lô NVL

```mermaid
stateDiagram-v2
    [*] --> PendingCCP1: Nhập kho
    PendingCCP1 --> Pass: C14 trong ngưỡng
    PendingCCP1 --> Fail: C14 ngoài ngưỡng
    Fail --> Isolated: Cô lập
    Pass --> Available: Cho xuất SX
    Available --> Consumed: Xuất hết cho mẻ
```

### Mẻ sản xuất

```mermaid
stateDiagram-v2
    [*] --> Draft: Tạo lệnh
    Draft --> Running: Bắt đầu mẻ
    Running --> PendingCCP2: Ghi Ttop / chờ Lab
    PendingCCP2 --> Done: CCP2 pass
    PendingCCP2 --> Blocked: CCP2 fail
    Running --> Cancelled: Hủy
```

---

## 4. Phân quyền to-be (RBAC)

| Role | Module chính |
|------|--------------|
| thu_kho | Nhập/xuất, tồn, YCMH |
| ky_thuat | Mẻ SX, operation record |
| lab | GC data, CCP |
| ql_nm | Dashboard, báo cáo |
| attp | CCP, audit, export |
| admin | Cấu hình, user |

---

## 5. Lộ trình triển khai

| Giai đoạn | Nội dung | Trạng thái demo |
|-----------|----------|-----------------|
| 1 | Kho + CCP1 + tồn | MVP ✅ |
| 2 | SX + operation + CCP2 | MVP ✅ |
| 3 | Lab GC + cảnh báo | MVP ✅ |
| 4 | Dashboard, truy xuất, audit | MVP ✅ |
| 5 | PDF BM-xx, mixing, duyệt lệnh | Mở rộng |

---

## 6. Lợi ích kỳ vọng

- Giảm thời gian lập báo cáo tồn/tuần
- Tra cứu truy xuất lô trong vài phút
- CCP fail được phát hiện sớm trên hệ thống
- Hồ sơ thẩm tra tập trung, có audit trail

---

*Chi tiết luồng dữ liệu: `docs/data-flow.md`*
