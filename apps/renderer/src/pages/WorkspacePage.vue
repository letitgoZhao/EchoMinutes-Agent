<script setup lang="ts">
import { onMounted, ref } from "vue";

import NotePanel from "../components/NotePanel.vue";
import TranscriptCard from "../components/TranscriptCard.vue";
import WorkflowStepper from "../components/WorkflowStepper.vue";
import {
  getMockNote,
  getMockTranscript,
  type TranscriptSegment
} from "../services/apiClient";
import { useI18nStore } from "../stores/i18n";

const segments = ref<TranscriptSegment[]>([]);
const i18n = useI18nStore();
const noteMarkdown = ref(i18n.t("notePlaceholder"));
const error = ref<string | null>(null);

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
  void loadMockWorkspace();
});
</script>

<template>
  <section class="workspace-layout">
    <aside class="sidebar">
      <h2>{{ i18n.t("meetingLibraryTitle") }}</h2>
      <p class="muted-copy">{{ i18n.t("mockWorkspaceDescription") }}</p>
      <WorkflowStepper />
      <button type="button" disabled>{{ i18n.t("importMedia") }}</button>
    </aside>

    <section class="transcript-panel">
      <header>
        <h2>{{ i18n.t("transcriptTitle") }}</h2>
        <button type="button" @click="loadMockWorkspace">
          {{ i18n.t("reloadMockData") }}
        </button>
      </header>
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
