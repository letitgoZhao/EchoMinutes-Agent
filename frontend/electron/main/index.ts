import { app, BrowserWindow, dialog, ipcMain, shell } from "electron";
import { spawn, spawnSync, type ChildProcessWithoutNullStreams } from "node:child_process";
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

function findProjectRoot(): string {
  const candidates = [
    process.env.ECHOMINUTES_PROJECT_DIR,
    process.resourcesPath,
    join(process.resourcesPath, "app"),
    resolve(app.getAppPath(), ".."),
    resolve(app.getAppPath(), "../.."),
    resolve(process.cwd(), ".."),
    resolve(process.cwd(), "../.."),
    resolve(process.cwd(), ".")
  ].filter(Boolean) as string[];

  const projectRoot = candidates.find((candidate) =>
    existsSync(join(candidate, "pyproject.toml")) &&
    existsSync(join(candidate, "backend", "app", "main.py"))
  );

  if (!projectRoot) {
    throw new Error("Unable to locate project root with pyproject.toml and backend/app/main.py");
  }

  return projectRoot;
}

function startBackend(): void {
  if (backendProcess) {
    return;
  }

  const projectRoot = findProjectRoot();
  backendProcess = spawn(
    "uv",
    [
      "run",
      "uvicorn",
      "--app-dir",
      "backend",
      "app.main:app",
      "--host",
      BACKEND_HOST,
      "--port",
      BACKEND_PORT
    ],
    {
      cwd: projectRoot,
      env: process.env
    }
  );

  backendProcess.stdout.on("data", (chunk) => {
    console.info(`[backend] ${chunk.toString().trim()}`);
  });

  backendProcess.stderr.on("data", (chunk) => {
    console.error(`[backend] ${chunk.toString().trim()}`);
  });

  backendProcess.on("error", (error) => {
    console.error(`[backend] Failed to start backend process: ${error.message}`);
    backendProcess = null;
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

  const backendPid = backendProcess.pid;
  if (process.platform === "win32" && backendPid) {
    spawnSync("taskkill", ["/pid", String(backendPid), "/T", "/F"], {
      windowsHide: true
    });
  } else {
    backendProcess.kill();
  }
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
  const shouldStartBackend = !shouldSkipBackendStart && !backendAlreadyRunning;

  if (shouldStartBackend) {
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
