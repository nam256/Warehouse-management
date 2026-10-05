import type { ReactNode } from "react";

export type ActionBarProps = {
  children: ReactNode;
  align?: "start" | "end" | "between";
};

export default function ActionBar({ children, align = "end" }: ActionBarProps) {
  return <div className={`action-bar action-bar--${align}`}>{children}</div>;
}
