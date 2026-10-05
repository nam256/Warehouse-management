# Chương 3 — Khảo sát thực trạng tại Oxeyns

---

## 3.1. Giới thiệu công ty

| Mục | Nội dung |
|-----|----------|
| Tên | Công ty TNHH Oxeyns – Chi nhánh Long An |
| Địa điểm | KCN Tân Kim, Cần Giuộc, Long An |
| Lĩnh vực | Hương liệu thiên nhiên, tinh dầu |
| Sản phẩm chính | t-Cinnamic Aldehyde (t-CA) từ dầu quế |
| Quy mô | ~6 NS, nhà xưởng 250 m², ~36 tấn/năm |
| Tiêu chuẩn | FSSC 22000, HACCP, Kosher |

---

## 3.2. Tổ chức và vai trò (`tochuc.txt`)

| Bộ phận | Vai trò chính |
|---------|---------------|
| Thủ kho | Nhập/xuất/tồn NVL, báo cáo tuần |
| Phòng Kỹ thuật | Vận hành chưng cất, chiết rót, phối trộn |
| Phòng Lab | GC, C14, % t-CA |
| QL nhà máy | Điều phối, báo cáo |
| Đội ATTP/FSSC | HACCP, thẩm tra, hồ sơ CL |

---

## 3.3. Quy trình sản xuất t-CA

Theo `quytrinhsanxuat.txt` và HACCP:

```text
Tiếp nhận dầu quế → Bảo quản → Chưng cất chân không (32–37h)
→ Chiết rót, bơm Nito → Phối trộn → Đóng phuy, dán nhãn
```

**Thông số:** T 108–115°C, P (-0.99)–(-0.10) MPa; Ttop CCP2: 107–110°C.

**Nhánh BTP:** chưng cất lại → TP thô % t-CA > 99%.

---

## 3.4. Hệ thống ATTP/HACCP

- Sổ tay ATTP, QT-xx, SSOP
- Chương trình thẩm tra: CCP 14 ngày/lần; thẩm tra nội bộ năm
- CCP1: C14 13.02–14.39 dpm/gC; CCP2: Ttop + % t-CA

Chi tiết: `chuongtrinhthamtra.txt`

---

## 3.5. Hiện trạng CNTT

Xem `docs/hien-trang-cntt.md`:

- Excel/Google Sheets tồn kho
- Giấy BM-xx + file rời trên PC từng phòng
- Chưa ERP/MES tích hợp
- GC: file/email — nhập tay

---

## 3.6. Kết quả khảo sát phỏng vấn (synthesized)

| Đối tượng | File tóm tắt | Pain point chính |
|-----------|--------------|------------------|
| Thủ kho | `docs/phong-van/thu-kho.md` | Tồn thủ công, truy xuất lô |
| Kỹ thuật | `docs/phong-van/ky-thuat.md` | Operation tách GC |
| Lab | `docs/phong-van/lab.md` | Độ trễ C14, không link batch |
| QL NM | `docs/phong-van/ql-nm.md` | Thiếu dashboard |
| ATTP | `docs/phong-van/attp.md` | Hồ sơ CCP phân tán |

> **Ghi chú methodology:** Nội dung tổng hợp từ tài liệu nội bộ; cần bổ sung biên bản phỏng vấn trực tiếp khi triển khai tại NM.

---

## 3.7. Biểu mẫu đang sử dụng

| Mã | Mục đích |
|----|----------|
| BM-01/GMP01 | Phiếu nhập NVL |
| BM-02/GMP01 | Tồn tháng |
| BM-01/GMP03 | Operation record |
| BM-01/GMP04 | Material balance |
| BM-01/GMP05 | Mixing |
| BM-02/GMP05 | GC data |

Mô tả số hóa: `docs/bieu-mau/`

---

## 3.8. Quan sát hiện trường (kế hoạch)

- [ ] 1 mẻ chưng cất (32h+ — có thể quan sát một phần ca)
- [ ] 1 lần nhập kho dầu quế
- Ghi nhận ảnh/quy trình thực tế bổ sung vào phụ lục

---

## 3.9. Tổng kết chương

- Oxeyns có quy trình ATTP chặt nhưng **CNTT phân tán**
- Dữ liệu CCP và batch nằm rải rác → cơ sở đề xuất hệ thống tích hợp Chương 5
