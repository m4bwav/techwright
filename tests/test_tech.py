import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import tech  # noqa: E402

WLAN = """
There is 1 interface on the system:

    Name                   : Wi-Fi
    Description            : Example Wi-Fi 7 Adapter
    State                  : connected
    SSID                   : HomeNet
    Radio type             : 802.11ax
    Band                   : 5 GHz
    Channel                : 36
    Receive rate (Mbps)    : 864.6
    Transmit rate (Mbps)   : 720.6
    Signal                 : 31%
"""

IPCONFIG = """
Windows IP Configuration


Unknown adapter Tailscale:

   IPv4 Address. . . . . . . . . . . : 100.64.0.9
   Default Gateway . . . . . . . . . :

Ethernet adapter Ethernet:

   Connection-specific DNS Suffix  . : lan
   IPv4 Address. . . . . . . . . . . : 192.168.0.42
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : fe80::1%7
                                       192.168.0.1
"""

PING_OK = """Ping statistics for 1.1.1.1:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 9ms, Maximum = 12ms, Average = 10ms"""
PING_DEAD = """Ping statistics for 1.1.1.1:
    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),"""
PING_POSIX = "4 packets transmitted, 4 received, 0% packet loss, time 3004ms\nrtt min/avg/max/mdev = 9.1/10.5/12.0/1.0 ms"

OK = {"loss_pct": 0.0, "avg_ms": 5.0}
DEAD = {"loss_pct": 100.0, "avg_ms": None}


class Parsers(unittest.TestCase):
    def test_wlan(self):
        w = tech.parse_wlan_interfaces(WLAN)[0]
        self.assertEqual(w["state"], "connected")
        self.assertEqual(w["channel"], "36")
        self.assertEqual(w["signal_pct"], 31)

    def test_gateway_skips_empty_and_ipv6(self):
        self.assertEqual(tech.parse_ipconfig_gateways(IPCONFIG),
                         [("Ethernet adapter Ethernet", "192.168.0.42", "192.168.0.1")])

    def test_ping(self):
        self.assertEqual(tech.parse_ping(PING_OK), {"loss_pct": 0.0, "avg_ms": 10.0})
        self.assertEqual(tech.parse_ping(PING_DEAD)["loss_pct"], 100.0)
        self.assertEqual(tech.parse_ping(PING_POSIX), {"loss_pct": 0.0, "avg_ms": 10.5})


class Verdicts(unittest.TestCase):
    def test_ladder(self):
        self.assertEqual(tech.net_verdict(None, None, DEAD, DEAD, False)[0], "no-link")
        self.assertEqual(tech.net_verdict(None, "g", DEAD, DEAD, False)[0], "local-network")
        self.assertEqual(tech.net_verdict(None, "g", OK, DEAD, False)[0], "isp")
        self.assertEqual(tech.net_verdict(None, "g", OK, OK, False)[0], "dns")
        self.assertEqual(tech.net_verdict(None, "g", OK, OK, True), ("ok", []))

    def test_weak_signal_advice(self):
        wifi = tech.parse_wlan_interfaces(WLAN)[0]
        v, adv = tech.net_verdict(wifi, "g", OK, OK, True)
        self.assertEqual(v, "ok")
        self.assertTrue(any("weak" in a for a in adv))


class Disk(unittest.TestCase):
    def test_admin_needed(self):
        rows, f, admin = tech.disk_findings({"disks": [{"DeviceId": "0", "FriendlyName": "SSD",
                                             "HealthStatus": "Healthy", "Size": 2e12}],
                                             "reliability": "ADMIN"})
        self.assertTrue(admin)
        self.assertEqual(f, [])
        self.assertEqual(rows[0]["size_gb"], 2000)

    def test_stop_findings(self):
        data = {"disks": [{"DeviceId": "1", "FriendlyName": "HDD", "HealthStatus": "Warning"}],
                "reliability": {"DeviceId": "1", "Wear": 85, "Temperature": 72,
                                "ReadErrorsUncorrected": 3, "WriteErrorsUncorrected": 0}}
        _, f, admin = tech.disk_findings(data)
        self.assertFalse(admin)
        self.assertEqual(sum(x.startswith("STOP") for x in f), 2)
        self.assertTrue(any("worn" in x for x in f) and any("airflow" in x for x in f))


if __name__ == "__main__":
    unittest.main()
