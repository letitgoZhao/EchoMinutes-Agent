<script setup lang="ts">
import { computed, onMounted } from "vue";

import MeetingLibrary from "../components/MeetingLibrary.vue";
import NotePanel from "../components/NotePanel.vue";
import TranscriptCard from "../components/TranscriptCard.vue";
import WorkflowStepper from "../components/WorkflowStepper.vue";
import { useI18nStore } from "../stores/i18n";
import { useMeetingsStore } from "../stores/meetings";

const i18n = useI18nStore();
const meetingsStore = useMeetingsStore();
const currentMeeting = computed(() => meetingsStore.selectedMeeting);
const segments = computed(() => meetingsStore.transcript);
const latestTask = computed(() => meetingsStore.latestTranscriptionTask);
const noteDraft = computed({
  get: () => meetingsStore.noteMarkdown,
  set: (markdown: string) => meetingsStore.updateNoteDraft(markdown)
});

onMounted(() => {
  void meetingsStore.loadMeetings();
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
      <header class="panel-header">
        <section class="panel-heading">
          <h2>{{ i18n.t("transcriptTitle") }}</h2>
          <p v-if="currentMeeting" class="muted-copy current-meeting-copy">
            {{ i18n.t("currentMeeting") }}: {{ currentMeeting.title }}
          </p>
        </section>
        <button
          v-if="currentMeeting"
          type="button"
          :disabled="meetingsStore.transcribing"
          @click="meetingsStore.runMockTranscription"
        >
          {{
            meetingsStore.transcribing
              ? i18n.t("transcribingMedia")
              : i18n.t("runMockTranscription")
          }}
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

      <article v-if="latestTask" class="task-status-panel">
        <section>
          <strong>{{ i18n.t("latestTranscriptionTask") }}</strong>
          <span>{{ i18n.t("taskStatus") }}: {{ latestTask.status }}</span>
          <span>{{ i18n.t("taskAttempts") }}: {{ latestTask.attemptCount }}</span>
          <p v-if="latestTask.errorMessage" class="error-copy">
            {{ latestTask.errorMessage }}
          </p>
        </section>
        <button
          v-if="latestTask.retryable"
          type="button"
          :disabled="meetingsStore.retryingTranscription"
          @click="meetingsStore.retryLatestTranscriptionTask"
        >
          {{
            meetingsStore.retryingTranscription
              ? i18n.t("retryingTask")
              : i18n.t("retryTask")
          }}
        </button>
      </article>

      <p v-if="meetingsStore.error" class="error-copy">
        {{ meetingsStore.error }}
      </p>
      <p v-else-if="currentMeeting && segments.length === 0" class="muted-copy">
        {{ i18n.t("noTranscript") }}
      </p>
      <TranscriptCard
        v-for="segment in segments"
        :key="segment.id"
        :segment="segment"
        :saving="meetingsStore.updatingTranscriptSegmentId === segment.id"
        @rename-speaker="meetingsStore.renameSpeaker($event.currentSpeaker, $event.newSpeaker)"
        @update-segment="meetingsStore.updateTranscriptSegment($event.segmentId, $event.text)"
      />
    </section>

    <NotePanel
      v-model="noteDraft"
      :can-export="Boolean(currentMeeting && meetingsStore.noteMarkdown.trim())"
      :can-generate="Boolean(currentMeeting && segments.length > 0)"
      :can-save="Boolean(currentMeeting)"
      :export-history="meetingsStore.exports"
      :exporting-format="meetingsStore.exportingFormat"
      :generating="meetingsStore.generatingNote"
      :opening-export-folder="meetingsStore.openingExportFolder"
      :placeholder="i18n.t('notePlaceholder')"
      :saving="meetingsStore.savingNote"
      @export-note="meetingsStore.exportNote"
      @open-export-folder="meetingsStore.openLatestExportFolder"
      @regenerate="meetingsStore.generateNote"
      @save="meetingsStore.saveNote"
    />
  </section>
</template>
