import { defineStore } from "pinia";

import { getSettings, type AppSettings } from "../services/apiClient";

interface SettingsState {
  settings: AppSettings | null;
  loading: boolean;
  error: string | null;
}

export const useSettingsStore = defineStore("settings", {
  state: (): SettingsState => ({
    settings: null,
    loading: false,
    error: null
  }),
  actions: {
    async loadSettings() {
      this.loading = true;
      this.error = null;
      try {
        this.settings = await getSettings();
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to load settings";
      } finally {
        this.loading = false;
      }
    }
  }
});
