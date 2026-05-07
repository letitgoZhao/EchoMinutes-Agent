import { defineStore } from "pinia";

const STORAGE_KEY = "echominutes.theme";

export const themeOptions = [
  { id: "light-clarity", labelKey: "themeLightClarity", tone: "light" },
  { id: "light-sage", labelKey: "themeLightSage", tone: "light" },
  { id: "light-quartz", labelKey: "themeLightQuartz", tone: "light" },
  { id: "dark-graphite", labelKey: "themeDarkGraphite", tone: "dark" },
  { id: "dark-ember", labelKey: "themeDarkEmber", tone: "dark" },
  { id: "dark-aurora", labelKey: "themeDarkAurora", tone: "dark" }
] as const;

export type ThemeId = (typeof themeOptions)[number]["id"];

function readInitialTheme(): ThemeId {
  if (typeof window === "undefined") {
    return "light-clarity";
  }

  const storedTheme = window.localStorage.getItem(STORAGE_KEY);
  return themeOptions.some((theme) => theme.id === storedTheme)
    ? (storedTheme as ThemeId)
    : "light-clarity";
}

function applyThemeAttribute(theme: ThemeId): void {
  if (typeof document === "undefined") {
    return;
  }

  document.documentElement.dataset.theme = theme;
}

export const useThemeStore = defineStore("theme", {
  state: () => ({
    theme: readInitialTheme()
  }),
  actions: {
    applyCurrentTheme() {
      applyThemeAttribute(this.theme);
    },
    setTheme(theme: ThemeId) {
      this.theme = theme;
      window.localStorage.setItem(STORAGE_KEY, theme);
      applyThemeAttribute(theme);
    }
  }
});
