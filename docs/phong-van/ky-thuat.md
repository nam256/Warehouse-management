# Tóm tắt phỏng vấn — Phòng Kỹ thuật

> **Nguồn:** Tổng hợp synthesized từ `quytrinhsanxuat.txt`, `chuongtrinhthamtra.txt`, `detai.txt`.  
> **Không phải biên bản phỏng vấn trực tiếp.**

---

## Thông tin buổi phỏng vấn (mô phỏng)

| Mục | Nội dung |
|-----|----------|
| Đối tượng | Phòng Kỹ thuật — vận hành chưng cất, chiết rót, phối trộn |
| Thời lượng | ~50 phút |
| Mục tiêu | Operation record, thông số T/P, CCP2, liên kết kho |

---

## 1. Quy trình vận hành (t-CA)

1. Nhận NVL đã qua CCP1 từ kho
2. **Chưng cất chân không:** T 108–115°C (gia nhiệt 130–150°C), P (-0.99)–(-0.10) MPa, **32–37 h/mẻ**
3. Theo dõi **Ttop (TI103): 107–110°C** — quyết định thu TP/BTP
4. Chiết rót, **bơm Nito** (10 bar / 2 phút), lấy mẫu
5. Phối trộn (khuấy + Nito ~2h), đóng phuy, dán nhãn

**Nhánh BTP:** bán thành phẩm → chưng cất lại → TP thô **% t-CA > 99%**

---

## 2. Ghi chép hiện tại

| Biểu mẫu | Nội dung |
|----------|----------|
| BM-01/GMP03 | Operation Record — từng công đoạn, T, P, thời gian |
| BM-01/GMP04 | Material balance — đầu vào/đầu ra/hao hụt theo mẻ |
| BM-01/GMP05 | Mixing report (phối trộn) |

Ghi **giấy tại xưởng**, cuối ca hoặc cuối mẻ nhập lại Excel (nếu có). Dữ liệu T/P đọc từ **thiết bị đo** (QT-KSTB).

---

## 3. CCP2 — Chưng cất

| Thông số | Giới hạn | Ai ghi |
|----------|----------|--------|
| Ttop (TI103) | 107–110°C | Kỹ thuật (realtime) |
| % t-CA | > 99% | Lab (GC) |

Khi vượt ngưỡng: dừng, lấy mẫu khảo sát, báo QL NM và ATTP — **chưa có popup/cảnh báo tự động** trên hệ thống số.

---

## 4. Pain point

1. Operation record **tách rời** GC data — khó đối chiếu một mẻ trên một màn hình
2. **Material balance** tính tay, dễ sai khi hao hụt chưng cất lớn
3. Không link trực tiếp **phiếu xuất kho** với mẻ SX — đối chiếu batch thủ công
4. Báo cáo mẻ theo thời gian thực **không có** — QL NM hỏi tiến độ qua Zalo/điện thoại

---

## 5. Kỳ vọng hệ thống

- Tạo **Production Order** (mẻ SX) với mã batch SX
- Ghi **operation record điện tử** theo bước: chưng cất, chiết rót, phối trộn…
- Tự động lấy SL NVL từ module Kho khi xuất cho mẻ
- Validate CCP2 tại nhập liệu; **chặn hoàn thành mẻ** nếu fail
- Xuất BM-01/GMP03/GMP04 (PDF/Excel) phục vụ thẩm tra

---

## 6. Trích dẫn (paraphrase synthesized)

> “Em ghi T và P trên sổ trong suốt 36 giờ mẻ. Lab gửi % t-CA qua email chiều hôm sau. Khi thẩm tra, anh HACCP phải ghép giấy em với GC của Lab — mất nửa buổi.”

---

*Cập nhật sau phỏng vấn thực tế với tên nhân sự Kỹ thuật và ảnh operation record mẫu.*
