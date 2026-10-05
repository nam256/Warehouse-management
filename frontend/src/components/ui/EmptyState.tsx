import type { ReactNode } from "react";

export type EmptyStateProps = {
  title: string;
  description?: string;
  action?: ReactNode;
};

export default function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <section className="empty-state" aria-live="polite">
      <div className="empty-state__icon" aria-hidden="true">
        —
      </div>
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      {action && <div>{action}</div>}
    </section>
  );
}
