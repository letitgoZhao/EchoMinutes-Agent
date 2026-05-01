# EchoMinutes Local Workspace Example

Runtime-generated files should live in a user-configurable local workspace, not in source-controlled application directories.

Expected runtime folders:

```text
workspace.local/
  media/
  exports/
  logs/
  echominutes.sqlite3
```

`workspace.local/` is intentionally ignored by git.
