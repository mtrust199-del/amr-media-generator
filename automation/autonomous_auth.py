"""
autonomous_auth.py – Automated authentication helper (improved)

This module is placed in the `automation/` folder and handles low‑resource
tasks: temporary‑mail verification and simple web‑login flows.
Uses Playwright (headless Chromium) to keep memory footprint small (~200 MB).
"""

import os
import json
import logging
from typing import Optional, Dict, Any

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ---------------------------------------------------------------------------
# Logging (lightweight, file + optional console)
# ---------------------------------------------------------------------------
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "auth.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
    ],
)
logger = logging.getLogger("AutonomousAuth")

# ---------------------------------------------------------------------------
# Configuration (can be overridden by config/autonomous_auth.json)
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "login_url": "https://arena.ai/login",
    "email_selector": 'input[name="email"]',
    "password_selector": 'input[name="password"]',
    "submit_selector": 'button[type="submit"]',
    "success_selector": "text=Dashboard",
    "success_timeout_ms": 30000,
    "headless": True,
}

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "autonomous_auth.json")


def _load_config() -> Dict[str, Any]:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            return {**DEFAULT_CONFIG, **user_cfg}
        except Exception as e:
            logger.warning(f"Could not load config {CONFIG_PATH}: {e}")
    return dict(DEFAULT_CONFIG)


# ---------------------------------------------------------------------------
# Core login function
# ---------------------------------------------------------------------------

def run_autonomous_auth(email: str, password: str, **kwargs) -> bool:
    """Log in to a web platform (default: Arena.ai) via Playwright.

    Returns True on success, False otherwise.
    Extra kwargs override config keys temporarily.
    """
    cfg = {**_load_config(), **kwargs}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=cfg["headless"])
            page = browser.new_page()
            logger.info(f"Opening {cfg['login_url']}")
            page.goto(cfg["login_url"], timeout=60000)

            logger.info("Filling credentials...")
            page.fill(cfg["email_selector"], email)
            page.fill(cfg["password_selector"], password)
            page.click(cfg["submit_selector"])

            logger.info("Waiting for post-login indicator...")
            page.wait_for_selector(cfg["success_selector"], timeout=cfg["success_timeout_ms"])
            logger.info("✅  Login successful – account verified and ready to use.")
            browser.close()
            return True

    except PlaywrightTimeout:
        # Capture page content and screenshot for debugging
        try:
            html_path = os.path.join(os.path.dirname(__file__), "..", "logs", "login_failure.html")
            os.makedirs(os.path.dirname(html_path), exist_ok=True)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(page.content())
            screenshot_path = os.path.join(os.path.dirname(__file__), "..", "logs", "login_failure.png")
            page.screenshot(path=screenshot_path, full_page=True)
            logger.error(f"❌  Login timed out – saved page HTML to {html_path} and screenshot to {screenshot_path}")
        except Exception as debug_err:
            logger.error(f"❌  Login timed out – also failed to capture debug info: {debug_err}")
        return False
    except Exception as e:
        logger.error(f"❌  Login failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Temp‑Mail API bridge (connects to your legacy Temp‑Mail project)
# ---------------------------------------------------------------------------

def check_temp_mail_api(email: str) -> Optional[str]:
    """Helper to fetch the latest verification code from your Temp‑Mail interface.

    Replace the stub below with actual API calls to the Temp‑Mail service
    built in your original project. Expected return: verification code (str)
    or None if not found.
    """
    logger.info(f"Checking Temp‑Mail for {email} ...")

    # ------------------------------------------------------------------
    # TODO: Insert your legacy Temp‑Mail API logic here.
    # Example (pseudo‑code):
    #   response = requests.get(f"http://localhost:5000/api/temp-mail/{email}/latest")
    #   if response.ok:
    #       data = response.json()
    #       return data.get("code") or data.get("body")
    # ------------------------------------------------------------------

    # Stub return – remove when real integration is added.
    logger.warning("check_temp_mail_api is a stub – implement me!")
    return None


# ---------------------------------------------------------------------------
# CLI entry‑point (for manual testing / Task Scheduler)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    # Read credentials from environment or fallback to args
    email = os.getenv("AUTH_EMAIL", sys.argv[1] if len(sys.argv) > 1 else "test@example.com")
    password = os.getenv("AUTH_PASSWORD", sys.argv[2] if len(sys.argv) > 2 else "your_password")

    success = run_autonomous_auth(email, password)
    if success:
        print("🔓  Authenticated successfully.")
        # After login, optionally check temp‑mail for a verification code
        code = check_temp_mail_api(email)
        if code:
            print(f"📧  Verification code received: {code}")
    else:
        print("⚠️  Authentication failed – check logs.")
        sys.exit(1)