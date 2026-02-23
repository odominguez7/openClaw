# Accessing the OpenClaw Control UI

The OpenClaw gateway exposes a web control UI for managing the WhatsApp bot and other channels. This guide explains how to access it.

## Local Access (on the server)

If you're on the same machine where OpenClaw runs:

1. Ensure the gateway is running:
   ```bash
   systemctl --user status openclaw-gateway.service
   ```

2. Open in your browser:
   - **URL:** `http://localhost:18789/`
   - **WebSocket:** `ws://localhost:18789`

3. When prompted, enter your gateway token (found in `~/.openclaw/openclaw.json` under `gateway.auth.token`).

## Remote Access (SSH port forwarding)

The gateway binds to loopback by default, so remote access requires SSH port forwarding.

### From your local machine

Run this in a terminal on your **local** Mac/PC (not on the server):

```bash
ssh -L 18789:localhost:18789 odominguez7@<your-server-hostname-or-ip>
```

Then open `http://localhost:18789/` in your local browser. Keep the SSH session open while using the UI.

### Using Cursor / VS Code Remote SSH

If you connect to the server via Cursor or VS Code Remote SSH:

1. Open the **Ports** panel: `Ctrl+Shift+P` → **Ports: Focus on Ports View**
2. Click **Forward a Port** and enter `18789`
3. Open `http://localhost:18789/` in your local browser

## Service Management

| Action | Command |
|--------|---------|
| Check status | `systemctl --user status openclaw-gateway.service` |
| Restart | `systemctl --user restart openclaw-gateway.service` |
| View logs | `journalctl --user -u openclaw-gateway -f` |
| Log file | `~/.openclaw/gateway.log` |

## Default Port

- **Gateway UI:** `18789`

To use a different port, edit `~/.openclaw/openclaw.json` under `gateway.port` and restart the service.

## WhatsApp Bot

The control UI lets you manage the WhatsApp channel (Baileys). Session data is stored in:

- `~/.openclaw/credentials/whatsapp/default/`

Channel policies (DM allowlist, group policy, etc.) are configured in `~/.openclaw/openclaw.json` under `channels.whatsapp`.
