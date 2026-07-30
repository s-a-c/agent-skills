---
name: s-a-c-debug-confirmation-gate
description: Require user confirmation before fixing any bug or error. Use before writing fix code for a reported bug, a discovered bug, a test failure, or any error that needs fixing.
---

# Debug Confirmation Gate

> **Core rule:** NEVER write fix code before presenting Root Cause + Evidence + Proposed Fix and getting explicit user confirmation.

> **Gate (must):** When you identify a bug, error, test failure, or any code that
> needs fixing — whether the user asked you to fix it, or you discovered it
> yourself — you MUST present your analysis and get user confirmation BEFORE
> writing any fix.

## Required Analysis Report

Present the following to the user:

1. **Root Cause** — What is causing the issue and why
2. **Evidence** — Error messages, stack traces, or code references that support your analysis
3. **Proposed Fix** — Specific files and changes you plan to make
4. **Risk Assessment** — What else could be affected by this fix

Then ask: "Do you agree with this analysis and proposed fix?"

## Wait for Confirmation

- If user confirms → proceed with implementation
- If user requests changes → revise analysis and re-present
- If user rejects → stop and ask for guidance

## Do Not

- Write fix code before presenting analysis
- Combine analysis + fix in one step
- Skip this gate because the fix "seems obvious"
