# s-a-c agent-skills

A portable [agent-skills](https://agentskills.io) **governance pack** for the
[Vercel `skills`](https://github.com/vercel-labs/skills) CLI — "npm for agent
skills." Each skill is a `SKILL.md` (`name` + `description` frontmatter)
installable into OpenCode, Claude Code, Codex, Cursor, and 70+ other agents.
**Gate** skills additionally ship a co-located rule wrapper under `rules/`.

## Install

```bash
# all skills, interactively
npx skills add s-a-c/agent-skills

# specific skills (repeatable) — a gate skill brings its rules/ wrapper too
npx skills add s-a-c/agent-skills --skill s-a-c-git-write-gate --skill s-a-c-frontend-king-mode

# list available skills without installing
npx skills add s-a-c/agent-skills --list
```

See the [`skills` CLI docs](https://github.com/vercel-labs/skills) for global
(`-g`), agent-specific (`-a`), and non-interactive (`-y`) options.

## Skills

| Skill | Use when | Gate |
|---|---|:--:|
| `s-a-c-code-style-router` | choosing a language-specific code-style rule | |
| `s-a-c-frontend-king-mode` | frontend/UI work, or `ULTRATHINK` on a design task | |
| `s-a-c-javascript-cli-style` | zero-dependency ESM JavaScript CLI projects | |
| `s-a-c-debug-confirmation-gate` | before fixing any bug or error | ✓ |
| `s-a-c-bypass-shell-aliases` | issuing shell commands that must not hang on aliases | ✓ |
| `s-a-c-doc-tree-prefixes` | structuring a `docs/` tree with path-derived prefixes | ✓ |
| `s-a-c-doc-format-parity` | keeping Markdown/HTML documentation in parity | ✓ |
| `s-a-c-software-doc-lifecycle` | turning research or an idea into a software system | ✓ |
| `s-a-c-git-write-gate` | before any git write operation | ✓ |
| `s-a-c-scratch-script-safety` | running scratch scripts safely inside the workspace | ✓ |
| `s-a-c-governed-memory-substrate` | using a governed memory substrate for recall (parameterized) | |

## Always-on wrappers (gate skills)

Gate skills (✓ above) ship a co-located `rules/<gate>.md` — a thin
`alwaysApply: true` rule that fires every turn and routes to the skill for the
gate body. The skill is the single source of the body; the wrapper only enforces
always-on routing.

`npx skills add --skill <gate>` fetches **both** files (the skill folder is
copied whole), but installing a skill does **not** enforce the gate — `npx
skills` installs opt-in skills, not always-on rules. Enforcement is opt-in:

- **Enable:** copy the wrapper into your agent's always-on rules location and
  adapt the frontmatter — `~/.config/agents/rules/` (opencode),
  `.cursor/rules/*.mdc` (Cursor), `.clinerules/` (Cline). The wrapper's filename
  matches the skill (`s-a-c-` prefixed, namespaced), so copy it as-is — no rename
  needed, and it won't collide in a shared rules dir. Each carries the exact
  `cp`/`curl` one-liner.
- **Disable:** delete that copy. The skill stays installed as opt-in; only the
  always-on enforcement is removed.

```bash
# enable the git-write gate for opencode (global) — path-stable fetch from GitHub
# (works regardless of where the skill was installed; filename matches the skill — no rename)
curl -fsSL https://raw.githubusercontent.com/s-a-c/agent-skills/main/skills/s-a-c-git-write-gate/rules/s-a-c-git-write-gate.md \
  -o ~/.config/agents/rules/s-a-c-git-write-gate.md
# …or copy from the installed skill folder (path varies by agent/scope), e.g.
cp ~/.agents/skills/s-a-c-git-write-gate/rules/s-a-c-git-write-gate.md ~/.config/agents/rules/s-a-c-git-write-gate.md
```

## Layout

```
skills/<name>/SKILL.md            # every skill (name + description)
skills/<gate>/rules/<gate>.md     # gate skills only: always-on rule wrapper
```

This repo is a **portable export**: skills are generalized to be
workspace-agnostic. Workspace-specific values in `s-a-c-governed-memory-substrate`
are placeholders to fill in on install.

## License

MIT — see [LICENSE](./LICENSE).
