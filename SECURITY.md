# Security

Report a vulnerability through GitHub's private vulnerability reporting on this repository (Security tab, "Report a vulnerability"). Please do not open a public issue.

techwright's `tech.py` only reads: it runs Windows commands such as `netsh`, `ping`, `nslookup` and PowerShell `Get-*` cmdlets, and the backup restore test copies one file you name into a temp folder to compare hashes. It never changes settings, never uploads anything and needs no admin rights.
