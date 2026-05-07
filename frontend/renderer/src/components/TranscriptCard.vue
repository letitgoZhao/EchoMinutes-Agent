<script setup lang="ts">
import { computed, shallowRef, watch } from "vue";

import type { TranscriptSegment } from "../services/apiClient";
import { useI18nStore } from "../stores/i18n";

const props = defineProps<{
  segment: TranscriptSegment;
  saving: boolean;
}>();

const emit = defineEmits<{
  renameSpeaker: [payload: { currentSpeaker: string; newSpeaker: string }];
  updateSegment: [payload: { segmentId: string; text: string }];
}>();

const i18n = useI18nStore();
const speakerDraft = shallowRef(props.segment.speaker);
const textDraft = shallowRef(props.segment.text);

watch(
  () => props.segment.speaker,
  (speaker) => {
    speakerDraft.value = speaker;
  }
);

watch(
  () => props.segment.text,
  (text) => {
    textDraft.value = text;
  }
);

const hasTextChanges = computed(() => textDraft.value.trim() !== props.segment.text);

function formatTime(ms: number): string {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, "0");
  const seconds = (totalSeconds % 60).toString().padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function submitRename() {
  const nextSpeaker = speakerDraft.value.trim();
  if (!nextSpeaker || nextSpeaker === props.segment.speaker) {
    speakerDraft.value = props.segment.speaker;
    return;
  }

  emit("renameSpeaker", {
    currentSpeaker: props.segment.speaker,
    newSpeaker: nextSpeaker
  });
}

function saveText() {
  const nextText = textDraft.value.trim();
  if (!nextText || nextText === props.segment.text) {
    textDraft.value = props.segment.text;
    return;
  }

  emit("updateSegment", {
    segmentId: props.segment.id,
    text: nextText
  });
}

function resetText() {
  textDraft.value = props.segment.text;
}
</script>

<template>
  <article class="transcript-card">
    <header>
      <form class="speaker-rename" @submit.prevent="submitRename">
        <input
          v-model="speakerDraft"
          type="text"
          :aria-label="i18n.t('speakerNameLabel')"
        />
        <button type="submit">{{ i18n.t("renameSpeaker") }}</button>
      </form>
      <span class="transcript-timestamp">
        {{ formatTime(segment.startMs) }} - {{ formatTime(segment.endMs) }}
      </span>
    </header>
    <textarea
      v-model="textDraft"
      class="transcript-editor"
      :aria-label="i18n.t('transcriptEditorLabel')"
    />
    <div class="transcript-card-actions">
      <button type="button" :disabled="!hasTextChanges || saving" @click="saveText">
        {{ saving ? i18n.t("savingTranscript") : i18n.t("saveTranscript") }}
      </button>
      <button type="button" :disabled="!hasTextChanges || saving" @click="resetText">
        {{ i18n.t("resetTranscript") }}
      </button>
    </div>
    <small v-if="segment.confidence < 0.9">{{ i18n.t("lowConfidence") }}</small>
  </article>
</template>
