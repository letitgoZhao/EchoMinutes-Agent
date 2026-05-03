import { app, BrowserWindow, dialog, ipcMain, shell } from "electron";
import { spawn, type ChildProcessWithoutNullStreams } from "node:child_process";
import { existsSync } from "node:fs";
import { request } from "node:http";
import { isAbsolute, join, resolve } from "node:path";

let mainWindow: BrowserWindow | null = null;
let backendProcess: ChildProcessWithoutNullStreams | null = null;

const BACKEND_HOST = process.env.ECHOMINUTES_API_HOST ?? "127.0.0.1";
const BACKEND_PORT = process.env.ECHOMINUTES_API_PORT ?? "8765";

interface SelectedMediaFile {
  canceled: boolean;
  filePath: string | null;
  fileName: string | null;
}

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

function getPreloadPath(): string {
  const candidates = [
    join(__dirname, "../preload/index.mjs"),
    join(__dirname, "../preload/index.js")
  ];

  const preloadPath = candidates.find((candidate) => existsSync(candidate));
  if (!preloadPath) {
    throw new Error("Unable to locate Electron preload bundle");
  }

  return preloadPath;
}

function registerIpcHandlers(): void {
  ipcMain.handle("media:select", async (): Promise<SelectedMediaFile> => {
    const dialogOptions: Electron.OpenDialogOptions = {
      title: "Select meeting media",
      properties: ["openFile"],
      filters: [
        {
          name: "Audio and video",
          extensions: [
            "aac",
            "flac",
            "m4a",
            "mkv",
            "mov",
            "mp3",
            "mp4",
            "ogg",
            "wav",
            "webm",
            "wma"
          ]
        },
        { name: "All files", extensions: ["*"] }
      ]
    };

    const result = mainWindow
      ? await dialog.showOpenDialog(mainWindow, dialogOptions)
      : await dialog.showOpenDialog(dialogOptions);

    if (result.canceled || result.filePaths.length === 0) {
      return {
        canceled: true,
        filePath: null,
        fileName: null
      };
    }

    const [filePath] = result.filePaths;
    return {
      canceled: false,
      filePath,
      fileName: filePath.split(/[\\/]/).pop() ?? filePath
    };
  });

  ipcMain.handle("shell:openPath", async (_event, targetPath: string): Promise<void> => {
    if (!targetPath || !isAbsolute(targetPath)) {
      throw new Error("A valid absolute path is required.");
    }

    const errorMessage = await shell.openPath(targetPath);
    if (errorMessage) {
      throw new Error(errorMessage);
    }
  });
}

async function createWindow(): Promise<void> {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 1024,
    minHeight: 680,
    title: "EchoMinutes Agent",
    webPreferences: {
      preload: getPreloadPath(),
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
  registerIpcHandlers();

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
