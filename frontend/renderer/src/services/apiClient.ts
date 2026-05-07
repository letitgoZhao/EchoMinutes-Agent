export interface HealthResponse {
  ok: boolean;
  version: string;
  workspaceDir: string;
}

export interface AppSettings {
  apiHost: string;
  apiPort: number;
  workspaceDir: string;
  transcriptionProvider: string;
  asrReady: boolean;
  dashscopeBaseUrl: string;
  dashscopeModel: string;
  dashscopeAsrBaseUrl: string;
  dashscopeAsrModel: string;
  dashscopeAsrSpeakerCount: number;
  hasDashscopeApiKey: boolean;
  ffmpegAvailable: boolean;
  ffmpegPath: string | null;
}

export interface AppSettingsUpdate {
  workspaceDir?: string;
  dashscopeApiKey?: string;
  dashscopeBaseUrl?: string;
  dashscopeModel?: string;
  dashscopeAsrBaseUrl?: string;
  dashscopeAsrModel?: string;
  dashscopeAsrSpeakerCount?: number;
  clearDashscopeApiKey?: boolean;
}

export interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
}

export interface ProviderTestResponse {
  ok: boolean;
  provider: string;
  model?: string;
  ffmpeg?: string;
  message: string;
}

export interface TranscriptSegment {
  id: string;
  speaker: string;
  startMs: number;
  endMs: number;
  text: string;
  confidence: number;
}

