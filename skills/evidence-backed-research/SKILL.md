---
name: evidence-backed-research
description: Build a citation-ready evidence packet that separates sourced facts, inference, conflicts, staleness, and open gaps before any narrative is written.
---

# Evidence-backed research

Use this skill when an answer, brief, record, or article must be defensible at the
claim level. The skill stops at structured evidence; it does not write promotional prose
or decide that weak evidence is sufficient.

## Inputs

- A bounded research question or target.
- A list of allowed source types or domains, if constrained.
- The date at which the research should be considered current.
- An optional output schema.

## Outputs

- One evidence packet using the structure in
  [`examples/evidence-packet.json`](examples/evidence-packet.json).
- A list of conflicts, stale sources, unsupported assumptions, and unanswered questions.
- A clear recommendation: `ready_for_synthesis`, `needs_more_evidence`, or `blocked`.

## Workflow

1. Restate the exact question and define what would count as sufficient evidence.
2. Gather primary sources first, then credible secondary sources where necessary.
3. For every claim, record:
   - the normalized claim;
   - source title and URL;
   - publication or access date;
   - a short supporting excerpt or faithful paraphrase;
   - confidence: `confirmed`, `inferred`, or `reported`;
   - temporal status: `current`, `historical`, or `unknown`.
4. Record conflicting evidence side by side. Do not silently choose the preferred answer.
5. Separate source-backed facts from analyst inference.
6. Check whether precise numbers, dates, and superlatives are directly supported.
7. List evidence gaps and issue the readiness recommendation.

## Confidence rules

- `confirmed`: the subject or authoritative primary source states it directly.
- `inferred`: strong technical evidence supports it, but the subject did not state it.
- `reported`: a credible third party states it.

Confidence describes the relationship between claim and source, not how persuasive the
claim sounds.

## Failure handling

- If a source cannot be opened, record it as unavailable; do not rely on a search snippet
  as confirmed evidence.
- If evidence is older than the user-defined freshness window, label it historical.
- If sources conflict, return `needs_more_evidence` unless the output can honestly retain
  both possibilities.
- If the central claim has no direct support, return `blocked`.

## Boundaries

- Do not invent citations, quotes, dates, or source contents.
- Do not transform inference into fact.
- Do not write publication-ready narrative as part of this skill.
- Do not expose private documents or credentials in the packet.
- Preserve uncertainty when the evidence does not resolve it.
