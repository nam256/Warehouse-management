import type { ReactNode } from "react";

export type AlertTone = "danger" | "warning" | "success" | "info";

export type AlertBannerProps = {
  tone?: AlertTone;
  title?: string;
  children: ReactNode;
  onClose?: () => void;
};

export default function AlertBanner({
  tone = "info",
  title,
  children,
  onClose,
}: AlertBannerProps) {
  return (
    <div className={`alert-banner alert-banner--${tone}`} role={tone === "danger" ? "alert" : "status"}>
      <div className="alert-banner__content">
        {title && <strong>{title}</strong>}
        <div>{children}</div>
      </div>
      {onClose && (
        <button type="button" className="alert-banner__close" onClick={onClose} aria-label="Đóng thông báo">
          ×
        </button>
      )}
    </div>
  );
}
