# Context packet

## Objective

Publish a validated public data correction without bypassing human review.

## Decisions

- The public repository is the source of truth for approved records.
- External publication requires explicit human approval.

## Priority work

- [blocked] TASK-103: Verify the private importer rejects an unapproved commit. (critical; due 2026-07-18)
- [ready] TASK-101: Review the correction pull request. (high; due 2026-07-17)
- [pending] TASK-102: Update the public record after approval. (medium)

## Risks and blockers

- Running both import and export workflows could overwrite approved data.

## Status counts

- approved: 0
- blocked: 1
- ready: 1
