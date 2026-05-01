<script setup lang="ts">
import { useI18nStore } from "../stores/i18n";

defineProps<{
  markdown: string;
}>();

const i18n = useI18nStore();
</script>

<template>
  <section class="note-panel">
    <header>
      <h2>{{ i18n.t("noteTitle") }}</h2>
      <button type="button">{{ i18n.t("regenerate") }}</button>
    </header>
    <textarea :value="markdown" :aria-label="i18n.t('noteEditorLabel')" />
  </section>
</template>