export interface NoteResponse {
  id: string | null;
  meetingId: string | null;
  markdown: string;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface Meeting {
  id: string;
  title: string;
  sourceFileName: string;
  sourceFilePath: string;
  workspaceMediaPath: string;
  language: string;
  accentHint: string | null;
  status: string;
  durationSeconds: number | null;
  errorMessage: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface MeetingCreate {
  sourceFilePath: string;
  title?: string;
  language?: string;
  accentHint?: string | null;
}

export interface ExportRecord {
  id: string;
  meetingId: string;
  format: ExportFormat;
  fileName: string;
  filePath: string;
  folderPath: string;
  createdAt: string;
}

export type ExportFormat = "markdown" | "pdf" | "word";

export interface ProcessingTask {
  id: string;
  meetingId: string;
  kind: string;
  status: string;
  attemptCount: number;
  retryable: boolean;
  errorMessage: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface TranscriptionTaskRunResponse {
  task: ProcessingTask;
  meeting: Meeting;
}

let cachedBaseUrl: string | null = null;

export async function getBackendBaseUrl(): Promise<string> {
  if (cachedBaseUrl) {
    return cachedBaseUrl;
  }

  cachedBaseUrl =
    (await window.echominutes?.backend.getBaseUrl()) ?? "http://127.0.0.1:8765";
  return cachedBaseUrl;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const baseUrl = await getBackendBaseUrl();
  const response = await fetch(`${baseUrl}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    },
    ...init
  });

  if (!response.ok) {
    let detail = "";
    const contentType = response.headers.get("content-type") ?? "";
    if (contentType.includes("application/json")) {
      const errorPayload = (await response.json()) as { detail?: string };
      detail = errorPayload.detail?.trim() ?? "";
    } else {
      detail = (await response.text()).trim();
    }

    const suffix = detail ? ` - ${detail}` : "";
    throw new Error(`Request failed: ${response.status} ${response.statusText}${suffix}`);
  }

  return response.json() as Promise<T>;
}

export function getHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>("/api/health");
}

export function getSettings(): Promise<AppSettings> {
  return requestJson<AppSettings>("/api/settings");
}

export function updateSettings(payload: AppSettingsUpdate): Promise<AppSettings> {
  return requestJson<AppSettings>("/api/settings", {
    method: "PUT",
    body: JSON.stringify({
      workspace_dir: payload.workspaceDir,
      dashscope_api_key: payload.dashscopeApiKey,
      dashscope_base_url: payload.dashscopeBaseUrl,
      dashscope_model: payload.dashscopeModel,
      dashscope_asr_base_url: payload.dashscopeAsrBaseUrl,
      dashscope_asr_model: payload.dashscopeAsrModel,
      dashscope_asr_speaker_count: payload.dashscopeAsrSpeakerCount,
      clear_dashscope_api_key: payload.clearDashscopeApiKey ?? false
    })
  });
}

export function getRecentLogs(limit = 50): Promise<LogEntry[]> {
  return requestJson<LogEntry[]>(`/api/logs/recent?limit=${limit}`);
}

export function testLlmSettings(): Promise<ProviderTestResponse> {
  return requestJson<ProviderTestResponse>("/api/settings/test-llm", {
    method: "POST"
  });
}

export function testAsrSettings(): Promise<ProviderTestResponse> {
  return requestJson<ProviderTestResponse>("/api/settings/test-asr", {
    method: "POST"
  });
}

export function getMeetings(): Promise<Meeting[]> {
  return requestJson<Meeting[]>("/api/meetings");
}

export function createMeeting(payload: MeetingCreate): Promise<Meeting> {
  return requestJson<Meeting>("/api/meetings", {
    method: "POST",
    body: JSON.stringify({
      source_file_path: payload.sourceFilePath,
      title: payload.title,
      language: payload.language ?? "auto",
      accent_hint: payload.accentHint ?? null
    })
  });
}

export function transcribeMeeting(meetingId: string): Promise<Meeting> {
  return requestJson<Meeting>(`/api/meetings/${meetingId}/transcribe`, {
    method: "POST"
  });
}

export function getTranscriptionTasks(meetingId: string): Promise<ProcessingTask[]> {
  return requestJson<ProcessingTask[]>(`/api/meetings/${meetingId}/transcription-tasks`);
}

export function startTranscriptionTask(meetingId: string): Promise<TranscriptionTaskRunResponse> {
  return requestJson<TranscriptionTaskRunResponse>(
    `/api/meetings/${meetingId}/transcription-tasks`,
    {
      method: "POST"
    }
  );
}

export function retryTranscriptionTask(
  meetingId: string,
  taskId: string
): Promise<TranscriptionTaskRunResponse> {
  return requestJson<TranscriptionTaskRunResponse>(
    `/api/meetings/${meetingId}/transcription-tasks/${taskId}/retry`,
    {
      method: "POST"
    }
  );
}

export function getMeetingTranscript(meetingId: string): Promise<TranscriptSegment[]> {
  return requestJson<TranscriptSegment[]>(`/api/meetings/${meetingId}/transcript`);
}

export function renameSpeaker(
  meetingId: string,
  currentSpeaker: string,
  newSpeaker: string
): Promise<TranscriptSegment[]> {
  return requestJson<TranscriptSegment[]>(`/api/meetings/${meetingId}/speakers`, {
    method: "PUT",
    body: JSON.stringify({
      current_speaker: currentSpeaker,
      new_speaker: newSpeaker
    })
  });
}

export function updateTranscriptSegment(
  meetingId: string,
  segmentId: string,
  text: string
): Promise<TranscriptSegment> {
  return requestJson<TranscriptSegment>(`/api/meetings/${meetingId}/segments/${segmentId}`, {
    method: "PATCH",
    body: JSON.stringify({ text })
  });
}

export function getMeetingNote(meetingId: string): Promise<NoteResponse | null> {
  return requestJson<NoteResponse | null>(`/api/meetings/${meetingId}/note`);
}

export function summarizeMeeting(meetingId: string): Promise<NoteResponse> {
  return requestJson<NoteResponse>(`/api/meetings/${meetingId}/note/summarize`, {
    method: "POST"
  });
}

export function saveMeetingNote(meetingId: string, markdown: string): Promise<NoteResponse> {
  return requestJson<NoteResponse>(`/api/meetings/${meetingId}/note`, {
    method: "PUT",
    body: JSON.stringify({ markdown })
  });
}

export function getMeetingExports(meetingId: string): Promise<ExportRecord[]> {
  return requestJson<ExportRecord[]>(`/api/meetings/${meetingId}/exports`);
}

export function exportMeeting(meetingId: string, format: ExportFormat): Promise<ExportRecord> {
  return requestJson<ExportRecord>(`/api/meetings/${meetingId}/exports`, {
    method: "POST",
    body: JSON.stringify({ format })
  });
}
