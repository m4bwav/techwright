# AGENTS.md

Rules for any AI agent working in this repository. `CLAUDE.md` imports this file; `.github/copilot-instructions.md` points here.

## What this is

techwright: one hub skill, `skills/techwright/` (SKILL.md and references), and `scripts/tech.py` (standard library only, read-only Windows checks: net, disk, backup, health). `evals/` holds the skill eval suite, `ai-docs/` the notes, plans and handoff (start with `ai-docs/HANDOFF.md`).

## Rules

- Python 3.9+, standard library only. UTF-8, LF. tech.py never changes the machine; fixes are printed steps the owner approves.
- Every change gets a test: `python -m unittest discover -s tests`.
- Evergreen unit at the root: read `evergreen.json` before editing; changes go in CHANGELOG with the reason, lessons in LEARNINGS.
- A release bumps `.claude-plugin/plugin.json` and CHANGELOG together.
- Prices carry an as-of date and a source. Plain short sentences, no em dashes, relative links. No AI attribution anywhere.
