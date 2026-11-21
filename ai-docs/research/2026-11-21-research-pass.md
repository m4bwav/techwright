# techwright research pass (2026-11-21)

Light pass (one subagent, one web search; source URLs not fetched yet, verify before citing).

## Existing tools (do not duplicate)
- desktop-commander computer-health-check: read-only scored checkup (disk, CPU/RAM hogs, battery, startup, updates). Point to it; do not rebuild.
- jackspace/claudeskillz network-diagnostics (WSL/Linux only), windows-expert (general admin knowledge).
- AhmedLaminou/windows-mcp-server (Windows diagnostics MCP).
- Cite rather than rebuild: smartmontools, CrystalDiskInfo, WizTree, Ookla speedtest CLI, iperf3, Restic/Kopia/Duplicati, Tailscale, Cloudflare Tunnel, Caddy/Traefik/NPM, awesome-selfhosted.
- Neighbours: fixwright (appliances), labwright (AI server pool), quirkwright (agent shell), shieldwright (security; keeps account/device hardening, techwright keeps router hardening).

## Sources per skill
- Troubleshoot: support.microsoft.com/windows, support.apple.com, iFixit.
- Network: CISA home network security, NSA "Best Practices for Securing Your Home Network", FCC broadband speed guide, Wi-Fi Alliance (WPA3), Microsoft "Fix Wi-Fi connection issues".
- Backup: Backblaze 3-2-1 and Drive Stats, CISA backup guidance, Microsoft File History / Windows Backup.
- Buy: rtings, PCPartPicker, Keepa/camelcamelcamel; every price dated.
- Homelab: Docker, Tailscale KB, Cloudflare Tunnel, TrueNAS, Synology KB, OWASP.

## Read-only Windows probes for tech.py
netsh wlan show interfaces / networks mode=bssid / drivers; ipconfig /all; ping gateway -> 1.1.1.1 -> hostname (local/ISP/DNS split); tracert -d, pathping; Resolve-DnsName; Get-NetAdapter, Get-NetConnectionProfile; Get-PhysicalDisk | Get-StorageReliabilityCounter; smartctl -a if present; Get-Volume; File History event log + config; wbadmin get versions, vssadmin list shadows (admin); powercfg /batteryreport, /requests; Win32_ReliabilityRecords; Get-WinEvent System level 1,2 (Kernel-Power 41, disk 7/153, WHEA); Get-ComputerInfo, Get-HotFix; Get-MpComputerStatus; winget list --upgrade-available; sfc /verifyonly (admin).
Never run fixers (winsock reset, ipconfig /release, chkdsk /f, DISM) without a yes. PowerShell output via ConvertTo-Json; admin-only probes skipped gracefully.

## Gap
Native Windows Wi-Fi diagnosis from netsh (channel, band, placement, mesh vs extender, ISP gateway bridge mode); 3-2-1 check against what is actually configured plus a proven restore test; symptom tree with ordered safe checks and a "take it in" stop; CISA/NSA router checklist; dated-price buying advice; safe beginner homelab path (Tailscale/Tunnel over port forwarding).
