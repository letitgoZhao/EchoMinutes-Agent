<script setup lang="ts">
import type { TranscriptSegment } from "../services/apiClient";
import { useI18nStore } from "../stores/i18n";

defineProps<{
  segment: TranscriptSegment;
}>();

const i18n = useI18nStore();

function formatTime(ms: number): string {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, "0");
  const seconds = (totalSeconds % 60).toString().padStart(2, "0");
  return `${minutes}:${seconds}`;
}
</script>

<template>
  <article class="transcript-card">
    <header>
      <strong>{{ segment.speaker }}</strong>
      <span>{{ formatTime(segment.startMs) }} - {{ formatTime(segment.endMs) }}</span>
    </header>
    <p>{{ segment.text }}</p>
    <small v-if="segment.confidence < 0.9">{{ i18n.t("lowConfidence") }}</small>
  </article>
</template>
