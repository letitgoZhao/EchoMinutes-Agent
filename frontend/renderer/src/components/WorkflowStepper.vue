<script setup lang="ts">
import { computed } from "vue";

import type { Meeting, ProcessingTask } from "../services/apiClient";
import { useI18nStore, type TranslationKey } from "../stores/i18n";

type WorkflowStepState = "idle" | "active" | "complete" | "failed";

interface WorkflowStep {
  key: string;
  labelKey: TranslationKey;
  state: WorkflowStepState;
}

const props = defineProps<{
  exporting: boolean;
  exportCount: number;
  generatingNote: boolean;
  hasNote: boolean;
  importing: boolean;
  latestTask: ProcessingTask | null;
  meeting: Meeting | null;
  noteDirty: boolean;
  transcriptCount: number;
  transcribing: boolean;
}>();

const i18n = useI18nStore();

const importState = computed<WorkflowStepState>(() => {
  if (props.importing) {
    return "active";
  }
  return props.meeting ? "complete" : "idle";
});

const transcriptionState = computed<WorkflowStepState>(() => {
  if (!props.meeting) {
    return "idle";
  }
  if (props.latestTask?.status === "failed" || props.meeting.status === "failed") {
    return "failed";
  }
  if (
    props.transcribing ||
    props.latestTask?.status === "running" ||
    props.latestTask?.status === "queued" ||
    props.meeting.status === "transcribing"
  ) {
    return "active";
  }
  return props.transcriptCount > 0 || props.meeting.status === "transcribed"
    ? "complete"
    : "idle";
});

const organizeState = computed<WorkflowStepState>(() => {
  if (transcriptionState.value === "failed") {
    return "failed";
  }
  if (transcriptionState.value === "active") {
    return "idle";
  }
  return props.transcriptCount > 0 ? "complete" : "idle";
});

const noteState = computed<WorkflowStepState>(() => {
  if (!props.meeting || props.transcriptCount === 0) {
    return "idle";
  }
  if (props.generatingNote) {
    return "active";
  }
  return props.hasNote ? "complete" : "idle";
});

const reviewState = computed<WorkflowStepState>(() => {
  if (!props.hasNote) {
    return "idle";
  }
  return props.noteDirty ? "active" : "complete";
});

const exportState = computed<WorkflowStepState>(() => {
  if (!props.hasNote) {
    return "idle";
  }
  if (props.exporting) {
    return "active";
  }
  return props.exportCount > 0 ? "complete" : "idle";
});

const steps = computed<WorkflowStep[]>(() => [
  { key: "import", labelKey: "workflowImport", state: importState.value },
  { key: "transcribe", labelKey: "workflowTranscribe", state: transcriptionState.value },
  { key: "organize", labelKey: "workflowOrganize", state: organizeState.value },
  { key: "notes", labelKey: "workflowNotes", state: noteState.value },
  { key: "review", labelKey: "workflowReview", state: reviewState.value },
  { key: "export", labelKey: "workflowExport", state: exportState.value }
]);

function getStatusLabel(state: WorkflowStepState): string {
  if (state === "active") {
    return i18n.t("workflowStatusActive");
  }
  if (state === "complete") {
    return i18n.t("workflowStatusComplete");
  }
  if (state === "failed") {
    return i18n.t("workflowStatusFailed");
  }
  return i18n.t("workflowStatusIdle");
}
</script>

<template>
  <ol class="workflow-stepper" aria-label="Meeting workflow">
    <li
      v-for="(step, index) in steps"
      :key="step.key"
      :class="[`workflow-step-${step.state}`]"
    >
      <span class="workflow-step-index">{{ index + 1 }}</span>
      <strong>{{ i18n.t(step.labelKey) }}</strong>
      <small>{{ getStatusLabel(step.state) }}</small>
    </li>
  </ol>
</template>
