<script setup lang="ts">
import { computed, shallowRef } from "vue";

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
const activeMode = shallowRef<"edit" | "preview">("edit");
const previewBlocks = computed(() =>
  markdown.value.split(/\r?\n/).map((rawLine, index) => {
    const line = rawLine.trim();
    if (!line) {
      return { id: index, type: "blank", text: "" };
    }
    if (line.startsWith("### ")) {
      return { id: index, type: "heading3", text: line.slice(4) };
    }
    if (line.startsWith("## ")) {
      return { id: index, type: "heading2", text: line.slice(3) };
    }
    if (line.startsWith("# ")) {
      return { id: index, type: "heading1", text: line.slice(2) };
    }
    if (line.startsWith("- ")) {
      return { id: index, type: "list", text: line.slice(2) };
    }
    return { id: index, type: "paragraph", text: line };
  })
);
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
    <section class="note-workspace">
      <nav class="note-mode-switch" :aria-label="i18n.t('noteMode')">
        <button
          type="button"
          :class="{ active: activeMode === 'edit' }"
          @click="activeMode = 'edit'"
        >
          {{ i18n.t("editNote") }}
        </button>
        <button
          type="button"
          :class="{ active: activeMode === 'preview' }"
          @click="activeMode = 'preview'"
        >
          {{ i18n.t("previewNote") }}
        </button>
      </nav>
      <textarea
        v-if="activeMode === 'edit'"
        v-model="markdown"
        :aria-label="i18n.t('noteEditorLabel')"
        :placeholder="placeholder"
      />
      <article v-else class="note-preview" :aria-label="i18n.t('notePreviewLabel')">
        <template v-for="block in previewBlocks" :key="block.id">
          <h1 v-if="block.type === 'heading1'">{{ block.text }}</h1>
          <h2 v-else-if="block.type === 'heading2'">{{ block.text }}</h2>
          <h3 v-else-if="block.type === 'heading3'">{{ block.text }}</h3>
          <p v-else-if="block.type === 'list'" class="note-preview-list-item">
            {{ block.text }}
          </p>
          <p v-else-if="block.type === 'paragraph'">{{ block.text }}</p>
          <div v-else class="note-preview-spacer" />
        </template>
      </article>
    </section>
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
