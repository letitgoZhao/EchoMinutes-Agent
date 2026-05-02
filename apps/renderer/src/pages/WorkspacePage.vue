<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import MeetingLibrary from "../components/MeetingLibrary.vue";
import NotePanel from "../components/NotePanel.vue";
import TranscriptCard from "../components/TranscriptCard.vue";
import WorkflowStepper from "../components/WorkflowStepper.vue";
import {
  getMockNote,
  getMockTranscript,
  type TranscriptSegment
} from "../services/apiClient";
import { useI18nStore } from "../stores/i18n";
import { useMeetingsStore } from "../stores/meetings";

const segments = ref<TranscriptSegment[]>([]);
const i18n = useI18nStore();
const meetingsStore = useMeetingsStore();
const noteMarkdown = ref(i18n.t("notePlaceholder"));
const error = ref<string | null>(null);
const currentMeeting = computed(() => meetingsStore.selectedMeeting);

async function loadMockWorkspace() {
  error.value = null;

  try {
    const [mockSegments, mockNote] = await Promise.all([
      getMockTranscript(),
      getMockNote()
    ]);
    segments.value = mockSegments;
    noteMarkdown.value = mockNote.markdown;
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : i18n.t("mockWorkspaceLoadError");
  }
}

onMounted(() => {
  void meetingsStore.loadMeetings();
  void loadMockWorkspace();
});
</script>

<template>
  <section class="workspace-layout">
    <MeetingLibrary
      :meetings="meetingsStore.meetings"
      :selected-meeting-id="meetingsStore.selectedMeetingId"
      :loading="meetingsStore.loading"
      :importing="meetingsStore.importing"
      :error="meetingsStore.error"
      @import-media="meetingsStore.importMedia"
      @select-meeting="meetingsStore.selectMeeting"
    />

    <section class="transcript-panel">
      <header>
        <section>
          <h2>{{ i18n.t("transcriptTitle") }}</h2>
          <p v-if="currentMeeting" class="muted-copy">
            {{ i18n.t("currentMeeting") }}: {{ currentMeeting.title }}
          </p>
        </section>
        <button type="button" @click="loadMockWorkspace">
          {{ i18n.t("reloadMockData") }}
        </button>
      </header>

      <WorkflowStepper />

      <article v-if="currentMeeting" class="meeting-summary">
        <dl>
          <dt>{{ i18n.t("sourceMedia") }}</dt>
          <dd>{{ currentMeeting.sourceFileName }}</dd>
          <dt>{{ i18n.t("copiedMedia") }}</dt>
          <dd>{{ currentMeeting.workspaceMediaPath }}</dd>
        </dl>
        <p class="muted-copy">{{ i18n.t("transcriptPending") }}</p>
      </article>

      <p v-if="error" class="error-copy">{{ error }}</p>
      <TranscriptCard
        v-for="segment in segments"
        :key="segment.id"
        :segment="segment"
      />
    </section>

    <NotePanel :markdown="noteMarkdown" />
  </section>
</template>
