---
description: CRITICAL — Scratch scripts must run inside workspace (.agents/tmp/), NEVER in /tmp/
alwaysApply: true
---

# Scratch Scripts Policy

Always-on wrapper for the **`s-a-c-scratch-script-safety`** skill — fires every
turn and routes to the skill for the full gate body. The skill is the single
source of the body; this file only enforces always-on routing.

**Not enforced by installing the skill.** `npx skills` installs opt-in skills,
not always-on rules. To enforce, copy this file into your agent's always-on rules
location (`~/.config/agents/rules/`, `.cursor/rules/*.mdc`, `.clinerules/`, …) and
adapt the frontmatter. The filename matches the skill (`s-a-c-` prefixed,
namespaced), so copy it as-is — no rename needed, and it won't collide in a shared
rules dir. To stop enforcement, delete that copy — the skill stays installed as
opt-in.

```bash
# enable: path-stable fetch from GitHub (filename matches the target — no rename)
curl -fsSL https://raw.githubusercontent.com/s-a-c/agent-skills/main/skills/s-a-c-scratch-script-safety/rules/s-a-c-scratch-script-safety.md \
  -o ~/.config/agents/rules/s-a-c-scratch-script-safety.md
# …or copy from the installed skill folder (path varies by agent/scope), e.g.
cp ~/.agents/skills/s-a-c-scratch-script-safety/rules/s-a-c-scratch-script-safety.md ~/.config/agents/rules/s-a-c-scratch-script-safety.md
```
