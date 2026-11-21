# Homelab and self-hosting (safe beginner path)

1. **Start small**: an old PC, mini PC or NAS; one service the owner will actually use (photos, media, file sync, backups).
2. **Back it up**: the server is not a backup of itself; give it its own 3-2-1 (backup.md).
3. **Containers**: Docker Compose keeps each service in one file that can be rebuilt; pin image versions, keep the compose files in git.
4. **Remote access without opening ports**: prefer Tailscale (a private network of your own devices; quickstart https://tailscale.com/kb/1017/install, checked 2026-11-21) or Cloudflare Tunnel (cloudflared makes outbound-only connections, so no public IP or port forward is needed; https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/, checked 2026-11-21). Port forwarding a service to the internet is the last resort, behind a reverse proxy (Caddy, Traefik, Nginx Proxy Manager) with HTTPS and updates on.
5. **Updates**: a weekly habit for the OS and images; turn on automatic security updates.
6. **Power and noise**: idle watts matter for a box that runs all year; say the yearly cost at the owner's rate.

Ideas list: awesome-selfhosted. The owner's AI servers (ComfyUI, Ollama pool) belong to labwright; router changes for the lab go through network.md's checklist.
