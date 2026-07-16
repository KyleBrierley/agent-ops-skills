---
name: schema-validated-records
description: Convert evidence into machine-readable records with provenance, confidence, history, and deterministic schema validation before downstream use.
---

# Schema-validated records

Use this skill when research or operational state must become a stable machine-readable
contract without losing source provenance or uncertainty.

## Inputs

- A JSON Schema or equivalent explicit contract.
- Source evidence or normalized facts.
- Allowed enums, identifiers, and update rules.
- Existing records when history must be preserved.

## Outputs

- A record conforming to the supplied schema.
- A deterministic validation report.
- A change summary describing additions, replacements, removals, and confidence changes.
- Any unresolved evidence-to-field mapping questions.

See [`examples/widget-record.schema.json`](examples/widget-record.schema.json) and
[`examples/widget-record.json`](examples/widget-record.json).

## Workflow

1. Read the schema before transforming data.
2. Map each evidence-backed fact to a field and preserve its source reference.
3. Use only allowed identifiers and enum values.
4. Represent uncertainty explicitly rather than omitting it deceptively.
5. Preserve history:
   - mark replaced or previous values;
   - do not destructively erase meaningful transitions;
   - omit dates that are unknown rather than substituting source-publication dates.
6. Validate with the project’s deterministic validator.
7. Check cross-record invariants such as unique identifiers and documented categories.
8. Compare the record back to the evidence and report any unsupported fields.

## Validation order

1. Parseability.
2. Schema conformance.
3. Identifier and filename consistency.
4. Enum and category consistency.
5. Cross-record uniqueness.
6. Provenance completeness.
7. Human review of semantic accuracy.

## Failure handling

- On schema failure, return the exact field path and validator message.
- On missing evidence, leave the field absent or explicitly unknown; do not guess.
- On conflicting evidence, retain both claims where the schema permits or escalate the
  mapping decision.
- On an incompatible schema change, stop and propose a migration rather than silently
  rewriting records.

## Boundaries

- Passing schema validation does not prove factual truth.
- Do not label inferred data as confirmed.
- Do not use source publication date as an adoption or transition date.
- Do not delete historical state merely to simplify the current record.
- Do not publish a record before its evidence and semantic meaning are reviewed.
