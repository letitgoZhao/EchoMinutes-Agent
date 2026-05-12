import { defineStore } from "pinia";

import {
  createMeeting,
  deleteMeeting,
  exportMeeting,
  getMeetingExports,
  getMeetingNote,
  getMeetingTranscript,
  getMeetings,
  getTranscriptionTasks,
  renameSpeaker,
  retryTranscriptionTask,
  saveMeetingNote,
  startTranscriptionTask,
  summarizeMeeting,
  updateTranscriptSegment as patchTranscriptSegment,
  type ExportFormat,
  type ExportRecord,
  type Meeting,
  type ProcessingTask,
  type TranscriptSegment
} from "../services/apiClient";
import { openLocalPath, selectMediaFile } from "../services/desktopClient";

interface MeetingsState {
  meetings: Meeting[];
  transcript: TranscriptSegment[];
  noteMarkdown: string;
  savedNoteMarkdown: string;
  exports: ExportRecord[];
  transcriptionTasks: ProcessingTask[];
  selectedMeetingId: string | null;
  loading: boolean;
  importing: boolean;
  transcribing: boolean;
  generatingNote: boolean;
  savingNote: boolean;
  exportingFormat: ExportFormat | null;
  openingExportFolder: boolean;
  retryingTranscription: boolean;
  renamingSpeaker: boolean;
  updatingTranscriptSegmentId: string | null;
  deletingMeetingId: string | null;
  error: string | null;
}

