<script setup lang="ts">
import { computed, onMounted, onUnmounted, shallowRef } from "vue";

import { getHealth, type HealthResponse } from "../services/apiClient";
import { useI18nStore } from "../stores/i18n";

const BACKEND_RETRY_DELAY_MS = 2000;

const health = shallowRef<HealthResponse | null>(null);
const loading = shallowRef(false);
const error = shallowRef<string | null>(null);
const i18n = useI18nStore();
let retryTimer: number | null = null;

const statusText = computed(() => {
  if (loading.value) {
    return i18n.t("backendChecking");
  }

  if (health.value?.ok) {
    return i18n.t("backendOnline", { version: health.value.version });
  }

  return i18n.t("backendOffline");
});

function clearRetryTimer() {
  if (retryTimer === null) {
    return;
  }

  window.clearTimeout(retryTimer);
  retryTimer = null;
}

function scheduleRetry() {
  if (retryTimer !== null || health.value?.ok) {
    return;
  }

  retryTimer = window.setTimeout(() => {
    retryTimer = null;
    void refreshHealth({ retryOnFailure: true });
  }, BACKEND_RETRY_DELAY_MS);
}

async function refreshHealth(options: { retryOnFailure?: boolean } = {}) {
  if (loading.value) {
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    health.value = await getHealth();
    clearRetryTimer();
  } catch (caught) {
    health.value = null;
    error.value = caught instanceof Error ? caught.message : "Backend unavailable";
    if (options.retryOnFailure) {
      scheduleRetry();
    }
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void refreshHealth({ retryOnFailure: true });
});

onUnmounted(() => {
  clearRetryTimer();
});
</script>

<template>
  <button
    class="status-badge"
    :class="{ ok: health?.ok, error: error }"
    type="button"
    @click="refreshHealth({ retryOnFailure: true })"
  >
    <span class="status-dot" />
    <span>{{ statusText }}</span>
  </button>
</template>
