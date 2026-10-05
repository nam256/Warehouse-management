export type BadgeClass =
  | "badge-warn"
  | "badge-info"
  | "badge-accent"
  | "badge-ok"
  | "badge-danger"
  | "badge-neutral";

export type StatusMeta = {
  label: string;
  badgeClass: BadgeClass;
};

export const STATUS_MAP: Record<string, StatusMeta> = {
  quarantine: { label: "Chờ xử lý", badgeClass: "badge-warn" },
  open: { label: "Đang mở", badgeClass: "badge-warn" },
  sampling: { label: "Đang lấy mẫu", badgeClass: "badge-info" },
  under_test: { label: "Đang kiểm nghiệm", badgeClass: "badge-info" },
  investigating: { label: "Đang điều tra", badgeClass: "badge-info" },
  awaiting_release: { label: "Chờ phê duyệt", badgeClass: "badge-accent" },
  verification: { label: "Chờ xác minh", badgeClass: "badge-accent" },
  released: { label: "Đã giải phóng", badgeClass: "badge-ok" },
  closed: { label: "Đã đóng", badgeClass: "badge-ok" },
  pass: { label: "Đạt", badgeClass: "badge-ok" },
  rejected: { label: "Từ chối", badgeClass: "badge-danger" },
  fail: { label: "Không đạt", badgeClass: "badge-danger" },
  overdue: { label: "Quá hạn", badgeClass: "badge-danger" },
  retest: { label: "Kiểm nghiệm lại", badgeClass: "badge-neutral" },
  action_pending: { label: "Chờ hành động", badgeClass: "badge-neutral" },
  pending: { label: "Chờ xử lý", badgeClass: "badge-warn" },
  ordered: { label: "Đã đặt hàng", badgeClass: "badge-info" },
  fulfilled: { label: "Hoàn tất", badgeClass: "badge-ok" },
  draft: { label: "Bản nháp", badgeClass: "badge-neutral" },
  approved: { label: "Đã duyệt", badgeClass: "badge-accent" },
  running: { label: "Đang sản xuất", badgeClass: "badge-info" },
  done: { label: "Hoàn thành", badgeClass: "badge-ok" },
  cancelled: { label: "Đã hủy", badgeClass: "badge-danger" },
  active: { label: "Đang giữ chỗ", badgeClass: "badge-accent" },
  consumed: { label: "Đã xuất dùng", badgeClass: "badge-info" },
};

export function getStatusMeta(status: string): StatusMeta {
  return STATUS_MAP[status] ?? {
    label: status || "Chưa xác định",
    badgeClass: "badge-neutral",
  };
}
