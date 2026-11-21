# Tests

- Unit: `python -m unittest discover -s tests` (fixture-tested parsers; no live probes).
- Skill evals: `evals/evals.json` (5 cases: restore, 321, battery, router, prices; fixtures in `evals/fixtures`).
- T-001 2026-11-21, one run each, graded by the parent session on evergreen-tester reports: with skill 5/5, bare baseline 5/5. With the skill the restore case ran `tech.py backup --restore-test` (restore_test: differs); bare used sha256sum and cmp. No trigger proxy run: the plugin was not installed during the run.
