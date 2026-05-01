# Contributing

Thanks for helping build EchoMinutes-Agent.

Before changing code, read:

1. `AGENTS.md`
2. `docs/EchoMinutes-Agent.md`
3. `.codex/rules/project.md`

## Development Principles

- Keep the first version local-first and desktop-focused.
- Prefer provider abstractions over direct cloud API calls in business logic.
- Keep real API keys out of the repository.
- Start with mock providers unless the task explicitly requires real Aliyun or Qwen integration.
- Keep changes aligned to the current delivery slice: P0, P1, P2, or P3.

## Pull Request Checklist

- Describe the delivery slice the change belongs to.
- List changed files and user-visible behavior.
- Run at least one relevant validation command.
- Mention any tests that could not be run.
- Avoid unrelated refactors.
