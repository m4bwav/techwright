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

Add `--json` for machine-readable output. Nothing changes the machine: fixes are printed as steps for you to approve.

## Docs

Wiki: https://github.com/m4bwav/techwright/wiki (coming soon). Notes and plans are in [ai-docs](ai-docs/HANDOFF.md). Tests: [TESTS.md](TESTS.md).

## License

MIT. See [LICENSE](LICENSE). Security reports: [SECURITY.md](SECURITY.md).
