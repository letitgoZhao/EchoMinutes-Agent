import { app, BrowserWindow, dialog, ipcMain, shell } from "electron";
import { spawn, spawnSync, type ChildProcessWithoutNullStreams } from "node:child_process";
import { appendFileSync, existsSync, mkdirSync } from "node:fs";
import { request } from "node:http";
import { dirname, isAbsolute, join, resolve } from "node:path";

let mainWindow: BrowserWindow | null = null;
let backendProcess: ChildProcessWithoutNullStreams | null = null;

const BACKEND_HOST = process.env.ECHOMINUTES_API_HOST ?? "127.0.0.1";
const BACKEND_PORT = process.env.ECHOMINUTES_API_PORT ?? "8765";
const BACKEND_BASE_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}`;

interface SelectedMediaFile {
  canceled: boolean;
  filePath: string | null;
  fileName: string | null;
}

interface BackendLaunchCommand {
  command: string;
  args: string[];
  cwd: string;
  env: NodeJS.ProcessEnv;
  description: string;
}

function writeBackendLog(message: string): void {
  const timestamp = new Date().toISOString();
  const logLine = `[${timestamp}] ${message}\n`;

  console.info(logLine.trimEnd());

  try {
    const logPath = join(app.getPath("userData"), "logs", "backend-runtime.log");
    mkdirSync(dirname(logPath), { recursive: true });
    appendFileSync(logPath, logLine, "utf8");
  } catch (error) {
    console.warn(`[backend] Unable to write backend runtime log: ${String(error)}`);
  }
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

function getBackendEnvironment(projectRoot: string): NodeJS.ProcessEnv {
  return {
    ...process.env,
    ECHOMINUTES_API_HOST: BACKEND_HOST,
    ECHOMINUTES_API_PORT: BACKEND_PORT,
    ECHOMINUTES_PROJECT_DIR: projectRoot,
    ECHOMINUTES_WORKSPACE_DIR:
      process.env.ECHOMINUTES_WORKSPACE_DIR ?? join(app.getPath("userData"), "workspace.local")
  };
}

function getPackagedBackendExecutable(): string | null {
  const executableName = process.platform === "win32" ? "echominutes-backend.exe" : "echominutes-backend";
  const explicitExecutable = process.env.ECHOMINUTES_BACKEND_EXE;

  const candidates = [
    explicitExecutable,
    join(process.resourcesPath, "backend-runtime", executableName),
    join(process.resourcesPath, executableName)
  ].filter(Boolean) as string[];

  return candidates.find((candidate) => existsSync(candidate)) ?? null;
}

function getPackagedPythonExecutable(projectRoot: string): string | null {
  const executableName = process.platform === "win32" ? "python.exe" : "python";
  const candidates = [
    join(projectRoot, ".venv", process.platform === "win32" ? "Scripts" : "bin", executableName),
    join(process.resourcesPath, ".venv", process.platform === "win32" ? "Scripts" : "bin", executableName)
  ];

  return candidates.find((candidate) => existsSync(candidate)) ?? null;
}

function getBackendLaunchCommands(projectRoot: string): BackendLaunchCommand[] {
  const env = getBackendEnvironment(projectRoot);
  const packagedBackendExecutable = getPackagedBackendExecutable();
  const packagedPythonExecutable = getPackagedPythonExecutable(projectRoot);
  const uvicornArgs = [
    "uvicorn",
    "--app-dir",
    "backend",
    "app.main:app",
    "--host",
    BACKEND_HOST,
    "--port",
    BACKEND_PORT
  ];
  const commands: BackendLaunchCommand[] = [];

  if (packagedBackendExecutable) {
    commands.push({
      command: packagedBackendExecutable,
      args: ["--host", BACKEND_HOST, "--port", BACKEND_PORT],
      cwd: projectRoot,
      env,
      description: "packaged backend runtime"
    });
  }

  if (packagedPythonExecutable) {
    commands.push({
      command: packagedPythonExecutable,
      args: ["-m", ...uvicornArgs],
      cwd: projectRoot,
      env,
      description: "packaged Python virtual environment"
    });
  }

  commands.push({
    command: "uv",
    args: ["run", ...uvicornArgs],
    cwd: projectRoot,
    env,
    description: "local uv environment"
  });

  return commands;
}

async function waitForBackendReady(timeoutMs = 12000): Promise<boolean> {
  const startedAt = Date.now();

  while (Date.now() - startedAt < timeoutMs) {
    if (await isBackendRunning()) {
      return true;
    }

    await new Promise((resolveReady) => setTimeout(resolveReady, 400));
  }

  return false;
}

async function startBackend(): Promise<void> {
  if (backendProcess) {
    return;
  }

  const projectRoot = findProjectRoot();

  for (const launchCommand of getBackendLaunchCommands(projectRoot)) {
    writeBackendLog(
      `[backend] Starting with ${launchCommand.description}: ${launchCommand.command} ${launchCommand.args.join(" ")}`
    );

    backendProcess = spawn(launchCommand.command, launchCommand.args, {
      cwd: launchCommand.cwd,
      env: launchCommand.env,
      windowsHide: true
    });

    backendProcess.stdout.on("data", (chunk) => {
      writeBackendLog(`[backend:stdout] ${chunk.toString().trim()}`);
    });

    backendProcess.stderr.on("data", (chunk) => {
      writeBackendLog(`[backend:stderr] ${chunk.toString().trim()}`);
    });

    const spawnError = await new Promise<Error | null>((resolveSpawnError) => {
      const errorTimer = setTimeout(() => resolveSpawnError(null), 500);
      backendProcess?.once("error", (error) => {
        clearTimeout(errorTimer);
        resolveSpawnError(error);
      });
    });

    if (spawnError) {
      writeBackendLog(
        `[backend] Failed to start with ${launchCommand.description}: ${spawnError.message}`
      );
      backendProcess = null;
      continue;
    }

    backendProcess.on("exit", (code, signal) => {
      writeBackendLog(`[backend] Process exited with code=${code ?? "null"} signal=${signal ?? "null"}`);
      backendProcess = null;
    });

    if (await waitForBackendReady()) {
      writeBackendLog(`[backend] Ready at ${BACKEND_BASE_URL}/api/health`);
      return;
    }

    writeBackendLog(`[backend] ${launchCommand.description} did not become ready before timeout.`);
    stopBackend();
  }

  writeBackendLog("[backend] All backend launch strategies failed.");
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
    await startBackend();
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
