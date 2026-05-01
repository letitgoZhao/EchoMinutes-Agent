# Environment Rules

## Files

- `.env` is local-only and ignored by git.
- `.env.example` uses the same variable names as `.env` with placeholder values only.
- Real provider credentials must never be committed.

## Default Development Mode

Keep local environment files concise. Early testing uses DashScope compatible mode:

```text
DASHSCOPE_API_KEY="sk-<your_api_key>"
DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
DASHSCOPE_MODEL="qwen-plus"
```

## Local Workspace

Generated media, databases, exports, logs, and temporary files belong under configurable local workspace paths, not hard-coded project paths.
