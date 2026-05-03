<script setup lang="ts">
import { onMounted } from "vue";

import { useI18nStore } from "../stores/i18n";
import { useSettingsStore } from "../stores/settings";

const settingsStore = useSettingsStore();
const i18n = useI18nStore();

onMounted(() => {
  void settingsStore.loadDiagnostics();
});
</script>

<template>
  <section class="settings-page">
    <header>
      <h2>{{ i18n.t("settingsTitle") }}</h2>
      <button type="button" @click="settingsStore.loadDiagnostics">
        {{ i18n.t("refresh") }}
      </button>
    </header>

    <p class="muted-copy">
      {{ i18n.t("settingsDescription") }}
    </p>

    <p v-if="settingsStore.error" class="error-copy">{{ settingsStore.error }}</p>
    <dl v-if="settingsStore.settings" class="settings-grid">
      <dt>{{ i18n.t("apiHost") }}</dt>
      <dd>{{ settingsStore.settings.apiHost }}</dd>
      <dt>{{ i18n.t("apiPort") }}</dt>
      <dd>{{ settingsStore.settings.apiPort }}</dd>
      <dt>{{ i18n.t("workspace") }}</dt>
      <dd>{{ settingsStore.settings.workspaceDir }}</dd>
      <dt>{{ i18n.t("dashscopeBaseUrl") }}</dt>
      <dd>{{ settingsStore.settings.dashscopeBaseUrl }}</dd>
      <dt>{{ i18n.t("dashscopeModel") }}</dt>
      <dd>{{ settingsStore.settings.dashscopeModel }}</dd>
      <dt>{{ i18n.t("apiKeyConfigured") }}</dt>
      <dd>
        {{ settingsStore.settings.hasDashscopeApiKey ? i18n.t("yes") : i18n.t("no") }}
      </dd>
    </dl>
    <p v-else>{{ i18n.t("loadingSettings") }}</p>

    <section class="logs-panel">
      <header class="logs-panel-header">
        <section>
          <h3>{{ i18n.t("recentLogsTitle") }}</h3>
          <p class="muted-copy">{{ i18n.t("recentLogsDescription") }}</p>
        </section>
      </header>

      <p v-if="settingsStore.logsLoading" class="muted-copy">
        {{ i18n.t("loadingRecentLogs") }}
      </p>
      <p v-else-if="settingsStore.logs.length === 0" class="muted-copy">
        {{ i18n.t("noRecentLogs") }}
      </p>
      <ol v-else class="logs-list">
        <li v-for="entry in settingsStore.logs" :key="`${entry.timestamp}-${entry.message}`">
          <span class="log-meta">{{ entry.timestamp }} | {{ entry.level }}</span>
          <code>{{ entry.message }}</code>
        </li>
      </ol>
    </section>
  </section>
</template>
