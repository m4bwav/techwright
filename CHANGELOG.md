# Changelog

## 0.1.1 (2026-11-21)
- Fix: `backup --restore-test` that could not restore the file still printed `3-2-1 met` and exited 0. A failed restore now sets the verdict to `restore failed`, adds a `STOP` finding first and exits 2.
- README: verdicts, `admin_needed`, exit codes, what runs off Windows, tests, wiki link.

## 0.1.0 (2026-11-21)
- First release: hub skill `techwright` with references (troubleshoot, network with the CISA router checklist, backup, buying, homelab) and `tech.py` (net, disk, backup with `--restore-test`, health), all read-only.
- Eval suite of five cases with no-skill baselines.
