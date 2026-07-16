---
name: human-approved-publishing
description: Prepare and validate a publication candidate while preserving an explicit human decision gate before any external post, merge, send, or release.
---

# Human-approved publishing

Use this skill when an agent may prepare material for publication but must not perform the
external action without a clearly recorded human decision.

## Inputs

- Draft content or structured material.
- Target channel and audience.
- Publication requirements: citations, formatting, validation, privacy, and voice.
- The identity of the human approver or approval mechanism.

## Outputs

- A publication candidate.
- A validation report with blocking and non-blocking findings.
- A decision record with one state:
  `draft`, `ready_for_review`, `approved`, `changes_requested`, or `published`.
- If approved, an exact action packet describing what would be published and where.

See [`examples/decision-record.json`](examples/decision-record.json).

## Workflow

1. Confirm the target channel, intended audience, and irreversible action.
2. Create or normalize the draft without publishing it.
3. Run deterministic checks available for the artifact.
4. Review facts, privacy, attribution, links, tone, and channel-specific constraints.
5. Present:
   - the exact candidate;
   - blocking findings;
   - non-blocking suggestions;
   - the exact external action awaiting approval.
6. Stop in `ready_for_review`.
7. Move to `approved` only after an explicit human approval tied to the current candidate.
8. Before execution, verify that the candidate has not changed since approval.
9. Record the result as `published` only after the external system confirms success.

## Approval validity

Approval is scoped to the exact artifact, destination, and action presented. A material
content change, different destination, or new external side effect invalidates the prior
approval and returns the state to `ready_for_review`.

## Failure handling

- If validation fails, use `changes_requested` and list the blockers.
- If the approval is ambiguous or refers to an older version, remain in
  `ready_for_review`.
- If publication fails, preserve `approved`, record the failure, and do not claim
  `published`.
- If external state cannot be verified, report `publication_unconfirmed`.

## Boundaries

- Never infer approval from silence, prior enthusiasm, or approval of a different draft.
- Never hide the target destination or external side effect.
- Never label a prepared artifact as published.
- Do not weaken deterministic validation to obtain a green result.
- Do not include secrets or private verification evidence in the public artifact.
