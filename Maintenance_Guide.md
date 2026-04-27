# Maintenance Guide – AMR Media Project

## 1. GitHub Auto‑Update Service
1. **Schedule**: Daily at 04:00 AM (cron or Windows Task Scheduler).
2. **Script**:
   ```bash
   #!/usr/bin/env bash
   cd "D:/All DATA/claude project"
   git fetch origin
   git reset --hard origin/main
   python -m pip install -r requirements.txt
   # Restart Flask server (adjust service name if using systemd/ NSSM)
   # Example using `pm2`:
   pm2 restart amr-media
   ```
3. **Permissions**: Ensure the account running the script has write access to the project folder.
4. **Logging**: Output saved to `logs/update.log`.

## 2. n8n Webhook Integration
- **WhatsApp**: `http://localhost:5000/webhook/whatsapp` → translates command via OpenRouter → executes locally.
- **Telegram**: `http://localhost:5000/webhook/telegram` → generates content → auto‑uploads.
- **Arena.ai**: `http://localhost:5000/webhook/arena` → automates login via Playwright.

## 3. Content Management Pipelines
- **Metadata Tagging** (OpenCV‑Lite): extracts frame‑level data and writes JSON side‑car files.
- **Thumbnail Watermarking** (MoviePy‑LowRes): adds a small overlay with branding.
- **Auto‑Upload**: uses platform agents (YouTube, TikTok) defined in `smart_agent.py`.

## 4. System‑Control Utilities
- **Backup**: `BackupManager.create_backup()` encrypts with AES‑256; stores in `backups/`.
- **Screen Streaming**: Flask route `/stream` serves screenshots captured via PyAutoGUI.

## 5. Troubleshooting
- **Server fails to start**: check `config/app.log` for errors.
- **n8n webhook not reachable**: verify firewall allows port 5000.
- **Git update fails**: ensure git is installed and `origin/main` exists.

---
*Generated per the `skiles.json` skill set and integrated with the unified AMR Media architecture.*