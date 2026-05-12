<script setup lang="ts">
import { onMounted, reactive, watch } from "vue";

import { useI18nStore } from "../stores/i18n";
import { useSettingsStore } from "../stores/settings";

const settingsStore = useSettingsStore();
const i18n = useI18nStore();

const form = reactive({
  workspaceDir: "",
  dashscopeApiKey: "",
  dashscopeBaseUrl: "",
  dashscopeModel: "",
  dashscopeAsrBaseUrl: "",
  dashscopeAsrModel: "",
  dashscopeAsrSpeakerCount: 0
});

watch(
  () => settingsStore.settings,
  (settings) => {
    if (!settings) {
      return;
    }

    form.workspaceDir = settings.workspaceDir;
    form.dashscopeBaseUrl = settings.dashscopeBaseUrl;
    form.dashscopeModel = settings.dashscopeModel;
    form.dashscopeAsrBaseUrl = settings.dashscopeAsrBaseUrl;
    form.dashscopeAsrModel = settings.dashscopeAsrModel;
    form.dashscopeAsrSpeakerCount = settings.dashscopeAsrSpeakerCount;
  },
  { immediate: true }
);

onMounted(() => {
  void settingsStore.loadDiagnostics();
});

async function saveProviderSettings() {
  await settingsStore.saveSettings({
    workspaceDir: form.workspaceDir,
    dashscopeApiKey: form.dashscopeApiKey.trim() || undefined,
    dashscopeBaseUrl: form.dashscopeBaseUrl,
    dashscopeModel: form.dashscopeModel,
    dashscopeAsrBaseUrl: form.dashscopeAsrBaseUrl,
    dashscopeAsrModel: form.dashscopeAsrModel,
    dashscopeAsrSpeakerCount: form.dashscopeAsrSpeakerCount
  });
  form.dashscopeApiKey = "";
}

async function clearApiKey() {
  await settingsStore.saveSettings({
    clearDashscopeApiKey: true
  });
  form.dashscopeApiKey = "";
}

async function testAllProviders() {
  await Promise.all([settingsStore.testLlmProvider(), settingsStore.testAsrProvider()]);
}
</script>

<template>
  <section class="settings-page">
    <header class="settings-page-header">
      <section>
        <h2>{{ i18n.t("settingsTitle") }}</h2>
        <p class="muted-copy">
          {{ i18n.t("settingsDescription") }}
        </p>
      </section>
      <button type="button" @click="settingsStore.loadDiagnostics">
        {{ i18n.t("refresh") }}
      </button>
    </header>

    <p v-if="settingsStore.error" class="error-copy">{{ settingsStore.error }}</p>
    <p v-if="settingsStore.savedMessage" class="success-copy">
      {{ i18n.t("settingsSaved") }}
    </p>

    <section class="settings-readiness-panel">
      <header>
        <section>
          <h3>{{ i18n.t("providerReadiness") }}</h3>
          <p class="muted-copy">{{ i18n.t("providerReadinessDescription") }}</p>
        </section>
        <button
          type="button"
          :disabled="settingsStore.testingLlm || settingsStore.testingAsr"
          @click="testAllProviders"
        >
          {{
            settingsStore.testingLlm || settingsStore.testingAsr
              ? i18n.t("testingProvider")
              : i18n.t("testAllProviders")
          }}
        </button>
      </header>

      <div class="provider-tests">
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
          <p v-else class="muted-copy">{{ i18n.t("providerTestPending") }}</p>
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
          <p v-else class="muted-copy">{{ i18n.t("providerTestPending") }}</p>
        </article>
      </div>
    </section>

    <form v-if="settingsStore.settings" class="provider-config" @submit.prevent="saveProviderSettings">
      <header>
        <section>
          <h3>{{ i18n.t("providerConfigTitle") }}</h3>
          <p class="muted-copy">{{ i18n.t("providerConfigDescription") }}</p>
        </section>
      </header>

      <label>
        <span>{{ i18n.t("workspace") }}</span>
        <input v-model="form.workspaceDir" autocomplete="off" />
      </label>
      <label>
        <span>{{ i18n.t("dashscopeApiKey") }}</span>
        <input
          v-model="form.dashscopeApiKey"
          autocomplete="off"
          :placeholder="i18n.t('apiKeyPlaceholder')"
          type="password"
        />
      </label>
      <label>
        <span>{{ i18n.t("dashscopeBaseUrl") }}</span>
        <input v-model="form.dashscopeBaseUrl" autocomplete="off" />
      </label>
      <label>
        <span>{{ i18n.t("dashscopeModel") }}</span>
        <input v-model="form.dashscopeModel" autocomplete="off" />
      </label>
      <label>
        <span>{{ i18n.t("dashscopeAsrBaseUrl") }}</span>
        <input v-model="form.dashscopeAsrBaseUrl" autocomplete="off" />
      </label>
      <label>
        <span>{{ i18n.t("dashscopeAsrModel") }}</span>
        <input v-model="form.dashscopeAsrModel" autocomplete="off" />
      </label>
      <label>
        <span>{{ i18n.t("dashscopeAsrSpeakerCount") }}</span>
        <input v-model.number="form.dashscopeAsrSpeakerCount" min="0" step="1" type="number" />
      </label>

      <footer class="settings-actions">
        <button type="submit" :disabled="settingsStore.saving">
          {{ settingsStore.saving ? i18n.t("savingSettings") : i18n.t("saveSettings") }}
        </button>
        <button
          type="button"
          :disabled="settingsStore.saving || !settingsStore.settings.hasDashscopeApiKey"
          @click="clearApiKey"
        >
          {{ i18n.t("clearApiKey") }}
        </button>
      </footer>
    </form>

    <p v-else class="muted-copy">{{ i18n.t("loadingSettings") }}</p>

    <section class="settings-runtime-layout">
      <section v-if="settingsStore.settings" class="runtime-panel">
        <header>
          <h3>{{ i18n.t("hostRuntimeTitle") }}</h3>
          <p class="muted-copy">{{ i18n.t("hostRuntimeDescription") }}</p>
        </header>
        <dl class="settings-grid">
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
          <dt>{{ i18n.t("dashscopeAsrSpeakerCount") }}</dt>
          <dd>{{ settingsStore.settings.dashscopeAsrSpeakerCount || i18n.t("auto") }}</dd>
          <dt>{{ i18n.t("apiKeyConfigured") }}</dt>
          <dd>
            {{ settingsStore.settings.hasDashscopeApiKey ? i18n.t("yes") : i18n.t("no") }}
          </dd>
          <dt>{{ i18n.t("ffmpegAvailable") }}</dt>
          <dd>{{ settingsStore.settings.ffmpegAvailable ? i18n.t("yes") : i18n.t("no") }}</dd>
          <dt>{{ i18n.t("ffmpegPath") }}</dt>
          <dd>{{ settingsStore.settings.ffmpegPath ?? i18n.t("notConfigured") }}</dd>
        </dl>
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
  </section>
</template>
