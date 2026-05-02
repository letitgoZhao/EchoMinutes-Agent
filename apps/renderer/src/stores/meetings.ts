import { defineStore } from "pinia";

import { createMeeting, getMeetings, type Meeting } from "../services/apiClient";
import { selectMediaFile } from "../services/desktopClient";

interface MeetingsState {
  meetings: Meeting[];
  selectedMeetingId: string | null;
  loading: boolean;
  importing: boolean;
  error: string | null;
}

export const useMeetingsStore = defineStore("meetings", {
  state: (): MeetingsState => ({
    meetings: [],
    selectedMeetingId: null,
    loading: false,
    importing: false,
    error: null
  }),
  getters: {
    selectedMeeting(state): Meeting | null {
      return state.meetings.find((meeting) => meeting.id === state.selectedMeetingId) ?? null;
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
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to load meetings";
      } finally {
        this.loading = false;
      }
    },
    selectMeeting(meetingId: string) {
      this.selectedMeetingId = meetingId;
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
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to import media";
      } finally {
        this.importing = false;
      }
    }
  }
});
