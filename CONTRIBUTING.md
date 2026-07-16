# Contributing

Contributions should make a skill more portable, testable, or honest.

## Requirements

1. Keep one bounded outcome per skill.
2. Use synthetic examples with no personal or proprietary data.
3. Separate agent preparation from human authorization when an external action is possible.
4. State inputs, outputs, failure conditions, and non-goals.
5. Add or update validation for machine-readable artifacts.
6. Run:

   ```bash
   python3 scripts/validate_skills.py
   python3 -m unittest discover -s tests
   ```

## Pull requests

Explain the operating problem, the new behavior, the safety boundary, and how you tested
it. Avoid adding provider-specific instructions unless the skill truly depends on them.
