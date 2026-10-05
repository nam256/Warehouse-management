/** Nhãn tiếng Việt — không viết tắt trên giao diện */

export const VAI_TRO: Record<string, string> = {
  admin: "Quản trị viên",
  thu_kho: "Thủ kho",
  ky_thuat: "Nhân viên kỹ thuật",
  lab: "Phòng kiểm nghiệm",
  attp: "Bộ phận an toàn thực phẩm",
  ql_nm: "Quản lý nhà máy",
};

export const LOAI_VAT_TU: Record<string, string> = {
  NVL: "Nguyên liệu",
  TP: "Thành phẩm",
  BTP: "Bán thành phẩm",
};

export const TRANG_THAI_ME: Record<string, string> = {
  draft: "Nháp",
  approved: "Đã duyệt",
  running: "Đang sản xuất",
  done: "Hoàn thành",
  cancelled: "Đã hủy",
};

export const KET_QUA_CCP: Record<string, string> = {
  pass: "Đạt",
  fail: "Không đạt",
  pending: "Chờ kiểm tra",
};

export const TRANG_THAI_YCMH: Record<string, string> = {
  pending: "Chờ xử lý",
  approved: "Đã duyệt",
  ordered: "Đã đặt hàng",
  cancelled: "Đã hủy",
};

export const HUONG_TRUY_XUAT: Record<string, string> = {
  NVL: "Nguyên liệu",
  TP: "Thành phẩm",
};

export const LOAI_KIEM_NGHIEM: Record<string, string> = {
  GC: "Sắc ký khí",
};

export const TEN_THUC_THE: Record<string, string> = {
  stock_batch: "Lô hàng kho",
  stock_movement: "Phiếu nhập xuất kho",
  production_order: "Mẻ sản xuất",
  lab_test: "Kết quả kiểm nghiệm",
  purchase_request: "Yêu cầu mua hàng",
  corrective_action: "Hành động khắc phục",
  material: "Vật tư",
  supplier: "Nhà cung cấp",
  user: "Tài khoản người dùng",
};

export const HANH_DONG_AUDIT: Record<string, string> = {
  RECEIPT: "Nhập kho",
  ISSUE: "Xuất kho",
  CREATE: "Tạo mới",
  UPDATE: "Cập nhật",
  APPROVE: "Duyệt",
  CANCEL: "Hủy",
  START: "Bắt đầu sản xuất",
  OPERATION: "Ghi điểm kiểm soát 2",
  COMPLETE: "Hoàn thành mẻ",
  MIXING: "Pha trộn",
  LAB_TEST: "Kiểm nghiệm",
  PURCHASE_REQ: "Yêu cầu mua hàng",
  CORRECTIVE: "Hành động khắc phục",
  LOCK: "Khóa tài khoản",
  UNLOCK: "Mở khóa tài khoản",
};

export function nhan(map: Record<string, string>, ma: string): string {
  return map[ma] ?? ma;
}
