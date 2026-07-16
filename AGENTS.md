# Repository instructions

- Keep skills provider-neutral unless a capability requires a named provider.
- Never add real personal data, company-confidential material, credentials, private URLs,
  or absolute user filesystem paths.
- Every skill needs YAML frontmatter with `name` and `description`.
- Every skill must define inputs, outputs, workflow, failure handling, and boundaries.
- External actions must remain approval-gated.
- Run `python3 scripts/validate_skills.py` and the unit tests before proposing publication.
