---
description: Bypass shell aliases in agent-issued commands — use leading backslash or full executable path
alwaysApply: true
---

# Shell Alias Bypass

Always-on wrapper for the **`s-a-c-bypass-shell-aliases`** skill — fires every
turn and routes to the skill for the full gate body. The skill is the single
source of the body; this file only enforces always-on routing.

**Not enforced by installing the skill.** `npx skills` installs opt-in skills,
not always-on rules. To enforce, copy this file into your agent's always-on rules
location (`~/.config/agents/rules/`, `.cursor/rules/*.mdc`, `.clinerules/`, …) and
adapt the frontmatter. The filename is already the conventional rule name, so no
rename is needed. To stop enforcement, delete that copy — the skill stays
installed as opt-in.

```bash
# enable: path-stable fetch from GitHub (filename matches the target — no rename)
curl -fsSL https://raw.githubusercontent.com/s-a-c/agent-skills/main/skills/s-a-c-bypass-shell-aliases/rules/shell-alias-bypass.md \
  -o ~/.config/agents/rules/shell-alias-bypass.md
# …or copy from the installed skill folder (path varies by agent/scope), e.g.
cp ~/.agents/skills/s-a-c-bypass-shell-aliases/rules/shell-alias-bypass.md ~/.config/agents/rules/shell-alias-bypass.md
```
