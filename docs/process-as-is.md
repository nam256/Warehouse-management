# Quy trình nghiệp vụ As-Is (hiện trạng)

> Tổng hợp từ tài liệu nội bộ Oxeyns — chưa số hóa tích hợp.

---

## 1. Tổng quan

Quy trình sản xuất **t-Cinnamic Aldehyde (t-CA)** từ tinh dầu quế, ~6 nhân sự, ghi chép chủ yếu **giấy + Excel rời** giữa Kho, Kỹ thuật, Lab và ATTP.

---

## 2. Sơ đồ quy trình as-is

```mermaid
flowchart TD
    subgraph NCC["Nhà cung cấp"]
        A1[Giao tinh dầu quế]
    end

    subgraph KHO["Thủ kho"]
        A2[Tiếp nhận & kiểm sơ bộ]
        A3[Ghi BM-01/GMP01 giấy/Excel]
        A4[Bảo quản NVL nhiệt độ phòng]
        A5[Báo cáo tồn tuần/tháng]
    end

    subgraph LAB1["Lab / Lab ngoài"]
        B1[Lấy mẫu C14 - CCP1]
        B2[Kết quả email/file]
    end

    subgraph KT["Phòng Kỹ thuật"]
        C1[Yêu cầu xuất NVL]
        C2[Chưng cất chân không 32-37h]
        C3[Ghi BM-01/GMP03 T/P]
        C4[Chiết rót, bơm Nito]
        C5[Phối trộn, đóng phuy]
        C6[BM-01/GMP04 cân đối tay]
    end

    subgraph LAB2["Lab"]
        D1[GC % t-CA - CCP2]
        D2[BM-02/GMP05 Excel/giấy]
    end

    subgraph ATTP["Đội ATTP"]
        E1[Thẩm tra CCP 14 ngày/lần]
        E2[Thẩm tra nội bộ năm]
    end

    A1 --> A2 --> A3 --> B1
    B2 --> A4
    A4 --> C1 --> C2 --> C3 --> D1
    D2 --> C4 --> C5 --> C6
    A3 -.-> E1
    C3 -.-> E1
    D2 -.-> E1
    A5 --> E2
```

---

## 3. Điểm nghẽn chính

| # | Điểm | Mô tả |
|---|------|--------|
| 1 | Dữ liệu phân tán | BM-xx lưu giấy + Excel nhiều PC |
| 2 | CCP thủ công | Không cảnh báo tự động C14/Ttop/% t-CA |
| 3 | Truy xuất lô | Ghép chứng từ thủ công khi khách/ATTP hỏi |
| 4 | Độ trễ Lab | Kho/SX không thấy trạng thái pending tập trung |
| 5 | Báo cáo QL NM | Hợp nhất tồn + tiến độ mẻ thủ công |

---

## 4. Công cụ hiện tại

- Excel / Google Sheets (tồn kho)
- Giấy BM-xx/GMPxx
- Email / Zalo trao đổi kết quả Lab
- Sổ tay ATTP, QT-xx (PDF/in giấy)

Chi tiết: `docs/hien-trang-cntt.md`

---

## 5. CCP trên quy trình as-is

| CCP | Vị trí | Giới hạn | Hồ sơ |
|-----|--------|----------|-------|
| CCP1 | Sau nhập NVL | C14 13.02–14.39 | BM-01/GMP01 |
| CCP2 | Chưng cất | Ttop 107–110°C; % t-CA > 99 | BM-01/GMP03, BM-02/GMP05 |

---

*As-is mô tả trước triển khai prototype — so sánh với `docs/process-to-be.md`.*
