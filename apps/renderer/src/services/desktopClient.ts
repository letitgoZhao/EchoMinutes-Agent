export interface SelectedMediaFile {
  canceled: boolean;
  filePath: string | null;
  fileName: string | null;
}

export async function selectMediaFile(): Promise<SelectedMediaFile> {
  const fallback: SelectedMediaFile = {
    canceled: true,
    filePath: null,
    fileName: null
  };

  return window.echominutes?.media.selectFile() ?? fallback;
}
