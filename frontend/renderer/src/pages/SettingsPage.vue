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
      <dt>{{ i18n.t("transcriptionProvider") }}</dt>
      <dd>{{ settingsStore.settings.transcriptionProvider }}</dd>
      <dt>{{ i18n.t("asrReady") }}</dt>
      <dd>{{ settingsStore.settings.asrReady ? i18n.t("yes") : i18n.t("no") }}</dd>
      <dt>{{ i18n.t("dashscopeBaseUrl") }}</dt>
      <dd>{{ settingsStore.settings.dashscopeBaseUrl }}</dd>
      <dt>{{ i18n.t("dashscopeModel") }}</dt>
      <dd>{{ settingsStore.settings.dashscopeModel }}</dd>
      <dt>{{ i18n.t("dashscopeAsrBaseUrl") }}</dt>
      <dd>{{ settingsStore.settings.dashscopeAsrBaseUrl }}</dd>
      <dt>{{ i18n.t("dashscopeAsrModel") }}</dt>
      <dd>{{ settingsStore.settings.dashscopeAsrModel }}</dd>
      <dt>{{ i18n.t("apiKeyConfigured") }}</dt>
      <dd>
        {{ settingsStore.settings.hasDashscopeApiKey ? i18n.t("yes") : i18n.t("no") }}
      </dd>
      <dt>{{ i18n.t("ffmpegAvailable") }}</dt>
      <dd>{{ settingsStore.settings.ffmpegAvailable ? i18n.t("yes") : i18n.t("no") }}</dd>
      <dt>{{ i18n.t("ffmpegPath") }}</dt>
      <dd>{{ settingsStore.settings.ffmpegPath ?? i18n.t("notConfigured") }}</dd>
    </dl>
    <p v-else>{{ i18n.t("loadingSettings") }}</p>

    <section class="provider-tests">
      <article>
        <header>
          <h3>{{ i18n.t("llmReadiness") }}</h3>
          <button
            type="button"
            :disabled="settingsStore.testingLlm"
            @click="settingsStore.testLlmProvider"
          >
            {{ settingsStore.testingLlm ? i18n.t("testingProvider") : i18n.t("testProvider") }}
          </button>
        </header>
        <p
          v-if="settingsStore.llmTest"
          :class="settingsStore.llmTest.ok ? 'success-copy' : 'error-copy'"
        >
          {{ settingsStore.llmTest.message }}
        </p>
      </article>
      <article>
        <header>
          <h3>{{ i18n.t("asrReadiness") }}</h3>
          <button
            type="button"
            :disabled="settingsStore.testingAsr"
            @click="settingsStore.testAsrProvider"
          >
            {{ settingsStore.testingAsr ? i18n.t("testingProvider") : i18n.t("testProvider") }}
          </button>
        </header>
        <p
          v-if="settingsStore.asrTest"
          :class="settingsStore.asrTest.ok ? 'success-copy' : 'error-copy'"
        >
          {{ settingsStore.asrTest.message }}
        </p>
      </article>
    </section>

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
