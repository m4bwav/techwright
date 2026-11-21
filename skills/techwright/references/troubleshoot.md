# Troubleshooting: symptom to cause

Order every check from cheapest and safest to most invasive. Ask what changed recently (update, new app, new device, a drop, a spill) before anything else.

## Safe-check order
1. Restart (a real restart, not shutdown with Fast Startup).
2. Look: cables, power, lights, heat, noise, smell.
3. Read: `tech.py health` (events), `tech.py disk`, Task Manager for the top CPU/memory/disk process.
4. Undo the recent change: uninstall the new app, roll back the last update or driver (with a yes).
5. Repair tools, with a yes: SFC/DISM, `chkdsk` (reboot), reset network.
6. Reset or reinstall: only after a verified backup (`tech.py backup --restore-test`).

## Symptom trees
- **Slow PC**: disk near full (`disk` <10% free) -> clear space; a hog in Task Manager -> close or remove it; many startup apps -> disable in Task Manager > Startup; HDD as system drive -> an SSD is the biggest upgrade; high temperature -> clean vents.
- **Random restarts or shutdowns**: Kernel-Power 41 in `health` -> power or heat; WHEA errors -> hardware (RAM, CPU, overclock); disk 7/153 -> drive. Laptops: battery report.
- **Blue screen**: note the stop code; same code repeating after a driver update -> roll back that driver; WHEA 18 repeating -> take it in.
- **Won't turn on**: other outlet and charger; hold power 30 s with battery/charger out where possible; lights but no picture -> try an external display.
- **No internet**: go to network.md and run `net`.
- **Drive clicking or STOP from `disk`**: stop using it, copy the most important files first, then replace.
- **Updates failing** (WindowsUpdateClient 20): Update history for the KB, Windows Update troubleshooter, free space, then retry.

## Take it in
Burning smell, swollen battery, liquid damage, physical cracks on a charger, a clicking drive whose data has no backup, repeated fatal hardware errors, or a fix that needs opening a laptop under warranty. Say so plainly and point to the maker's support or a local repair shop; iFixit (https://www.ifixit.com/) has free repair guides for owners who want to do it themselves.
