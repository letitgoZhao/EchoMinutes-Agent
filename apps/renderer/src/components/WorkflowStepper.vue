<script setup lang="ts">
import { computed } from "vue";

import { useI18nStore } from "../stores/i18n";

const i18n = useI18nStore();

const steps = computed(() => [
  i18n.t("workflowImport"),
  i18n.t("workflowTranscribe"),
  i18n.t("workflowOrganize"),
  i18n.t("workflowNotes"),
  i18n.t("workflowReview"),
  i18n.t("workflowExport")
]);
</script>

<template>
  <ol class="workflow-stepper">
    <li
      v-for="(step, index) in steps"
      :key="step"
      :class="{ active: index === 0, muted: index > 0 }"
    >
      <span>{{ index + 1 }}</span>
      {{ step }}
    </li>
  </ol>
</template>
