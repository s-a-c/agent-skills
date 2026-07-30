---
name: s-a-c-governed-memory-substrate
description: Use a governed agent-memory substrate for recall (distinct from a task store), namespace-scoped and fail-closed on health checks. Parameterized template — fill the placeholders on install.
---

# Governed Memory Substrate

This is a **parameterized template.** It carries the reusable kernel for using a
governed agent-memory substrate and leaves workspace specifics as
`<PLACEHOLDER: …>` markers the installer fills in. Until the placeholders are
filled, treat the substrate endpoint, namespace, and readiness scripts as
unconfigured.

Use the central governed-memory substrate for **governed agent-memory recall**.
Two companion skills typically apply:

- a **workspace-wiring** skill — endpoints, namespace, scripts, fail-closed behavior
- a **generic usage** skill — memory types, lifecycle, reflection, decision tables

Read the workspace-wiring skill for environment-specific details. Read the usage
skill when any substrate MCP tool is called.

## Task-store boundary

| System | Use for |
| --- | --- |
| **Task tracker** (issue tracker / `bd`-equivalent) | Tasks, issues, blockers, project tracking in this repo |
| **Governed memory substrate** | Governed agent-memory recall via MCP in a scoped namespace (`<PLACEHOLDER: namespace>`) |

Do not store task state in the memory substrate. Do not use the task tracker as a
substitute for substrate recall.

## Endpoints

| Route | URL |
| --- | --- |
| Raw (scripts, health) | `<PLACEHOLDER: raw base URL, e.g. http://127.0.0.1:7243>` |
| Named (MCP in GUI hosts) | `<PLACEHOLDER: named URL>` |
| Dashboard | `<PLACEHOLDER: dashboard URL>` |
| MCP Streamable HTTP | `<PLACEHOLDER: streamable HTTP endpoint>` |
| MCP HTTP+SSE (legacy) | `<PLACEHOLDER: SSE endpoint>` |

Health checks in scripts use a `SUBSTRATE_HEALTH_URL` env var (default
`<PLACEHOLDER: raw health path, e.g. 7243/health>`).

## When to use the substrate

- Recall workspace-scoped agent memory
- Cite or follow substrate refs (`<PLACEHOLDER: ref scheme>://<namespace>/…`)
- Operator-directed memory workflows documented in `<PLACEHOLDER: operator docs path>`

## When not to use the substrate

The memory substrate is not PKM, validation evidence, accepted evidence, a task
store, or a governance authority. See `<PLACEHOLDER: substrate README>`.

Reviewable Intake (propose/approve/reject) is control-plane scope, not automatic in
a plain workspace.

## Fail closed

If substrate health checks fail, do not claim recall succeeded. Run:

```bash
<PLACEHOLDER: readiness script path, e.g. scripts/verify-substrate-readiness.sh>
```

## Operator docs

- `<PLACEHOLDER: contents page>`
- `<PLACEHOLDER: user guide>`
- `<PLACEHOLDER: agentic usage guide>`
- `<PLACEHOLDER: advanced usage>`
- Bootstrap: `<PLACEHOLDER: bootstrap script path>`
