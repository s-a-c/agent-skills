---
name: s-a-c-software-doc-lifecycle
description: Turn research or an idea into a decision-ready, traceable path to a buildable and operable software system. Use when software documentation turns research/idea into a system, or materially plans its evolution.
---

# Software Documentation Lifecycle

> **Core rule:** Turn evidence into a decision-ready, traceable path to a buildable and operable software system. Choose documentation proportionate to the work; do not manufacture a checklist of empty artifacts.

## 1. Start from the current state

- Before proposing, planning, or adding software documentation, inspect the existing documentation, research, issue tracker, domain language, and relevant source code. Identify the latest supported decision in each area before creating another document.
- State the effort's current lifecycle position and the next unresolved decision. Preserve useful material; synthesize or link it instead of duplicating it.
- The documentation-tree-prefixes skill remains authoritative for documentation-tree prefixes, navigation, Markdown presentation, links, visuals, and migration. This rule governs lifecycle content and decision flow only.

## 2. Build a proportional decision chain

Work from evidence toward operation. Address each applicable decision area in order; combine closely related areas when that makes the result clearer.

1. **Evidence and synthesis:** retain source research, then record the findings, assumptions, constraints, risks, opportunities, and open questions that matter.
2. **Problem and outcome:** define the problem, affected users and stakeholders, vision, goals, non-goals, success measures, and constraints.
3. **Requirements and scope:** describe use cases or user stories, functional behaviour, quality attributes, acceptance criteria, MVP/release scope, and explicit out-of-scope work.
4. **Traceability:** link consequential research findings to requirements, decisions, designs, and acceptance tests. Use a matrix only when it is clearer than concise links in the relevant documents.
5. **Solution design:** document the system context, significant architecture decisions, solution architecture, data model, external/API contracts, user experience, security, privacy, and trust boundaries that the selected scope needs.
6. **Delivery and assurance:** make the implementation approach, test strategy, acceptance plan, deployment and release approach, operational runbook, and maintenance or roadmap decisions discoverable before they are needed.

An area may be omitted, merged, or deferred only when it is genuinely inapplicable or premature. Record the reason and the document, issue, or future decision that owns it. Do not present an omission as an unresolved requirement.

## 3. Keep decisions traceable and durable

- Give each consequential decision one durable home; link to it from summaries and indexes instead of restating it in multiple places.
- Link claims to their evidence, designs to the requirements they satisfy, and tests to the acceptance criteria they verify.
- Record status and consequences for architectural decisions. Keep raw evidence separate from the synthesis that informs a decision.
- Update the nearest owning documentation when a changed implementation invalidates a documented decision, contract, operational procedure, or scope boundary.

## 4. Use Wayfinder when the route is not yet clear

When a `/wayfinder` skill is present, read its `SKILL.md` and follow it for an effort that is broad, materially uncertain, or expected to require multiple sessions before a buildable plan is possible. Use it when the destination, decision frontier, or dependencies cannot yet be stated sharply enough for an ordinary plan.

- Review the project's existing research and documentation before charting a map.
- Use the repository's documented issue tracker. The Wayfinder map is the planning index; its child tickets resolve individual decisions. Keep answers in their resolving tickets and link documentation assets as evidence rather than duplicating them in the map.
- Include the applicable lifecycle areas and domain skills in the map's `## Notes`, so each session knows which evidence and decisions govern the next ticket.
- Let newly resolved decisions graduate only the now-specific parts of the fog into tickets. Respect Wayfinder's one-ticket-per-session and native dependency workflow.

Do not invoke Wayfinder for a small, already decision-ready documentation change. Apply the proportional lifecycle directly and use the closest appropriate planning workflow instead.

## 5. Completion check

Before treating a software documentation effort as ready for implementation or release, verify that the next consumer can find:

- the supported problem, scope, and success criteria;
- the requirements and acceptance evidence relevant to the proposed change;
- the current architectural, interface, data, security, and operational decisions that affect it; and
- the source of each important claim, decision, and deferred question.

If a consumer cannot make a needed decision without rediscovering prior work, improve the links, synthesis, or ownership before adding more documents.

## See Also

- `s-a-c-doc-tree-prefixes` — structure/navigation contract for the docs tree.
- `s-a-c-doc-format-parity` — Markdown/HTML parity contract.
