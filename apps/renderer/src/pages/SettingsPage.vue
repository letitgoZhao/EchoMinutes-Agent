<script setup lang="ts">
import { onMounted } from "vue";

import { useI18nStore } from "../stores/i18n";
import { useSettingsStore } from "../stores/settings";

const settingsStore = useSettingsStore();
const i18n = useI18nStore();

onMounted(() => {
  void settingsStore.loadSettings();
});
</script>

<template>
  <section class="settings-page">
    <header>
      <h2>{{ i18n.t("settingsTitle") }}</h2>
      <button type="button" @click="settingsStore.loadSettings">
        {{ i18n.t("refresh") }}
      </button>
    </header>

    <p class="muted-copy">
      {{ i18n.t("settingsDescription") }}
    </p>

    <p v-if="settingsStore.error" class="error-copy">{{ settingsStore.error }}</p>
    <dl v-else-if="settingsStore.settings" class="settings-grid">
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
  </section>
</template>
