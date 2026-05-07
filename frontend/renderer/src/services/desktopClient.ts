export interface SelectedMediaFile {
  canceled: boolean;
  filePath: string | null;
  fileName: string | null;
}

export class DesktopCapabilityError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "DesktopCapabilityError";
  }
}

export async function selectMediaFile(): Promise<SelectedMediaFile> {
  if (!window.echominutes?.media) {
    throw new DesktopCapabilityError(
      "The Electron desktop bridge is unavailable. Restart the desktop app and try again."
    );
  }

  return window.echominutes.media.selectFile();
}

export async function openLocalPath(targetPath: string): Promise<void> {
  if (!window.echominutes?.shell) {
    throw new DesktopCapabilityError(
      "The Electron desktop bridge is unavailable. Restart the desktop app and try again."
    );
  }

  await window.echominutes.shell.openPath(targetPath);
}
