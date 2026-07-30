---
name: s-a-c-scratch-script-safety
description: Run scratch scripts inside a workspace-local tmp dir, never system /tmp, so command tools stay within the workspace boundary. Use before creating or running any scratch or temporary script.
---

# Scratch Script Safety

> **Core rule:** NEVER use the system `/tmp/` — always use a workspace-local tmp dir (e.g. `.agents/tmp/`) and set the command tool's working directory to the workspace root. `/tmp/` is outside the workspace boundary and causes command tools to hang.

> **Priority: critical** — Violating this rule causes commands to hang and freeze the conversation.

## The Rule

**NEVER create or run scratch scripts in the system `/tmp/`.** Always use a
workspace-local tmp directory instead.

Running scripts in `/tmp/` causes a command tool to hang because `/tmp/` is outside
the workspace boundary. This freezes the entire conversation with no recovery.

## Requirements

1. **Path:** All scratch/temporary scripts go in the workspace-local tmp dir
   (conventionally `.agents/tmp/`), NOT the system `/tmp/`.
2. **Working directory:** When invoking the agent's command tool, set its working
   directory (e.g. `Cwd` / `cwd` / `workdir`) to the **workspace root** — never to
   `/tmp/` or any path outside the workspace.
3. **Create dir first:** Run `mkdir -p .agents/tmp` before writing scratch files if
   the directory might not exist.
4. **Cleanup:** Delete scratch files after use when they are no longer needed.

## Examples

```
# CORRECT
Working directory: /path/to/project
Command:           node .agents/tmp/test-parser.js

# WRONG — will hang
Working directory: /tmp
Command:           node /tmp/test-parser.js
```

## Why This Matters

The command tool requires its working directory to be within the workspace. When
scripts are placed in `/tmp/` and the working directory is set to `/tmp/`, the
command hangs indefinitely — the agent goes silent and the user must restart the
conversation.
