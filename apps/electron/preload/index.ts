import { contextBridge } from "electron";

const backendBaseUrl = `http://${process.env.ECHOMINUTES_API_HOST ?? "127.0.0.1"}:${
  process.env.ECHOMINUTES_API_PORT ?? "8765"
}`;

contextBridge.exposeInMainWorld("echominutes", {
  backend: {
    getBaseUrl: async () => backendBaseUrl
  }
});
