/// <reference types="vite/client" />

interface EchoMinutesDesktopApi {
  backend: {
    getBaseUrl: () => Promise<string>;
  };
  media: {
    selectFile: () => Promise<{
      canceled: boolean;
      filePath: string | null;
      fileName: string | null;
    }>;
  };
}

declare global {
  interface Window {
    echominutes?: EchoMinutesDesktopApi;
  }
}

export {};
