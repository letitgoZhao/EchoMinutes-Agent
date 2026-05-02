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
            <strong>{{ meeting.title }}</strong>
            <span>{{ meeting.sourceFileName }}</span>
            <small>{{ i18n.t("statusImported") }}</small>
          </button>
        </li>
      </template>
    </ol>
  </aside>
</template>
