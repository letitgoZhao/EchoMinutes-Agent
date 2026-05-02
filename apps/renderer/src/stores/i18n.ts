import { defineStore } from "pinia";

const STORAGE_KEY = "echominutes.language";

export const translations = {
  en: {
    appEyebrow: "Local-first desktop workspace",
    workspaceNav: "Workspace",
    settingsNav: "Settings",
    primaryNavigation: "Primary navigation",
    languageToggleLabel: "Switch language",
    languageEnglish: "EN",
    languageChinese: "Chinese",
    backendChecking: "Checking backend",
    backendOnline: "Backend {version}",
    backendOffline: "Backend offline",
    meetingLibraryTitle: "Meeting Library",
    mockWorkspaceDescription: "P0 mock workspace. File import starts in P1.",
    p1ImportDescription: "Import local media to create a meeting record.",
    importMedia: "Import Media",
    importingMedia: "Importing...",
    loadingMeetings: "Loading meetings...",
    noMeetings: "No meetings yet. Import a local audio or video file to begin.",
    statusImported: "Imported",
    currentMeeting: "Current Meeting",
    sourceMedia: "Source Media",
    copiedMedia: "Copied Media",
    transcriptPending: "Transcript generation starts in P1b. Mock transcript remains visible for now.",
    transcriptTitle: "Transcript",
    reloadMockData: "Reload Mock Data",
    mockWorkspaceLoadError: "Failed to load mock workspace",
    noteTitle: "Meeting Note",
    regenerate: "Regenerate",
    noteEditorLabel: "Meeting note editor",
    notePlaceholder: "# Meeting Minutes\n\nMock note will appear here.",
    lowConfidence: "Low confidence",
    workflowImport: "Import",
    workflowTranscribe: "Transcribe",
    workflowOrganize: "Organize",
    workflowNotes: "Notes",
    workflowReview: "Review",
    workflowExport: "Export",
    settingsTitle: "Settings",
    refresh: "Refresh",
    settingsDescription:
      "These values are read from the local development environment for P0. Interactive secure key entry will be added later.",
    apiHost: "API Host",
    apiPort: "API Port",
    workspace: "Workspace",
    dashscopeBaseUrl: "DashScope Base URL",
    dashscopeModel: "DashScope Model",
    apiKeyConfigured: "API Key Configured",
    yes: "Yes",
    no: "No",
    loadingSettings: "Loading settings..."
  },
  zh: {
    appEyebrow: "本地优先桌面工作台",
    workspaceNav: "工作台",
    settingsNav: "设置",
    primaryNavigation: "主导航",
    languageToggleLabel: "切换语言",
    languageEnglish: "EN",
    languageChinese: "中文",
    backendChecking: "正在检查后端",
    backendOnline: "后端 {version}",
    backendOffline: "后端离线",
    meetingLibraryTitle: "会议库",
    mockWorkspaceDescription: "P0 模拟工作台。文件导入会在 P1 开始实现。",
    p1ImportDescription: "导入本地音视频，并创建会议记录。",
    importMedia: "导入音视频",
    importingMedia: "正在导入...",
    loadingMeetings: "正在加载会议...",
    noMeetings: "还没有会议。导入一个本地音频或视频文件开始。",
    statusImported: "已导入",
    currentMeeting: "当前会议",
    sourceMedia: "源媒体",
    copiedMedia: "已复制媒体",
    transcriptPending: "转写生成会在 P1b 开始实现。当前仍显示模拟转写内容。",
    transcriptTitle: "转写内容",
    reloadMockData: "重新加载模拟数据",
    mockWorkspaceLoadError: "加载模拟工作台失败",
    noteTitle: "会议纪要",
    regenerate: "重新生成",
    noteEditorLabel: "会议纪要编辑器",
    notePlaceholder: "# 会议纪要\n\n这里会显示模拟纪要。",
    lowConfidence: "低置信度",
    workflowImport: "导入",
    workflowTranscribe: "转写",
    workflowOrganize: "整理",
    workflowNotes: "纪要",
    workflowReview: "审阅",
    workflowExport: "导出",
    settingsTitle: "设置",
    refresh: "刷新",
    settingsDescription:
      "这些值来自 P0 阶段的本地开发环境。后续会加入安全的交互式密钥录入。",
    apiHost: "API 主机",
    apiPort: "API 端口",
    workspace: "工作区",
    dashscopeBaseUrl: "DashScope 基础地址",
    dashscopeModel: "DashScope 模型",
    apiKeyConfigured: "已配置 API Key",
    yes: "是",
    no: "否",
    loadingSettings: "正在加载设置..."
  }
} as const;

export type LanguageCode = keyof typeof translations;
export type TranslationKey = keyof (typeof translations)["en"];

function readInitialLanguage(): LanguageCode {
  if (typeof window === "undefined") {
    return "zh";
  }

  const storedLanguage = window.localStorage.getItem(STORAGE_KEY);
  return storedLanguage === "en" || storedLanguage === "zh" ? storedLanguage : "zh";
}

export const useI18nStore = defineStore("i18n", {
  state: () => ({
    language: readInitialLanguage()
  }),
  actions: {
    setLanguage(language: LanguageCode) {
      this.language = language;
      window.localStorage.setItem(STORAGE_KEY, language);
    },
    toggleLanguage() {
      this.setLanguage(this.language === "zh" ? "en" : "zh");
    },
    t(key: TranslationKey, params?: Record<string, string | number>) {
      let text: string = translations[this.language][key] ?? translations.en[key];

      if (params) {
        for (const [paramKey, value] of Object.entries(params)) {
          text = text.replace(`{${paramKey}}`, String(value));
        }
      }

      return text;
    }
  }
});
