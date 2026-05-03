<script setup lang="ts">
import type { ExportFormat, ExportRecord } from "../services/apiClient";
import { useI18nStore } from "../stores/i18n";

const markdown = defineModel<string>({ required: true });

defineProps<{
  canGenerate: boolean;
  canSave: boolean;
  canExport: boolean;
  exportHistory: ExportRecord[];
  exportingFormat: ExportFormat | null;
  generating: boolean;
  openingExportFolder: boolean;
  placeholder: string;
  saving: boolean;
}>();

const emit = defineEmits<{
  exportNote: [format: ExportFormat];
  openExportFolder: [];
  regenerate: [];
  save: [];
}>();

const i18n = useI18nStore();
</script>

<template>
  <section class="note-panel">
    <header class="panel-header">
      <h2>{{ i18n.t("noteTitle") }}</h2>
      <div class="note-actions">
        <button
          type="button"
          :disabled="!canGenerate || generating"
          @click="emit('regenerate')"
        >
          {{ generating ? i18n.t("generatingNote") : i18n.t("regenerate") }}
        </button>
        <button type="button" :disabled="!canSave || saving" @click="emit('save')">
          {{ saving ? i18n.t("savingNote") : i18n.t("saveNote") }}
        </button>
        <button
          type="button"
          :disabled="!canExport || Boolean(exportingFormat)"
          @click="emit('exportNote', 'markdown')"
        >
          {{
            exportingFormat === "markdown"
              ? i18n.t("exportingMarkdown")
              : i18n.t("exportMarkdown")
          }}
        </button>
        <button
          type="button"
          :disabled="!canExport || Boolean(exportingFormat)"
          @click="emit('exportNote', 'pdf')"
        >
          {{ exportingFormat === "pdf" ? i18n.t("exportingPdf") : i18n.t("exportPdf") }}
        </button>
        <button
          type="button"
          :disabled="!canExport || Boolean(exportingFormat)"
          @click="emit('exportNote', 'word')"
        >
          {{ exportingFormat === "word" ? i18n.t("exportingWord") : i18n.t("exportWord") }}
        </button>
      </div>
    </header>
    <textarea
      v-model="markdown"
      :aria-label="i18n.t('noteEditorLabel')"
      :placeholder="placeholder"
    />
    <footer class="export-history">
      <section>
        <h3>{{ i18n.t("exportHistory") }}</h3>
        <p v-if="exportHistory.length === 0" class="muted-copy">
          {{ i18n.t("noExports") }}
        </p>
        <ol v-else class="export-list">
          <li v-for="exportRecord in exportHistory" :key="exportRecord.id">
            <span>{{ exportRecord.fileName }}</span>
            <small>{{ exportRecord.format.toUpperCase() }}</small>
          </li>
        </ol>
      </section>
      <button
        type="button"
        :disabled="exportHistory.length === 0 || openingExportFolder"
        @click="emit('openExportFolder')"
      >
        {{
          openingExportFolder
            ? i18n.t("openingExportFolder")
            : i18n.t("openExportFolder")
        }}
      </button>
    </footer>
  </section>
</template>
