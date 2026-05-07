import { defineStore } from "pinia";

import {
  getRecentLogs,
  getSettings,
  testAsrSettings,
  testLlmSettings,
  updateSettings,
  type AppSettings,
  type AppSettingsUpdate,
  type LogEntry,
  type ProviderTestResponse
} from "../services/apiClient";

interface SettingsState {
  settings: AppSettings | null;
  loading: boolean;
  logs: LogEntry[];
  logsLoading: boolean;
  llmTest: ProviderTestResponse | null;
  asrTest: ProviderTestResponse | null;
  testingLlm: boolean;
  testingAsr: boolean;
  saving: boolean;
  error: string | null;
  savedMessage: string | null;
}

export const useSettingsStore = defineStore("settings", {
  state: (): SettingsState => ({
    settings: null,
    loading: false,
    logs: [],
    logsLoading: false,
    llmTest: null,
    asrTest: null,
    testingLlm: false,
    testingAsr: false,
    saving: false,
    error: null,
    savedMessage: null
  }),
  actions: {
    async loadSettings() {
      this.loading = true;
      this.error = null;
      this.savedMessage = null;
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
    },
    async saveSettings(payload: AppSettingsUpdate) {
      this.saving = true;
      this.error = null;
      this.savedMessage = null;
      try {
        this.settings = await updateSettings(payload);
        this.savedMessage = "Settings saved locally.";
        this.llmTest = null;
        this.asrTest = null;
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to save settings";
      } finally {
        this.saving = false;
      }
    },
    async testLlmProvider() {
      this.testingLlm = true;
      this.error = null;
      try {
        this.llmTest = await testLlmSettings();
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to test LLM provider";
      } finally {
        this.testingLlm = false;
      }
    },
    async testAsrProvider() {
      this.testingAsr = true;
      this.error = null;
      try {
        this.asrTest = await testAsrSettings();
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to test ASR provider";
      } finally {
        this.testingAsr = false;
      }
    }
  }
});
