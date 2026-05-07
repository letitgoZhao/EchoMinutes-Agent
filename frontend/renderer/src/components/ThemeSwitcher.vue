<script setup lang="ts">
import { useI18nStore, type TranslationKey } from "../stores/i18n";
import { themeOptions, useThemeStore, type ThemeId } from "../stores/theme";

const i18n = useI18nStore();
const themeStore = useThemeStore();

function selectTheme(theme: ThemeId) {
  themeStore.setTheme(theme);
}
</script>

<template>
  <section class="theme-switcher" :aria-label="i18n.t('themeSwitcherLabel')">
    <button
      v-for="theme in themeOptions"
      :key="theme.id"
      type="button"
      class="theme-option"
      :class="{ active: themeStore.theme === theme.id }"
      :data-theme-option="theme.id"
      :title="i18n.t(theme.labelKey as TranslationKey)"
      :aria-pressed="themeStore.theme === theme.id"
      @click="selectTheme(theme.id)"
    >
      <span class="theme-swatch" aria-hidden="true"></span>
      <span class="theme-label">{{ i18n.t(theme.labelKey as TranslationKey) }}</span>
    </button>
  </section>
</template>
