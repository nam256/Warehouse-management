import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { applyTheme, getStoredTheme, toggleTheme as flipTheme, type Theme } from "./theme";

type ThemeContextValue = {
  theme: Theme;
  isDark: boolean;
  setTheme: (theme: Theme) => void;
  toggle: () => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => getStoredTheme());

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  const value = useMemo<ThemeContextValue>(
    () => ({
      theme,
      isDark: theme === "dark",
      setTheme: (next) => {
        applyTheme(next);
        setThemeState(next);
      },
      toggle: () => {
        setThemeState((current) => flipTheme(current));
      },
    }),
    [theme],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme phải dùng trong ThemeProvider");
  }
  return ctx;
}
