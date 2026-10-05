import { useTheme } from "../theme-context";

type Props = {
  className?: string;
};

export default function ThemeToggle({ className = "" }: Props) {
  const { isDark, toggle } = useTheme();

  return (
    <button
      type="button"
      className={`theme-toggle ${className}`.trim()}
      onClick={toggle}
      aria-label={isDark ? "Chuyển sang giao diện sáng" : "Chuyển sang giao diện tối"}
      title={isDark ? "Giao diện sáng" : "Giao diện tối"}
    >
      <span aria-hidden="true">{isDark ? "☀" : "☾"}</span>
      <span className="theme-toggle__label">{isDark ? "Sáng" : "Tối"}</span>
    </button>
  );
}
