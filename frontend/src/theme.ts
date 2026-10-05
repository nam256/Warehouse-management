export type Theme = "light" | "dark";

export const THEME_STORAGE_KEY = "oxeyns-theme";

export function getStoredTheme(): Theme {
  try {
    const value = localStorage.getItem(THEME_STORAGE_KEY);
    if (value === "dark" || value === "light") return value;
  } catch {
    /* private mode */
  }
  return "light";
}

export function applyTheme(theme: Theme): void {
  document.documentElement.setAttribute("data-theme", theme);
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch {
    /* private mode */
  }
}

export function toggleTheme(current: Theme): Theme {
  const next: Theme = current === "dark" ? "light" : "dark";
  applyTheme(next);
  return next;
}
