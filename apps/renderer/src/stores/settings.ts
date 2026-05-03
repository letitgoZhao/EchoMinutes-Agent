import { defineStore } from "pinia";

import { getRecentLogs, getSettings, type AppSettings, type LogEntry } from "../services/apiClient";

interface SettingsState {
  settings: AppSettings | null;
  loading: boolean;
  logs: LogEntry[];
  logsLoading: boolean;
  error: string | null;
}

export const useSettingsStore = defineStore("settings", {
  state: (): SettingsState => ({
    settings: null,
    loading: false,
    logs: [],
    logsLoading: false,
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
    },
    async loadRecentLogs() {
      this.logsLoading = true;
      this.error = null;
      try {
        this.logs = await getRecentLogs();
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to load recent logs";
      } finally {
        this.logsLoading = false;
      }
    },
    async loadDiagnostics() {
      await Promise.all([this.loadSettings(), this.loadRecentLogs()]);
    }
  }
});
