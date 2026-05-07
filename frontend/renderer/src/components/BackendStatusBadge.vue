<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { getHealth, type HealthResponse } from "../services/apiClient";
import { useI18nStore } from "../stores/i18n";

const health = ref<HealthResponse | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);
const i18n = useI18nStore();

const statusText = computed(() => {
  if (loading.value) {
    return i18n.t("backendChecking");
  }

  if (health.value?.ok) {
    return i18n.t("backendOnline", { version: health.value.version });
  }

  return i18n.t("backendOffline");
});

async function refreshHealth() {
  loading.value = true;
  error.value = null;

  try {
    health.value = await getHealth();
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : "Backend unavailable";
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void refreshHealth();
});
</script>

<template>
  <button
    class="status-badge"
    :class="{ ok: health?.ok, error: error }"
    type="button"
    @click="refreshHealth"
  >
    <span class="status-dot" />
    <span>{{ statusText }}</span>
  </button>
</template>
