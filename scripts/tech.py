#!/usr/bin/env python3
"""techwright tech.py: read-only home IT checks (Windows first).

  tech.py net  [--json]   Wi-Fi link, gateway, internet and DNS ladder -> verdict
  tech.py disk [--json]   physical disk health, reliability counters, free space
  tech.py backup [--target D] [--restore-test F --original F]  3-2-1 table; restore test writes to temp only
  tech.py health [--json] 7-day critical events, Defender, next checks

Nothing here changes the machine. Probes that need admin are marked and skipped;
fixes are printed as suggestions, never run.
"""
import argparse
import json
import re
import shutil
import socket
import string
import subprocess
import sys

IS_WIN = sys.platform == "win32"


def run(cmd, timeout=20):
    """Run a command, return (code, stdout+stderr). Never raises."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.TimeoutExpired) as e:
        return -1, str(e)


# ---------- parsers (pure, fixture-tested) ----------

def parse_wlan_interfaces(text):
    """netsh wlan show interfaces -> list of dicts (lower-case keys)."""
    out, cur = [], None
    for line in text.splitlines():
        m = re.match(r"^\s{2,}([A-Za-z][\w ()/\-.]*?)\s+:\s?(.*)$", line)
        if not m:
            continue
        key, val = m.group(1).strip().lower(), m.group(2).strip()
        if key == "name":
            cur = {}
            out.append(cur)
        if cur is not None:
            cur.setdefault(key, val)
    for d in out:
        if "signal" in d:
            d["signal_pct"] = int(re.sub(r"\D", "", d["signal"]) or 0)
    return out


def parse_ipconfig_gateways(text):
    """ipconfig -> [(adapter, ipv4, gateway)] for adapters with an IPv4 gateway."""
    res, adapter, ip, expect_gw = [], None, None, False
    for line in text.splitlines():
        if line and not line.startswith(" ") and line.rstrip().endswith(":"):
            adapter, ip, expect_gw = line.rstrip(":").strip(), None, False
            continue
        m = re.search(r"IPv4 Address[ .]*: ([\d.]+)", line)
        if m:
            ip = m.group(1)
        if "Default Gateway" in line:
            expect_gw = True
        if expect_gw:
            g = re.search(r"(\d+\.\d+\.\d+\.\d+)\s*$", line)
            if g:
                res.append((adapter, ip, g.group(1)))
                expect_gw = False
            elif "Default Gateway" not in line and line.strip() and ":" in line:
                expect_gw = False
    return res


def parse_ping(text):
    """ping output (Windows or POSIX) -> {'loss_pct', 'avg_ms'}."""
    loss = re.search(r"\((\d+)% loss\)|(\d+(?:\.\d+)?)% packet loss", text)
    avg = re.search(r"Average = (\d+)ms|= [\d.]+/([\d.]+)/", text)
    return {
        "loss_pct": float(next(g for g in loss.groups() if g)) if loss else 100.0,
        "avg_ms": float(next(g for g in avg.groups() if g)) if avg else None,
    }


def net_verdict(wifi, gateway, gw_ping, inet_ping, dns_ok):
    """Ladder: link -> local network -> internet -> DNS. Returns (verdict, advice list)."""
    advice = []
    if wifi and wifi.get("state") == "connected":
        sig = wifi.get("signal_pct", 0)
        if sig < 40:
            advice.append(f"Wi-Fi signal {sig}% is weak: move closer, lift the router off the floor, "
                          "or add a wired mesh node; prefer 5/6 GHz near the router, 2.4 GHz for range.")
    if not gateway:
        return "no-link", ["No adapter has a default gateway: check the cable or Wi-Fi connection, "
                           "then restart the router."] + advice
    if gw_ping["loss_pct"] >= 50:
        return "local-network", ["The router does not answer: power-cycle router (30 s off), "
                                 "check the cable or Wi-Fi association."] + advice
    if gw_ping["loss_pct"] > 0 or (gw_ping["avg_ms"] or 0) > 30:
        advice.append("Loss or lag to your own router points at Wi-Fi interference or a bad cable, not the ISP.")
    if inet_ping["loss_pct"] >= 50:
        return "isp", ["Router answers but the internet does not: check the modem/ISP box lights "
                       "and the ISP's outage page before changing settings."] + advice
    if not dns_ok:
        return "dns", ["Internet answers by IP but names do not resolve: restart the router or set "
                       "DNS to 1.1.1.1 / 9.9.9.9 on the router."] + advice
    if inet_ping["loss_pct"] > 0 or (inet_ping["avg_ms"] or 0) > 100:
        return "degraded", ["Internet works with loss or lag; if the router hop is clean, raise it with the ISP."] + advice
    return "ok", advice


DISK_PS = (
    "$d=Get-PhysicalDisk | Select-Object DeviceId,FriendlyName,MediaType,BusType,HealthStatus,"
    "OperationalStatus,Size; $r=$null; try { $r=Get-PhysicalDisk | Get-StorageReliabilityCounter "
    "-ErrorAction Stop | Select-Object DeviceId,Temperature,Wear,ReadErrorsUncorrected,"
    "WriteErrorsUncorrected,PowerOnHours } catch { $r='ADMIN' }; "
    "@{disks=@($d);reliability=$r} | ConvertTo-Json -Depth 4 -Compress"
)


def disk_findings(data):
    """Parsed DISK_PS JSON -> (rows, findings, admin_needed)."""
    rel = data.get("reliability")
    admin = rel == "ADMIN"
    relmap = {}
    if isinstance(rel, dict):
        rel = [rel]
    if isinstance(rel, list):
        relmap = {str(r.get("DeviceId")): r for r in rel}
    rows, findings = [], []
    for d in data.get("disks") or []:
        r = relmap.get(str(d.get("DeviceId")), {})
        name = d.get("FriendlyName", "?")
        row = {"name": name, "media": d.get("MediaType"), "health": d.get("HealthStatus"),
               "size_gb": round((d.get("Size") or 0) / 1e9), "temp_c": r.get("Temperature"),
               "wear_pct": r.get("Wear"), "power_on_h": r.get("PowerOnHours"),
               "uncorrected": (r.get("ReadErrorsUncorrected") or 0) + (r.get("WriteErrorsUncorrected") or 0)}
        rows.append(row)
        if row["health"] not in (None, "Healthy"):
            findings.append(f"STOP: {name} reports {row['health']}. Back up now, before anything else; "
                            "then replace the drive.")
        if row["uncorrected"]:
            findings.append(f"STOP: {name} has {row['uncorrected']} uncorrected errors. Back up now.")
        if (row["wear_pct"] or 0) >= 80:
            findings.append(f"{name} is {row['wear_pct']}% worn: plan a replacement.")
        if (row["temp_c"] or 0) >= 70:
            findings.append(f"{name} runs at {row['temp_c']} C: check airflow or add a heatsink.")
    return rows, findings, admin


def free_space():
    rows = []
    roots = [f"{c}:\\" for c in string.ascii_uppercase] if IS_WIN else ["/"]
    for root in roots:
        try:
            u = shutil.disk_usage(root)
        except OSError:
            continue
        rows.append({"volume": root, "total_gb": round(u.total / 1e9),
                     "free_pct": round(100 * u.free / u.total, 1) if u.total else 0})
    return rows


# ---------- commands ----------

def cmd_net(args):
    if not IS_WIN:
        return {"error": "net: only Windows is supported so far"}
    _, wl = run(["netsh", "wlan", "show", "interfaces"])
    wifi = next((w for w in parse_wlan_interfaces(wl) if w.get("state") == "connected"), None)
    _, ipc = run(["ipconfig"])
    gws = parse_ipconfig_gateways(ipc)
    gateway = gws[0][2] if gws else None
    gw_ping = parse_ping(run(["ping", "-n", "4", gateway])[1]) if gateway else {"loss_pct": 100.0, "avg_ms": None}
    inet_ping = parse_ping(run(["ping", "-n", "4", "1.1.1.1"])[1])
    try:
        socket.getaddrinfo("example.com", 443)
        dns_ok = True
    except OSError:
        dns_ok = False
    verdict, advice = net_verdict(wifi, gateway, gw_ping, inet_ping, dns_ok)
    w = None
    if wifi:
        w = {k: wifi.get(k) for k in ("ssid", "radio type", "band", "channel", "signal_pct",
                                      "receive rate (mbps)", "transmit rate (mbps)")}
    return {"verdict": verdict, "wifi": w, "gateways": gws, "gateway_ping": gw_ping,
            "internet_ping": inet_ping, "dns_ok": dns_ok, "advice": advice}


def cmd_disk(args):
    out = {"free_space": free_space(), "disks": [], "findings": [], "admin_needed": []}
    for v in out["free_space"]:
        if v["free_pct"] < 10:
            out["findings"].append(f"{v['volume']} has {v['free_pct']}% free: clear space (Storage Sense, "
                                   "Disk Cleanup) before it slows updates.")
    if IS_WIN:
        code, txt = run(["powershell", "-NoProfile", "-Command", DISK_PS], timeout=60)
        try:
            rows, findings, admin = disk_findings(json.loads(txt[txt.index("{"):]))
            out["disks"], out["findings"] = rows, out["findings"] + findings
            if admin:
                out["admin_needed"].append("reliability counters (temperature, wear, errors): rerun as admin")
        except ValueError:
            out["findings"].append("Could not read Get-PhysicalDisk output.")
    if shutil.which("smartctl"):
        out["smartctl"] = "present: run `smartctl -H /dev/sdX` (admin) for SMART health"
    return out


BACKUP_PS = (
    "$fh=$null; try { $fh=(Get-CimInstance -Namespace root/Microsoft/Windows/FileHistory "
    "-ClassName MSFT_FhConfigInfo -ErrorAction Stop | Select-Object -First 1 | ConvertTo-Json -Compress) } catch {}; "
    "$od=[bool]$env:OneDrive -and (Test-Path $env:OneDrive); "
    "$wb=$null; $o=& wbadmin get versions 2>&1 | Out-String; if ($o -match 'denied|elevat') { $wb='ADMIN' } "
    r"elseif ($o -match 'Backup time: ([^\r\n]+)') { $wb=$matches[1] }; "
    "@{filehistory=$fh; onedrive=$od; onedrive_path=$env:OneDrive; wbadmin=$wb} | ConvertTo-Json -Compress"
)


def backup_table(state, extra_targets=()):
    """state from BACKUP_PS (or a fixture) -> (table, findings, admin_needed).

    A copy counts only when it is configured, not merely installed."""
    copies = [{"copy": "original", "media": "this PC", "offsite": False}]
    findings, admin = [], []
    if state.get("filehistory"):
        copies.append({"copy": "File History", "media": "external/network drive", "offsite": False})
    if state.get("onedrive"):
        copies.append({"copy": "OneDrive (synced folders)", "media": "cloud", "offsite": True})
        findings.append("OneDrive sync is not a true backup: deletions and ransomware sync too. "
                        "Count it off-site only after checking version history / Recycle Bin restore.")
    wb = state.get("wbadmin")
    if wb == "ADMIN":
        admin.append("wbadmin system-image versions: rerun as admin")
    elif wb:
        copies.append({"copy": f"system image ({wb})", "media": "backup drive", "offsite": False})
    for t in extra_targets:
        copies.append({"copy": f"declared target {t}", "media": f"declared:{t}", "offsite": False})
    n, media = len(copies), {c["media"] for c in copies}
    off = any(c["offsite"] for c in copies)
    if n < 3:
        findings.append(f"Only {n} cop{'y' if n == 1 else 'ies'} found; 3-2-1 needs 3.")
    if len(media) < 2:
        findings.append("All copies sit on one kind of media; add an external drive or cloud.")
    if not off:
        findings.append("No off-site copy: fire, theft or ransomware takes everything. Add a cloud backup.")
    verdict = "3-2-1 met" if n >= 3 and len(media) >= 2 and off else "gaps"
    return {"verdict": verdict, "copies": copies}, findings, admin


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def restore_test(backup_copy, original=None):
    """Copy one file out of the backup into a new temp dir and compare hashes. Writes only to temp."""
    import os
    import tempfile
    if not os.path.isfile(backup_copy):
        return {"restore_test": "fail", "reason": f"{backup_copy} is not a readable file in the backup"}
    d = tempfile.mkdtemp(prefix="techwright-restore-")
    dst = os.path.join(d, os.path.basename(backup_copy))
    shutil.copy2(backup_copy, dst)
    got = sha256(dst)
    res = {"restore_test": "pass", "restored_to": dst, "sha256": got}
    if got != sha256(backup_copy):
        res.update(restore_test="fail", reason="restored copy differs from the backup copy")
    elif original and os.path.isfile(original) and sha256(original) != got:
        res.update(restore_test="differs",
                   reason="restored file differs from the current original (changed since the backup?)")
    return res


def cmd_backup(args):
    state = {}
    if IS_WIN:
        _, txt = run(["powershell", "-NoProfile", "-Command", BACKUP_PS], timeout=60)
        try:
            state = json.loads(txt[txt.index("{"):])
        except ValueError:
            state = {}
    table, findings, admin = backup_table(state, args.target or [])
    out = {**table, "findings": findings, "admin_needed": admin}
    if args.restore_test:
        out["restore"] = restore_test(args.restore_test, args.original)
    else:
        out["findings"].append("No restore tested: run tech.py backup --restore-test <file in backup> "
                               "--original <same file on PC>. A backup never restored is a hope.")
    return out


HEALTH_PS = (
    "$ev=@(Get-WinEvent -FilterHashtable @{LogName='System';Level=1,2;StartTime=(Get-Date).AddDays(-7)} "
    "-MaxEvents 300 -ErrorAction SilentlyContinue | Group-Object ProviderName,Id | Sort-Object Count -Desc | "
    "Select-Object -First 10 @{n='key';e={$_.Name}},Count); "
    "$mp=$null; try { $mp=Get-MpComputerStatus -ErrorAction Stop | Select-Object AntivirusEnabled,"
    "RealTimeProtectionEnabled,AntivirusSignatureAge } catch {}; "
    "$bat=@(Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue).Count; "
    "$up=$null; try { $up=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToString('o') } catch {}; "
    "@{events=$ev; defender=$mp; batteries=$bat; last_boot=$up} | ConvertTo-Json -Depth 4 -Compress"
)

KNOWN_EVENTS = {
    "Microsoft-Windows-Kernel-Power, 41": "unexpected shutdowns (power loss, PSU, overheating or a crash).",
    "disk, 7": "STOP: bad blocks on a disk. Back up now, then run tech.py disk.",
    "disk, 153": "disk I/O retries: check the cable or port, then tech.py disk.",
    "Microsoft-Windows-WHEA-Logger, 1": "hardware error (WHEA): check temperatures, RAM and overclocks.",
    "Microsoft-Windows-WHEA-Logger, 18": "fatal hardware error (WHEA): take it in if it repeats.",
    "Microsoft-Windows-WindowsUpdateClient, 20": "Windows Update installs failing: Settings > Windows Update > "
    "Update history shows the KB; run the Windows Update troubleshooter.",
    "Ntfs, 55": "file system corruption: back up, then chkdsk (ask first; needs a reboot).",
}


def health_findings(data):
    findings = []
    ev = data.get("events") or []
    if isinstance(ev, dict):
        ev = [ev]
    for e in ev:
        note = KNOWN_EVENTS.get(e.get("key"))
        if note:
            findings.append(f"{e.get('key')} x{e.get('Count')}: {note}")
    mp = data.get("defender")
    if isinstance(mp, dict):
        if not mp.get("RealTimeProtectionEnabled"):
            findings.append("Defender real-time protection is off (fine only if another antivirus is active).")
        if (mp.get("AntivirusSignatureAge") or 0) > 7:
            findings.append(f"Defender signatures are {mp['AntivirusSignatureAge']} days old: run Windows Update.")
    return findings


def cmd_health(args):
    if not IS_WIN:
        return {"error": "health: only Windows is supported so far"}
    _, txt = run(["powershell", "-NoProfile", "-Command", HEALTH_PS], timeout=90)
    try:
        data = json.loads(txt[txt.index("{"):])
    except ValueError:
        return {"error": "could not read event/Defender output"}
    out = {"last_boot": data.get("last_boot"), "top_errors_7d": data.get("events"),
           "defender": data.get("defender"), "findings": health_findings(data),
           "next": ["tech.py disk for drive health"]}
    if data.get("batteries"):
        out["next"].append(r"powercfg /batteryreport /output %TEMP%\battery.html (writes one report file): "
                           "design vs full-charge capacity")
    if shutil.which("winget"):
        out["next"].append("winget upgrade (lists pending app updates; install only with a yes)")
    out["next"].append("For a scored all-round checkup use desktop-commander's computer-health-check if installed.")
    return out


def emit(res, as_json):
    if as_json:
        print(json.dumps(res, indent=2))
        return
    for k, v in res.items():
        if isinstance(v, list):
            print(f"{k}:")
            for i in v:
                print(f"  - {i}")
        else:
            print(f"{k}: {v}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tech.py", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    subs = {n: sub.add_parser(n) for n in ("net", "disk", "backup", "health")}
    for s in subs.values():
        s.add_argument("--json", action="store_true")
    b = subs["backup"]
    b.add_argument("--target", action="append", help="a backup location you keep yourself (counted as a copy)")
    b.add_argument("--restore-test", metavar="FILE", help="a file inside the backup to restore to temp")
    b.add_argument("--original", metavar="FILE", help="the same file on this PC, to compare hashes")
    a = ap.parse_args(argv)
    res = {"net": cmd_net, "disk": cmd_disk, "backup": cmd_backup, "health": cmd_health}[a.cmd](a)
    emit(res, a.json)
    return 1 if "error" in res else 0


if __name__ == "__main__":
    sys.exit(main())
