import type { ReactNode } from "react";

export type FilterBarProps = {
  children: ReactNode;
  ariaLabel?: string;
};

export default function FilterBar({ children, ariaLabel = "Bộ lọc dữ liệu" }: FilterBarProps) {
  return (
    <section className="filter-bar" aria-label={ariaLabel}>
      {children}
    </section>
  );
}
