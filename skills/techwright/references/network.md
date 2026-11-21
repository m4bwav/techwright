# Wi-Fi, internet and router

## Diagnose with `tech.py net`
The ladder splits the fault: no gateway -> link (cable, Wi-Fi association); router does not answer -> local network; router answers, internet does not -> ISP or modem; IP works, names do not -> DNS. Loss or lag to your own router means Wi-Fi or cable trouble, not the ISP.

Microsoft's own first steps (https://support.microsoft.com/en-us/windows/fix-wi-fi-connection-issues-in-windows-9424a1f7-6a3b-65a6-4d78-7f07eee84d2c, checked 2026-11-21): Wi-Fi on, Airplane mode off, forget the network and reconnect, power-cycle modem and router, try the other band.

## Better Wi-Fi
- Router high, central, in the open; not in a cabinet or on the floor.
- 5/6 GHz for speed near the router; 2.4 GHz for range through walls.
- Weak signal (under ~40%) in a room you use: a mesh system with wired backhaul beats a plug-in extender, which halves speed.
- ISP combo box plus your own router: put the ISP box in bridge mode so there is one router (double NAT breaks games and calls).
- Speed tests: test wired at the router first; if wired is fine, the problem is Wi-Fi.

## Router hardening checklist
From CISA "Home Network Security" (https://www.cisa.gov/news-events/news/home-network-security, checked 2026-11-21):
1. Turn on automatic firmware updates; replace routers that no longer get them.
2. Change the default admin username and password; use a strong, unique Wi-Fi password.
3. Use WPA3 (WPA2-AES if a device cannot do WPA3); never WEP or open.
4. Turn off WPS, UPnP and remote management unless something needs them.
5. Keep the router firewall on; remove unused services.
6. Put guests and smart-home devices on a guest or IoT network.

Router setting changes need a yes, and the owner should know the admin password before anything is changed. Account and device security beyond the router belongs to shieldwright.
