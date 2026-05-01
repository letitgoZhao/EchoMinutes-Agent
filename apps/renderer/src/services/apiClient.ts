export interface HealthResponse {
  ok: boolean;
  version: string;
  workspaceDir: string;
}

export interface AppSettings {
  apiHost: string;
  apiPort: number;
  workspaceDir: string;
  dashscopeBaseUrl: string;
  dashscopeModel: string;
  hasDashscopeApiKey: boolean;
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
  markdown: string;
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
    throw new Error(`Request failed: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export function getHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>("/api/health");
}

export function getSettings(): Promise<AppSettings> {
  return requestJson<AppSettings>("/api/settings");
}

export function getMockTranscript(): Promise<TranscriptSegment[]> {
  return requestJson<TranscriptSegment[]>("/api/dev/mock/transcript");
}

export function getMockNote(): Promise<NoteResponse> {
  return requestJson<NoteResponse>("/api/dev/mock/note");
}
