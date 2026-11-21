# techwright

![techwright banner](.github/images/banner.jpg)

Home tech support for computers, Wi-Fi and gadgets. A Claude Code plugin with one skill and a standard-library script that only reads.

- Symptom to likely cause, cheapest safe check first, and a clear "take it in" stop (swollen battery, burning smell, clicking drive with no backup).
- Wi-Fi and internet: link, router, ISP or DNS, from one `tech.py net` ladder.
- Router hardening from the CISA checklist.
- Backups: a 3-2-1 table of what this PC really has, and a restore test that copies a file back and compares SHA-256.
- Drive and system health: disk status, free space, critical events from the last week in plain words, Defender.
- Buying advice with an as-of date and a source on every price, and a safe beginner homelab path.

Not for account or device security (shieldwright), appliances (fixwright) or AI server pools (labwright).

## Install

In Claude Code:

```
/plugin marketplace add m4bwav/techwright
/plugin install techwright@techwright
```

Needs Python 3.9+ (standard library only). The checks run on Windows; on other systems the skill walks the same steps by hand.

## Use

Ask in plain words: "my PC is slow", "Wi-Fi keeps dropping", "is it my router or the ISP", "secure my router", "are my backups good", "is my drive dying", "what laptop should I buy". The script runs on its own too:

```
python scripts/tech.py net
python scripts/tech.py disk
python scripts/tech.py backup --target E:\Backup --restore-test E:\Backup\budget.txt --original C:\Users\me\budget.txt
python scripts/tech.py health
```

Add `--json` for machine-readable output. Nothing changes the machine: fixes are printed as steps for you to approve. Probes that need an administrator shell (disk reliability counters, system-image versions) are listed under `admin_needed` instead of run.

What each command reports:

- `net`: a verdict from the ladder link, router, internet, DNS: `ok`, `no-link`, `local-network`, `isp`, `dns` or `degraded`, with advice. A weak Wi-Fi signal (under 40%) adds advice without changing the verdict.
- `disk`: free space per volume (under 10% free is a finding) and each physical disk's health; a disk not `Healthy` or with uncorrected errors is a `STOP` line.
- `backup`: the copies it can see (File History, OneDrive, a system image, and each `--target` you name, which is counted as you declare it and not checked) against 3-2-1, verdict `3-2-1 met` or `gaps`. `--restore-test` copies one file from the backup into a new folder under your temp folder (left there for you to inspect) and compares SHA-256: `pass`, `differs` (the original changed since the backup) or `fail`.
- `health`: the ten most frequent critical and error events of the last seven days, with plain meanings for the known ones, Defender's state and the next checks.

Exit codes: 0 when the command ran (findings do not change it), 1 when the command is not supported on this system, 2 when a restore test failed, and 2 from argparse for a bad argument.

`net` and `health` need Windows. On other systems `disk` and `backup` run but see only free space on `/` and your declared targets.

## Docs

Wiki: https://github.com/m4bwav/techwright/wiki (commands with sample output, how verdicts are reached, recipes, FAQ). Notes and plans are in [ai-docs](ai-docs/HANDOFF.md). Tests: [TESTS.md](TESTS.md).

## Tests

`python -m pytest` (or `python -m unittest discover -s tests`) from the repo root; the parsers and verdicts are tested on fixture text, so the tests run on any system.

## License

MIT. See [LICENSE](LICENSE). Security reports: [SECURITY.md](SECURITY.md).
