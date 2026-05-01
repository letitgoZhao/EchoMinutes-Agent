/// <reference types="vite/client" />

interface EchoMinutesDesktopApi {
  backend: {
    getBaseUrl: () => Promise<string>;
  };
}

declare global {
  interface Window {
    echominutes?: EchoMinutesDesktopApi;
  }
}

export {};
