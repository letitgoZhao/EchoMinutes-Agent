<script setup lang="ts">
import { computed } from "vue";

import { useI18nStore, type LanguageCode } from "../stores/i18n";

const i18n = useI18nStore();

const languages: Array<{ code: LanguageCode; labelKey: "languageChinese" | "languageEnglish" }> = [
  { code: "zh", labelKey: "languageChinese" },
  { code: "en", labelKey: "languageEnglish" }
];

const label = computed(() => i18n.t("languageToggleLabel"));
</script>

<template>
  <div class="language-toggle" role="group" :aria-label="label">
    <button
      v-for="language in languages"
      :key="language.code"
      type="button"
      :class="{ active: i18n.language === language.code }"
      :aria-pressed="i18n.language === language.code"
      @click="i18n.setLanguage(language.code)"
    >
      {{ i18n.t(language.labelKey) }}
    </button>
  </div>
</template>
