# Luồng dữ liệu (Data Flow)

> As-is vs To-be — mức logical data flow phục vụ Chương 4–5 báo cáo TTTN.

---

## 1. Luồng dữ liệu As-Is

```mermaid
flowchart LR
    subgraph Sources["Nguồn dữ liệu"]
        P1[Phiếu giấy BM-xx]
        P2[Excel tồn kho]
        P3[Email Lab / file GC]
        P4[Sổ vận hành xưởng]
    end

    subgraph Storage["Lưu trữ rời"]
        F1[PC Thủ kho]
        F2[PC Kỹ thuật]
        F3[PC Lab]
        F4[Tủ hồ sơ ATTP]
    end

    subgraph Consumers["Người dùng"]
        U1[QL NM]
        U2[ATTP thẩm tra]
        U3[Khách hàng COA]
    end

    P1 --> F1 & F2
    P2 --> F1
    P3 --> F3
    P4 --> F2
    F1 & F2 & F3 -->|Copy thủ công| U1
    F1 & F2 & F3 & F4 -->|Ghép hồ sơ| U2
    F3 -->|COA| U3
```

**Vấn đề:** Không có master data tập trung; batch ID không thống nhất giữa file.

---

## 2. Luồng dữ liệu To-Be (hệ thống đề xuất)

```mermaid
flowchart TB
    subgraph Client["React Frontend"]
        UI_KHO[UI Kho]
        UI_SX[UI Sản xuất]
        UI_LAB[UI Lab]
        UI_RPT[Dashboard / Báo cáo]
    end

    subgraph API["FastAPI Backend"]
        AUTH[JWT Auth / RBAC]
        S_KHO[Stock Service]
        S_SX[Production Service]
        S_QA[Quality / CCP Service]
        S_AUD[Audit Service]
        S_RPT[Report Service]
    end

    subgraph DB["PostgreSQL / SQLite"]
        T_MD[(Master: Product, Supplier)]
        T_BATCH[(Batch / Lot)]
        T_MOV[(StockMovement)]
        T_PO[(ProductionOrder)]
        T_OP[(OperationRecord)]
        T_QA[(QualityTest / CCP)]
        T_LOG[(AuditLog)]
    end

    UI_KHO --> AUTH --> S_KHO
    UI_SX --> S_SX
    UI_LAB --> S_QA
    UI_RPT --> S_RPT

    S_KHO --> T_MD & T_BATCH & T_MOV
    S_SX --> T_PO & T_OP
    S_SX --> S_KHO
    S_QA --> T_QA
    S_QA --> T_BATCH & T_PO
    S_KHO & S_SX & S_QA --> S_AUD --> T_LOG
    S_RPT --> T_MOV & T_PO & T_QA & T_LOG
```

---

## 3. Luồng batch traceability (chi tiết)

```mermaid
sequenceDiagram
    participant TK as Thủ kho
    participant API as API Kho
    participant LB as Lab
    participant QA as API CCP
    participant KT as Kỹ thuật
    participant SX as API SX

    TK->>API: POST nhập lô NVL (BM-01/GMP01)
    API->>API: Tạo batch_id, status=pending CCP1
    LB->>QA: POST GC C14
    QA->>API: Cập nhật CCP1 pass/fail
    KT->>SX: POST production order
    KT->>API: POST xuất NVL (link batch + PO)
    KT->>SX: POST operation steps (T, P, Ttop)
    LB->>QA: POST GC % t-CA
    QA->>SX: CCP2 pass → cho phép done
    SX->>API: Nhập kho TP (batch TP mới)
    Note over API,SX: Truy xuất: batch_TP → PO → batch_NVL[]
```

---

## 4. Bảng ánh xạ thực thể ↔ biểu mẫu

| Thực thể DB | Biểu mẫu | Module |
|-------------|----------|--------|
| StockMovement (in) | BM-01/GMP01 | Kho |
| Inventory snapshot | BM-02/GMP01 | Báo cáo |
| ProductionOrder + Step | BM-01/GMP03 | SX |
| ProductionMaterialUsage | BM-01/GMP04 | SX |
| MixingRecord (future) | BM-01/GMP05 | SX |
| QualityTest | BM-02/GMP05 | Lab |

Chi tiết ERD: `docs/database-design.md`

---

## 5. Luồng export / báo cáo

```mermaid
flowchart LR
    DB[(Database)] --> RPT[Report Service]
    RPT --> CSV[CSV tồn / truy xuất]
    RPT --> PDF[PDF BM-xx - planned]
    RPT --> DASH[Dashboard JSON]
    DASH --> UI[React charts]
```

---

## 6. Dữ liệu nhạy cảm & bảo mật

- JWT token — không lưu plaintext password
- Audit log append-only
- Phân quyền theo role — segregation Thủ kho vs Lab vs ATTP
- Backup DB — `docs/backup-rollback.md`
