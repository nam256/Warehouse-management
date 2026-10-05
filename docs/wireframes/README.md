# Wireframes — Oxeyns Kho & SX (ASCII)

> Sketch mức low-fidelity phục vụ báo cáo TTTN. UI thực tế: React (`frontend/src/pages/`).

---

## 1. Đăng nhập (`/login`)

```text
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              ┌─────────────────────────────┐                │
│              │     OXEYNS — Kho & SX       │                │
│              │     Đăng nhập hệ thống      │                │
│              ├─────────────────────────────┤                │
│              │ Tài khoản                   │                │
│              │ [________________________]  │                │
│              │ Mật khẩu                    │                │
│              │ [________________________]  │                │
│              │                             │                │
│              │      [ Đăng nhập ]          │                │
│              │                             │                │
│              │ Demo: thu_kho / kho123      │                │
│              └─────────────────────────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Dashboard (`/`)

```text
┌──────────┬──────────────────────────────────────────────────┐
│ SIDEBAR  │  Dashboard                          [User ▼]    │
│          ├──────────────────────────────────────────────────┤
│ Dashboard│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│ Tồn kho  │  │ NVL tồn │ │ Mẻ chạy │ │ CCP fail│ │ Tồn thấp││
│ Nhập kho │  │  1,250  │ │    1    │ │    0    │ │    2    ││
│ Xuất kho │  └─────────┘ └─────────┘ └─────────┘ └─────────┘│
│ Sản xuất │                                                  │
│ Lab      │  Cảnh báo gần đây                                │
│ Truy xuất│  ┌────────────────────────────────────────────┐│
│ YCMH     │  │ • NL-QUE tồn < min — tạo YCMH              ││
│ CCP      │  │ • Lô LOT-20260615 pending CCP1             ││
│ Audit    │  └────────────────────────────────────────────┘│
│ Báo cáo  │                                                  │
│          │  Mẻ SX trong kỳ        │  CCP pass/fail/pending  │
│ [Logout] │  [==== biểu đồ ====]   │  [==== biểu đồ =====]   │
└──────────┴──────────────────────────────────────────────────┘
```

---

## 3. Nhập kho (`/stock-in`) — BM-01/GMP01

```text
┌──────────┬──────────────────────────────────────────────────┐
│ SIDEBAR  │  Phiếu nhập nguyên liệu                          │
│          ├──────────────────────────────────────────────────┤
│          │  NCC [▼ Chọn NCC    ]  NVL [▼ Tinh dầu quế     ] │
│          │  Mã lô NCC [________]  SL [____] KL [____] kg   │
│          │  Kiểm sơ bộ: Màu [Đạt▼] Mùi [Đạt▼] Tỷ trọng [] │
│          │                                                  │
│          │  ── CCP1 ──                                      │
│          │  C14 [________] dpm/gC   Trạng thái: (pending)  │
│          │                                                  │
│          │  [ Hủy ]                    [ Lưu phiếu nhập ]  │
│          │                                                  │
│          │  Phiếu gần đây                                   │
│          │  ┌──────┬────────┬──────┬────────┬──────────┐   │
│          │  │ Số PN│ Ngày   │ Lô   │ SL   │ CCP1     │   │
│          │  ├──────┼────────┼──────┼──────┼──────────┤   │
│          │  │ PN-01│20/06/26│ L-001│ 500  │ pass     │   │
│          │  └──────┴────────┴──────┴──────┴──────────┘   │
└──────────┴──────────────────────────────────────────────────┘
```

---

## 4. Sản xuất (`/production`) — BM-01/GMP03

```text
┌──────────┬──────────────────────────────────────────────────┐
│ SIDEBAR  │  Quản lý mẻ sản xuất                             │
│          ├──────────────────────────────────────────────────┤
│          │  [ + Tạo mẻ mới ]                                │
│          │                                                  │
│          │  Danh sách mẻ                                   │
│          │  ┌────────┬────────┬──────┬────────┬─────────┐  │
│          │  │ Mã PO  │ Batch  │ SP   │ Trạng th│ CCP2   │  │
│          │  ├────────┼────────┼──────┼────────┼─────────┤  │
│          │  │PO-0620 │ SX-001 │ t-CA │ running│ pending │  │
│          │  └────────┴────────┴──────┴────────┴─────────┘  │
│          │                                                  │
│          │  ── Operation Record (mẻ PO-0620) ──            │
│          │  Công đoạn [Chưng cất ▼]  T [108]  P [-0.5]     │
│          │  Ttop [109] °C  (CCP2: 107-110)                 │
│          │  [ + Thêm bước ]  [ Hoàn thành mẻ ]             │
└──────────┴──────────────────────────────────────────────────┘
```

---

## 5. Các màn hình khác (tham chiếu)

| Route | Mô tả ngắn |
|-------|------------|
| `/inventory` | Bảng tồn theo mã hàng/lô, export CSV |
| `/stock-out` | Xuất NVL cho mẻ SX |
| `/lab` | Nhập GC — BM-02/GMP05 |
| `/trace` | Tra cứu 2 chiều lô |
| `/reports` | Báo cáo, export |

---

## 6. Ghi chú thiết kế

- Sidebar cố định trái — pattern admin dashboard
- Form label **tiếng Việt** (NFR-001)
- Trạng thái CCP màu: pass (xanh), fail (đỏ), pending (vàng)
- Responsive: MVP ưu tiên desktop 1280px+ (vận hành tại văn phòng/xưởng)

---

*Screenshot thực tế đặt tại `docs/screenshots/` khi chụp demo.*
