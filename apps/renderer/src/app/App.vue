<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";

import BackendStatusBadge from "../components/BackendStatusBadge.vue";
import LanguageToggle from "../components/LanguageToggle.vue";
import { useI18nStore } from "../stores/i18n";

const i18n = useI18nStore();
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
      <BackendStatusBadge />
    </header>

    <RouterView />
  </main>
</template>
