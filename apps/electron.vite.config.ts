import { resolve } from "node:path";

import vue from "@vitejs/plugin-vue";
import { defineConfig } from "electron-vite";

export default defineConfig({
  main: {
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, "electron/main/index.ts")
        }
      }
    }
  },
  preload: {
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, "electron/preload/index.ts")
        }
      }
    }
  },
  renderer: {
    root: resolve(__dirname, "renderer"),
    plugins: [vue()],
    build: {
      rollupOptions: {
        input: resolve(__dirname, "renderer/index.html")
      }
    },
    server: {
      host: "127.0.0.1",
      port: 5173
    }
  }
});
