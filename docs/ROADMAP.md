# EchoMinutes-Agent Roadmap

EchoMinutes-Agent is past the first runnable-product phase. The next work should make the local-first meeting workflow reliable, inspectable, and useful enough to stand as a serious open-source desktop project.

## P3 Stabilization

- [ ] Add a restore or cleanup view for soft-deleted meetings.
- [ ] Add export preview checks for Markdown, PDF, and Word before writing history records.
- [ ] Add PDF font diagnostics in Settings so users know which local font is used.
- [ ] Add a compact error details panel for ASR, LLM, export, and backend startup failures.
- [ ] Add a packaged-app smoke test that starts `win-unpacked`, checks `/api/health`, imports a tiny audio file, and verifies export creation.

## Feature Completion

- [ ] Add meeting title rename and metadata editing.
- [ ] Add note template selection for weekly sync, design review, interview, and research discussion.
- [ ] Add speaker alias persistence so renamed speakers are reused across a meeting.
- [ ] Add transcript search, segment filtering, and quick jump from note sections to source transcript.
- [ ] Add an explicit workspace management page for storage location, media copies, exports, logs, and cache size.

## Technical Quality

- [ ] Add a lightweight SQLite migration layer instead of one-off schema upgrades.
- [ ] Add service-level tests for failed ASR, failed LLM, export errors, and retryable task states.
- [ ] Add frontend component tests for meeting library deletion, settings readiness states, and note/export button states.
- [ ] Add structured log categories for import, ASR, LLM, notes, exports, and packaging startup.
- [ ] Add a strict dependency audit pass before every packaged release.

## Product Experience

- [ ] Improve empty states for first launch, missing API key, missing FFmpeg, and provider quota failure.
- [ ] Add progress indicators for long ASR jobs and note generation.
- [ ] Add keyboard-friendly review flows for transcript editing and note saving.
- [ ] Add safer destructive actions with confirmation copy that explains what remains on disk.
- [ ] Add a first-run checklist that keeps cloud processing explicit without feeling like a setup wall.

## Evaluation And Release

- [ ] Keep a tiny public test fixture for offline checks and a private real-audio fixture for release smoke tests.
- [ ] Track ASR quality with speaker count, segment count, duration, and provider error code in local diagnostics.
- [ ] Track note quality with template coverage, required sections, action-item extraction, and export parity.
- [ ] Build a release checklist covering CI, Windows packaging, backend runtime startup, clean git status, and artifact upload.
- [ ] Document the app as a local-first AI Agent product with concrete Qwen, speaker rename, export, and Windows packaging capabilities.
