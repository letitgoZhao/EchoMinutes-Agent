<script setup lang="ts">
import { onMounted } from "vue";
import { RouterLink, RouterView } from "vue-router";

import BackendStatusBadge from "../components/BackendStatusBadge.vue";
import LanguageToggle from "../components/LanguageToggle.vue";
import ThemeSwitcher from "../components/ThemeSwitcher.vue";
import { useI18nStore } from "../stores/i18n";
import { useThemeStore } from "../stores/theme";

const i18n = useI18nStore();
const themeStore = useThemeStore();

onMounted(() => {
  themeStore.applyCurrentTheme();
});
</script>

<template>
  <main class="app-shell">
    <header class="topbar">
      <section>
        <p class="eyebrow">{{ i18n.t("appEyebrow") }}</p>
        <h1>EchoMinutes Agent</h1>
      </section>

      <nav class="nav-tabs" :aria-label="i18n.t('primaryNavigation')">
        <RouterLink to="/">{{ i18n.t("workspaceNav") }}</RouterLink>
        <RouterLink to="/settings">{{ i18n.t("settingsNav") }}</RouterLink>
      </nav>

      <LanguageToggle />
      <ThemeSwitcher />
      <BackendStatusBadge />
    </header>

    <RouterView />
  </main>
</template>