export const useMeetingsStore = defineStore("meetings", {
  state: (): MeetingsState => ({
    meetings: [],
    transcript: [],
    noteMarkdown: "",
    savedNoteMarkdown: "",
    exports: [],
    transcriptionTasks: [],
    selectedMeetingId: null,
    loading: false,
    importing: false,
    transcribing: false,
    generatingNote: false,
    savingNote: false,
    exportingFormat: null,
    openingExportFolder: false,
    retryingTranscription: false,
    renamingSpeaker: false,
    updatingTranscriptSegmentId: null,
    deletingMeetingId: null,
    error: null
  }),
  getters: {
    selectedMeeting(state): Meeting | null {
      return state.meetings.find((meeting) => meeting.id === state.selectedMeetingId) ?? null;
    },
    latestTranscriptionTask(state): ProcessingTask | null {
      return state.transcriptionTasks[0] ?? null;
    },
    hasSavedNote(state): boolean {
      return state.savedNoteMarkdown.trim().length > 0;
    },
    noteDirty(state): boolean {
      return state.noteMarkdown !== state.savedNoteMarkdown;
    }
  },
  actions: {
    async loadMeetings() {
      this.loading = true;
      this.error = null;
      try {
        this.meetings = await getMeetings();
        if (!this.selectedMeetingId && this.meetings.length > 0) {
          this.selectedMeetingId = this.meetings[0].id;
        }
        if (this.selectedMeetingId) {
          await this.loadTranscript(this.selectedMeetingId);
          await this.loadNote(this.selectedMeetingId);
          await this.loadExports(this.selectedMeetingId);
          await this.loadTranscriptionTasks(this.selectedMeetingId);
        }
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to load meetings";
      } finally {
        this.loading = false;
      }
    },
    async selectMeeting(meetingId: string) {
      this.selectedMeetingId = meetingId;
      await this.loadTranscript(meetingId);
      await this.loadNote(meetingId);
      await this.loadExports(meetingId);
      await this.loadTranscriptionTasks(meetingId);
    },
    clearSelectedMeeting() {
      this.selectedMeetingId = null;
      this.transcript = [];
      this.noteMarkdown = "";
      this.savedNoteMarkdown = "";
      this.exports = [];
      this.transcriptionTasks = [];
    },
    async importMedia() {
      this.importing = true;
      this.error = null;
      try {
        const selectedFile = await selectMediaFile();
        if (selectedFile.canceled || !selectedFile.filePath) {
          return;
        }

        const meeting = await createMeeting({
          sourceFilePath: selectedFile.filePath,
          language: "auto"
        });
        this.meetings = [
          meeting,
          ...this.meetings.filter((existingMeeting) => existingMeeting.id !== meeting.id)
        ];
        this.selectedMeetingId = meeting.id;
        this.transcript = [];
        this.noteMarkdown = "";
        this.savedNoteMarkdown = "";
        this.exports = [];
        this.transcriptionTasks = [];
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to import media";
      } finally {
        this.importing = false;
      }
    },
    async loadTranscript(meetingId: string) {
      this.error = null;
      try {
        this.transcript = await getMeetingTranscript(meetingId);
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to load transcript";
      }
    },
    async deleteMeeting(meetingId: string) {
      this.deletingMeetingId = meetingId;
      this.error = null;
      try {
        await deleteMeeting(meetingId);
        const wasSelected = this.selectedMeetingId === meetingId;
        this.meetings = this.meetings.filter((meeting) => meeting.id !== meetingId);

        if (wasSelected) {
          const nextMeeting = this.meetings[0] ?? null;
          if (nextMeeting) {
            await this.selectMeeting(nextMeeting.id);
          } else {
            this.clearSelectedMeeting();
          }
        }
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to delete meeting";
      } finally {
        this.deletingMeetingId = null;
      }
    },
    async runTranscription() {
      if (!this.selectedMeetingId) {
        return;
      }

      const meetingId = this.selectedMeetingId;
      this.transcribing = true;
      this.error = null;
      this.meetings = this.meetings.map((meeting) =>
        meeting.id === meetingId
          ? { ...meeting, status: "transcribing" }
          : meeting
      );
      try {
        const result = await startTranscriptionTask(meetingId);
        const updatedMeeting = result.meeting;
        this.meetings = this.meetings.map((meeting) =>
          meeting.id === updatedMeeting.id ? updatedMeeting : meeting
        );
        this.transcript = await getMeetingTranscript(updatedMeeting.id);
        this.transcriptionTasks = [
          result.task,
          ...this.transcriptionTasks.filter((task) => task.id !== result.task.id)
        ];
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Failed to transcribe media";
        try {
          this.transcriptionTasks = await getTranscriptionTasks(meetingId);
          this.meetings = await getMeetings();
        } finally {
          this.error = message;
        }
      } finally {
        this.transcribing = false;
      }
    },
    async loadNote(meetingId: string) {
      this.error = null;
      try {
        const note = await getMeetingNote(meetingId);
        this.noteMarkdown = note?.markdown ?? "";
        this.savedNoteMarkdown = note?.markdown ?? "";
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to load note";
      }
    },
    updateNoteDraft(markdown: string) {
      this.noteMarkdown = markdown;
    },
    async generateNote() {
      if (!this.selectedMeetingId) {
        return;
      }

      this.generatingNote = true;
      this.error = null;
      try {
        const note = await summarizeMeeting(this.selectedMeetingId);
        this.noteMarkdown = note.markdown;
        this.savedNoteMarkdown = note.markdown;
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to generate note";
      } finally {
        this.generatingNote = false;
      }
    },
    async saveNote() {
      if (!this.selectedMeetingId) {
        return;
      }

      this.savingNote = true;
      this.error = null;
      try {
        const note = await saveMeetingNote(this.selectedMeetingId, this.noteMarkdown);
        this.noteMarkdown = note.markdown;
        this.savedNoteMarkdown = note.markdown;
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to save note";
      } finally {
        this.savingNote = false;
      }
    },
    async renameSpeaker(currentSpeaker: string, newSpeaker: string) {
      if (!this.selectedMeetingId) {
        return;
      }

      this.renamingSpeaker = true;
      this.error = null;
      try {
        this.transcript = await renameSpeaker(
          this.selectedMeetingId,
          currentSpeaker,
          newSpeaker
        );
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to rename speaker";
      } finally {
        this.renamingSpeaker = false;
      }
    },
    async updateTranscriptSegment(segmentId: string, text: string) {
      if (!this.selectedMeetingId) {
        return;
      }

      this.updatingTranscriptSegmentId = segmentId;
      this.error = null;
      try {
        const updatedSegment = await patchTranscriptSegment(
          this.selectedMeetingId,
          segmentId,
          text
        );
        this.transcript = this.transcript.map((segment) =>
          segment.id === updatedSegment.id ? updatedSegment : segment
        );
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to update transcript";
      } finally {
        this.updatingTranscriptSegmentId = null;
      }
    },
    async loadExports(meetingId: string) {
      this.error = null;
      try {
        this.exports = await getMeetingExports(meetingId);
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to load exports";
      }
    },
    async loadTranscriptionTasks(meetingId: string) {
      this.error = null;
      try {
        this.transcriptionTasks = await getTranscriptionTasks(meetingId);
      } catch (error) {
        this.error =
          error instanceof Error ? error.message : "Failed to load transcription tasks";
      }
    },
    async retryLatestTranscriptionTask() {
      if (!this.selectedMeetingId || !this.latestTranscriptionTask) {
        return;
      }

      const meetingId = this.selectedMeetingId;
      const taskId = this.latestTranscriptionTask.id;
      this.retryingTranscription = true;
      this.error = null;
      try {
        const result = await retryTranscriptionTask(
          meetingId,
          taskId
        );
        this.transcriptionTasks = [
          result.task,
          ...this.transcriptionTasks.filter((task) => task.id !== result.task.id)
        ];
        this.meetings = this.meetings.map((meeting) =>
          meeting.id === result.meeting.id ? result.meeting : meeting
        );
        this.transcript = await getMeetingTranscript(result.meeting.id);
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Failed to retry transcription";
        try {
          this.transcriptionTasks = await getTranscriptionTasks(meetingId);
          this.meetings = await getMeetings();
        } finally {
          this.error = message;
        }
      } finally {
        this.retryingTranscription = false;
      }
    },
    async exportNote(format: ExportFormat) {
      if (!this.selectedMeetingId) {
        return;
      }

      this.exportingFormat = format;
      this.error = null;
      try {
        await saveMeetingNote(this.selectedMeetingId, this.noteMarkdown);
        this.savedNoteMarkdown = this.noteMarkdown;
        const exportRecord = await exportMeeting(this.selectedMeetingId, format);
        this.exports = [
          exportRecord,
          ...this.exports.filter((existingExport) => existingExport.id !== exportRecord.id)
        ];
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to export note";
      } finally {
        this.exportingFormat = null;
      }
    },
    async openLatestExportFolder() {
      const [latestExport] = this.exports;
      if (!latestExport) {
        return;
      }

      this.openingExportFolder = true;
      this.error = null;
      try {
        await openLocalPath(latestExport.folderPath);
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to open export folder";
      } finally {
        this.openingExportFolder = false;
      }
    }
  }
});
