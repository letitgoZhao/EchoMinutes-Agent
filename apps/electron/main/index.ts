import { app, BrowserWindow, shell } from "electron";
import { spawn, type ChildProcessWithoutNullStreams } from "node:child_process";
import { existsSync } from "node:fs";
import { request } from "node:http";
import { join, resolve } from "node:path";

let mainWindow: BrowserWindow | null = null;
let backendProcess: ChildProcessWithoutNullStreams | null = null;

const BACKEND_HOST = process.env.ECHOMINUTES_API_HOST ?? "127.0.0.1";
const BACKEND_PORT = process.env.ECHOMINUTES_API_PORT ?? "8765";

function findBackendDir(): string {
  const candidates = [
    process.env.ECHOMINUTES_BACKEND_DIR,
    resolve(app.getAppPath(), "../backend"),
    resolve(app.getAppPath(), "../../backend"),
    resolve(process.cwd(), "../backend"),
    resolve(process.cwd(), "../../backend"),
    resolve(process.cwd(), "backend")
  ].filter(Boolean) as string[];

  const backendDir = candidates.find((candidate) =>
    existsSync(join(candidate, "pyproject.toml"))
  );

  if (!backendDir) {
    throw new Error("Unable to locate backend/pyproject.toml");
  }

  return backendDir;
}

function startBackend(): void {
  if (backendProcess) {
    return;
  }

  const backendDir = findBackendDir();
  backendProcess = spawn(
    "uv",
    [
      "run",
      "--project",
      backendDir,
      "uvicorn",
      "app.main:app",
      "--host",
      BACKEND_HOST,
      "--port",
      BACKEND_PORT
    ],
    {
      cwd: backendDir,
      env: process.env
    }
  );

  backendProcess.stdout.on("data", (chunk) => {
    console.info(`[backend] ${chunk.toString().trim()}`);
  });

  backendProcess.stderr.on("data", (chunk) => {
    console.error(`[backend] ${chunk.toString().trim()}`);
  });

  backendProcess.on("exit", () => {
    backendProcess = null;
  });
}

function isBackendRunning(): Promise<boolean> {
  return new Promise((resolveBackendState) => {
    const healthRequest = request(
      {
        host: BACKEND_HOST,
        port: Number(BACKEND_PORT),
        path: "/api/health",
        method: "GET",
        timeout: 800
      },
      (response) => {
        response.resume();
        resolveBackendState(response.statusCode === 200);
      }
    );

    healthRequest.on("timeout", () => {
      healthRequest.destroy();
      resolveBackendState(false);
    });

    healthRequest.on("error", () => {
      resolveBackendState(false);
    });

    healthRequest.end();
  });
}

function stopBackend(): void {
  if (!backendProcess) {
    return;
  }

  backendProcess.kill();
  backendProcess = null;
}

async function createWindow(): Promise<void> {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 1024,
    minHeight: 680,
    title: "EchoMinutes Agent",
    webPreferences: {
      preload: join(__dirname, "../preload/index.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    void shell.openExternal(url);
    return { action: "deny" };
  });

  if (process.env.ELECTRON_RENDERER_URL) {
    await mainWindow.loadURL(process.env.ELECTRON_RENDERER_URL);
  } else {
    await mainWindow.loadFile(join(__dirname, "../renderer/index.html"));
  }
}

app.whenReady().then(async () => {
  const shouldSkipBackendStart = process.env.ECHOMINUTES_SKIP_BACKEND_START === "1";
  const backendAlreadyRunning = await isBackendRunning();

  if (!shouldSkipBackendStart && !backendAlreadyRunning) {
    startBackend();
  }

  await createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      void createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("before-quit", () => {
  stopBackend();
});
