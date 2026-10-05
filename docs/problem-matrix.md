# Ma trận vấn đề — Impact × Effort

> Phục vụ ưu tiên hóa giải pháp MVP cho Oxeyns Long An (quy mô ~6 NS).

**Thang điểm:** 1 (thấp) – 5 (cao)

---

## 1. Ma trận theo phòng ban

| ID | Vấn đề | Phòng | Impact | Effort số hóa | Ưu tiên |
|----|--------|-------|--------|---------------|---------|
| P01 | Tồn kho cập nhật thủ công, dễ lệch | Kho | 5 | 3 | **P0** |
| P02 | Khó truy xuất lô NVL→SX→TP | Kho/ATTP | 5 | 3 | **P0** |
| P03 | Phiếu nhập/xuất không link mẻ SX | Kho/SX | 4 | 2 | **P0** |
| P04 | Operation record giấy, tách rời GC | Kỹ thuật | 4 | 3 | **P1** |
| P05 | Material balance tính tay | Kỹ thuật | 3 | 2 | **P1** |
| P06 | Không cảnh báo CCP tự động | Lab/ATTP | 5 | 2 | **P0** |
| P07 | Hồ sơ thẩm tra CCP phân tán | ATTP | 4 | 3 | **P1** |
| P08 | QL NM thiếu dashboard tổng hợp | QL NM | 4 | 2 | **P1** |
| P09 | Độ trễ kết quả Lab không visible | Lab/Kho | 3 | 2 | **P1** |
| P10 | Export BM-xx PDF đúng mẫu | ATTP | 3 | 4 | **P2** |
| P11 | Workflow duyệt lệnh SX nhiều cấp | QL NM | 2 | 3 | **P2** |
| P12 | Tích hợp file GC tự động | Lab | 3 | 5 | **P3** |

---

## 2. Biểu đồ Impact × Effort

```text
Impact
  5 │ P01 P02 P06          │ Quick wins (P0)
    │                        │
  4 │ P03 P04 P07 P08       │ Kế hoạch MVP (P1)
    │                        │
  3 │ P05 P09 P10           │ Giai đoạn 2 (P2)
    │                        │
  2 │ P11                   │
    │                        │
  1 │                        │ P12 (effort cao)
    └────────────────────────┴────────────────── Effort
      1    2    3    4    5
```

**Quick wins (Impact cao, Effort thấp-vừa):** P01, P02, P03, P06 → đã đưa vào MVP prototype.

---

## 3. Ma trận giải pháp ↔ module

| Vấn đề | Giải pháp đề xuất | Module | FR |
|--------|-------------------|--------|-----|
| P01 | Tồn realtime, movements | Kho | FR-006 |
| P02 | Batch traceability 2 chiều | Kho/SX | FR-013 |
| P03 | Xuất kho link ProductionOrder | Kho/SX | FR-005, FR-007 |
| P04 | Operation record digital | SX | FR-008 |
| P06 | Rule CCP1/CCP2 + chặn release | Lab/CCP | FR-010 |
| P08 | Dashboard | Báo cáo | FR-011 |
| P07 | Audit log + màn CCP/HACCP | Hệ thống | FR-012 |

---

## 4. Rủi ro nếu không xử lý

| Vấn đề | Rủi ro |
|--------|--------|
| P02 | Không đáp ứng kịp truy xuất FSSC / TT-TVTH |
| P06 | CCP fail phát hiện muộn → lô không an toàn |
| P01 | Dừng SX vì thiếu NVL không báo trước |
| P07 | Thẩm tra 14 ngày tốn thời gian, thiếu sót hồ sơ |

---

## 5. Kết luận ưu tiên MVP

1. **Module Kho + CCP1** (P01, P02, P03)  
2. **CCP rule + Lab** (P06, P09)  
3. **SX + operation** (P04)  
4. **Dashboard + audit** (P07, P08)  
5. Material balance đầy đủ, PDF BM, mixing (P05, P10) — giai đoạn 2  

---

*Nguồn pain point: `docs/phong-van/` (synthesized).*
