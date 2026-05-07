<script setup lang="ts">
import type { Meeting } from "../services/apiClient";
import { useI18nStore } from "../stores/i18n";

defineProps<{
  meetings: Meeting[];
  selectedMeetingId: string | null;
  loading: boolean;
  importing: boolean;
  error: string | null;
}>();

const emit = defineEmits<{
  importMedia: [];
  selectMeeting: [meetingId: string];
}>();

const i18n = useI18nStore();

function getStatusLabel(status: string): string {
  if (status === "failed") {
    return i18n.t("statusFailed");
  }
  if (status === "transcribed") {
    return i18n.t("statusTranscribed");
  }
  if (status === "transcribing") {
    return i18n.t("statusTranscribing");
  }
  return i18n.t("statusImported");
}
</script>

<template>
  <aside class="sidebar">
    <header class="library-header">
      <section>
        <h2>{{ i18n.t("meetingLibraryTitle") }}</h2>
        <p class="muted-copy">{{ i18n.t("p1ImportDescription") }}</p>
      </section>
      <button type="button" :disabled="importing" @click="emit('importMedia')">
        {{ importing ? i18n.t("importingMedia") : i18n.t("importMedia") }}
      </button>
    </header>

    <section class="library-scroll-area">
      <p v-if="error" class="error-copy">{{ error }}</p>

      <ol class="meeting-list">
        <li v-if="loading" class="muted-copy">{{ i18n.t("loadingMeetings") }}</li>
        <li v-else-if="meetings.length === 0" class="muted-copy">
          {{ i18n.t("noMeetings") }}
        </li>
        <template v-else>
          <li v-for="meeting in meetings" :key="meeting.id">
            <button
              type="button"
              class="meeting-list-item"
              :class="{ active: meeting.id === selectedMeetingId }"
              @click="emit('selectMeeting', meeting.id)"
            >
              <strong class="meeting-list-item-title">{{ meeting.title }}</strong>
              <span class="meeting-list-item-meta">{{ meeting.sourceFileName }}</span>
              <small>{{ getStatusLabel(meeting.status) }}</small>
            </button>
          </li>
        </template>
      </ol>
    </section>
  </aside>
</template>
