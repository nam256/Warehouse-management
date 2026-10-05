import { getStatusMeta } from "../../ui/status";

export type StatusBadgeProps = {
  status: string;
  label?: string;
};

export default function StatusBadge({ status, label }: StatusBadgeProps) {
  const meta = getStatusMeta(status);
  return <span className={`status-badge ${meta.badgeClass}`}>{label ?? meta.label}</span>;
}
