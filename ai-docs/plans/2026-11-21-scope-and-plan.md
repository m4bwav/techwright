# techwright scope and plan (2026-11-21)

One plugin, one hub skill `techwright` with references loaded on demand (keep the package small), plus stdlib `scripts/tech.py`.

## tech.py (read-only, Windows first; macOS/Linux later or "not supported" message)
- `net`: netsh/ipconfig/ping ladder -> verdict (local link, Wi-Fi signal/channel congestion, ISP, DNS) as JSON or text.
- `disk`: reliability counters, smartctl if present, free space, disk error events.
- `backup`: File History / Windows Backup / OneDrive / wbadmin state -> 3-2-1 table with gaps; `backup --restore-test PATH` copies one file from the backup target to a temp dir and hashes it against the source (writes only to temp).
- `health`: reliability records, critical events, battery report, Defender, pending updates; defer the scored checkup to desktop-commander when present.
- Every probe marks admin-needed and skips; fixers are printed as suggestions, never run.
- Tests: fixture outputs of each command parsed offline (unittest, no live calls).

## References
troubleshoot.md (symptom trees, safe-check order, "take it in" stop rules), network.md (placement, channels, mesh vs extender, ISP box, router hardening checklist from CISA/NSA), backup.md, buying.md (needs -> specs -> 2-3 picks, prices with "as of" date, PCPartPicker compatibility), homelab.md (NAS, Compose, reverse proxy, Tailscale/Tunnel; neighbour labwright).

## Order
1. tech.py net + disk with fixture tests. 2. backup + restore test, health. 3. SKILL.md + references. 4. evergreen unit, evals with baseline. 5. README with banner, marketplace install, release. Public question on an askwright page near release.

## Goal
Ship the plugin as scoped below.

## Status
Done: released 0.1.0 (2026-11-21); see HANDOFF.md.

## Next single action
See HANDOFF.md.
