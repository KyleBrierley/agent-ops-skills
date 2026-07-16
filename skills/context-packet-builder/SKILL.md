---
name: context-packet-builder
description: Condense file-backed project state into a small prioritized handoff packet so a fresh agent can resume without loading full histories or private working logs.
---

# Context packet builder

Use this skill when a project has more durable state than a fresh agent should load into
context. It converts normalized current state into a compact handoff, prioritizing
decisions and next actions over history.

## Inputs

- A normalized JSON state file containing:
  - objective;
  - current decisions;
  - work items;
  - risks;
  - optional status counts.
- A maximum number of work items to include.

The example input is
[`examples/input/project-state.json`](examples/input/project-state.json).

## Outputs

- A deterministic Markdown context packet containing:
  - current objective;
  - decisions that constrain future work;
  - highest-priority active items;
  - blockers and risks;
  - compact status counts.

The reference output is
[`examples/expected-context-packet.md`](examples/expected-context-packet.md).

## Workflow

1. Read current canonical state, not full historical logs.
2. Normalize records before ranking them.
3. Exclude completed items unless they constrain current work.
4. Rank active work by:
   - blocking status;
   - explicit priority;
   - due date;
   - stable identifier.
5. Include only decisions that affect the next agent’s behavior.
6. Render the packet deterministically with
   [`scripts/build_context_packet.py`](scripts/build_context_packet.py).
7. Treat the packet as a derived view; update canonical state first when reality changes.

## Failure handling

- If required input fields are missing, stop with a field-specific error.
- If dates are invalid, report the record identifier and do not guess ordering.
- If canonical sources disagree, flag the conflict rather than hiding it in the summary.
- If the packet exceeds the requested item limit, truncate only after deterministic
  ranking and report the omitted count.

## Boundaries

- Do not treat the packet as the canonical database.
- Do not include secrets, personal communications, or verbose historical logs.
- Do not carry completed or stale work forward merely because it appeared in an old handoff.
- Do not infer approval or execution state from a planned next action.
- Do not compress away blockers, safety constraints, or irreversible decisions.
