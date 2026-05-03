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
    runMockTranscription: "Run Mock Transcription",
    transcribingMedia: "Transcribing...",
    loadingMeetings: "Loading meetings...",
    noMeetings: "No meetings yet. Import a local audio or video file to begin.",
    statusImported: "Imported",
    statusTranscribing: "Transcribing",
    statusTranscribed: "Transcribed",
    currentMeeting: "Current Meeting",
    sourceMedia: "Source Media",
    copiedMedia: "Copied Media",
    transcriptPending:
      "Transcript generation is ready. Run the mock transcription to persist speaker segments.",
    noTranscript: "No transcript yet. Start mock transcription for this meeting.",
    transcriptTitle: "Transcript",
    transcriptEditorLabel: "Transcript editor",
    saveTranscript: "Save Transcript",
    savingTranscript: "Saving...",
    resetTranscript: "Reset",
    reloadMockData: "Reload Mock Data",
    mockWorkspaceLoadError: "Failed to load mock workspace",
    noteTitle: "Meeting Note",
    regenerate: "Regenerate",
    generatingNote: "Generating...",
    saveNote: "Save Note",
    savingNote: "Saving...",
    exportMarkdown: "Export Markdown",
    exportingMarkdown: "Exporting...",
    exportPdf: "Export PDF",
    exportingPdf: "Exporting...",
    exportWord: "Export Word",
    exportingWord: "Exporting...",
    exportHistory: "Export History",
    noExports: "No exports yet.",
    openExportFolder: "Open Folder",
    openingExportFolder: "Opening...",
    noteEditorLabel: "Meeting note editor",
    notePlaceholder: "# Meeting Minutes\n\nGenerate a note after transcription.",
    lowConfidence: "Low confidence",
    speakerNameLabel: "Speaker name",
    renameSpeaker: "Rename",
    latestTranscriptionTask: "Latest Transcription Task",
    taskStatus: "Status",
    taskAttempts: "Attempts",
    retryTask: "Retry",
    retryingTask: "Retrying...",
    themeSwitcherLabel: "Theme",
    themeLightClarity: "Clarity",
    themeLightSage: "Sage",
    themeLightQuartz: "Quartz",
    themeDarkGraphite: "Graphite",
    themeDarkEmber: "Ember",
    themeDarkAurora: "Aurora",
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
    recentLogsTitle: "Recent Logs",
    recentLogsDescription: "Latest local workflow events from the backend workspace log.",
    loadingRecentLogs: "Loading recent logs...",
    noRecentLogs: "No recent logs yet.",
    yes: "Yes",
    no: "No",
    loadingSettings: "Loading settings..."
  },
  zh: {
    appEyebrow: "本地优先桌面工作区",
    workspaceNav: "工作区",
    settingsNav: "设置",
    primaryNavigation: "主导航",
    languageToggleLabel: "切换语言",
    languageEnglish: "EN",
    languageChinese: "中文",
    backendChecking: "正在检查后端",
    backendOnline: "后端 {version}",
    backendOffline: "后端离线",
    meetingLibraryTitle: "会议库",
    mockWorkspaceDescription: "P0 模拟工作区。P1 开始文件导入。",
    p1ImportDescription: "导入本地媒体并创建会议记录。",
    importMedia: "导入媒体",
    importingMedia: "导入中...",
    runMockTranscription: "运行模拟转写",
    transcribingMedia: "转写中...",
    loadingMeetings: "正在加载会议...",
    noMeetings: "还没有会议。导入本地音频或视频文件开始。",
    statusImported: "已导入",
    statusTranscribing: "转写中",
    statusTranscribed: "已转写",
    currentMeeting: "当前会议",
    sourceMedia: "源媒体",
    copiedMedia: "已复制媒体",
    transcriptPending: "转写流程已就绪。运行模拟转写以保存说话人片段。",
    noTranscript: "还没有转写文本。请先为当前会议运行模拟转写。",
    transcriptTitle: "转写文本",
    reloadMockData: "重新加载模拟数据",
    mockWorkspaceLoadError: "模拟工作区加载失败",
    noteTitle: "会议纪要",
    regenerate: "重新生成",
    generatingNote: "生成中...",
    saveNote: "保存纪要",
    savingNote: "保存中...",
    exportMarkdown: "导出 Markdown",
    exportingMarkdown: "导出中...",
    exportPdf: "导出 PDF",
    exportingPdf: "导出中...",
    exportWord: "导出 Word",
    exportingWord: "导出中...",
    exportHistory: "导出历史",
    noExports: "还没有导出记录。",
    openExportFolder: "打开文件夹",
    openingExportFolder: "打开中...",
    noteEditorLabel: "会议纪要编辑器",
    notePlaceholder: "# 会议纪要\n\n转写完成后可生成纪要。",
    lowConfidence: "低置信度",
    speakerNameLabel: "说话人名称",
    renameSpeaker: "重命名",
    latestTranscriptionTask: "最新转写任务",
    taskStatus: "状态",
    taskAttempts: "尝试次数",
    retryTask: "重试",
    retryingTask: "重试中...",
    themeSwitcherLabel: "主题",
    themeLightClarity: "明亮清晰",
    themeLightSage: "浅色青绿",
    themeLightQuartz: "浅色石英",
    themeDarkGraphite: "深色石墨",
    themeDarkEmber: "深色暖焰",
    themeDarkAurora: "深色极光",
    workflowImport: "导入",
    workflowTranscribe: "转写",
    workflowOrganize: "整理",
    workflowNotes: "纪要",
    workflowReview: "校对",
    workflowExport: "导出",
    settingsTitle: "设置",
    refresh: "刷新",
    settingsDescription:
      "这些值来自本地开发环境。后续会加入更完整的安全密钥录入。",
    apiHost: "API 主机",
    apiPort: "API 端口",
    workspace: "工作区",
    dashscopeBaseUrl: "DashScope Base URL",
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
      const localizedTranslations = translations[this.language] as Partial<
        Record<TranslationKey, string>
      >;
      let text: string = localizedTranslations[key] ?? translations.en[key];

      if (params) {
        for (const [paramKey, value] of Object.entries(params)) {
          text = text.replace(`{${paramKey}}`, String(value));
        }
      }

      return text;
    }
  }
});
