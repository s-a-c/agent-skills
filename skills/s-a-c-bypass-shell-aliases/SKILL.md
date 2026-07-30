---
name: s-a-c-bypass-shell-aliases
description: Bypass interactive shell aliases in agent-issued commands with a leading backslash or full executable path. Use before any agent shell command that must not hang on a y/n prompt.
---

# Bypass Shell Aliases

> **Core rule:** Agent-issued shell commands must not invoke interactive aliases. Prefix with `\` or use the full executable path.

## The Rule

Interactive shells alias common commands (`cp`, `mv`, `rm`, and others) with flags like `-i`. Those aliases run even when the agent passes `-f`, which causes **hangs** on `y/n` prompts in non-interactive and background terminals.

For every shell command the agent runs, use **one** of:

1. **Leading backslash** — bypasses aliases for that invocation:
   ```bash
   \cp -f source dest
   \mv -f source dest
   \rm -f file
   ```

2. **Full executable path** — same effect, explicit:
   ```bash
   /bin/cp -f source dest
   /bin/mv -f source dest
   /bin/rm -f file
   ```

Apply this to any command that might be aliased, not only file operations.

Secret-sync scripts (for example `infisical secrets get`) are non-interactive; file copies inside such scripts should still use `\cp` or `/bin/cp`.

## When It Applies

- All agent-issued terminal and script commands
- Copy/sync steps (dotfiles, config mirrors, chezmoi-style apply)
- Automation that must not block on prompts

## Examples

```bash
# BAD — may invoke cp -i and hang
cp -f config/.env config/.env.bak

# GOOD — backslash bypass
\cp -f config/.env config/.env.bak

# GOOD — full path
/bin/cp -f config/.env config/.env.bak
```

## See Also

- `s-a-c-scratch-script-safety` — scratch-script cwd policy.
