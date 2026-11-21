# Backups

## 3-2-1
Three copies of the data, on two kinds of storage, one off-site (Backblaze, https://www.backblaze.com/blog/the-3-2-1-backup-strategy/, checked 2026-11-21). `tech.py backup` counts only what is configured on this PC; ask about copies it cannot see (a NAS, a drive in a drawer, a cloud backup app) and pass them with `--target`.

## What counts
- **Windows Backup** saves user folders to OneDrive plus apps, Wi-Fi networks and settings (https://support.microsoft.com/en-us/windows/back-up-your-windows-pc-87a81f8a-78fa-456e-b521-ac0560e32338, checked 2026-11-21). Good for moving to a new PC; it is sync, not history.
- **OneDrive / Google Drive / Dropbox sync**: a deletion or ransomware syncs too. Counts off-site only if version history and the recycle bin cover the gap.
- **File History** to an external or network drive: versioned, local.
- **System image** (wbadmin) or a third-party image tool: whole-disk restore.
- **Backup apps** with versioning to cloud or NAS (Restic, Kopia, Duplicati, Backblaze Personal): real off-site history.

## Restore test
A backup never restored is a hope. Pick one file the owner cares about, find it inside the backup, then:
`tech.py backup --restore-test "<file in backup>" --original "<same file on PC>"`
It copies to a new temp folder and compares SHA-256: `pass`, `differs` (changed since the backup, usually fine) or `fail`. Repeat after any backup change, and at least every few months.

## Fixing gaps
No off-site copy: add a cloud backup with versioning. One media type: add an external drive with File History. Drive with STOP findings: back up first, today.
