#!/usr/bin/env python3
"""
skill_harvester.py — Auto-Sync Protocol (The Harvester)
Background service that pulls updates from GitHub every 5 minutes.
"""
import os
import time
import subprocess
import logging
from datetime import datetime

# Configuration
REPO_DIR = r"D:\All DATA\claude project\generat photo and video"
GITHUB_REPO = "mtrust199-del/amr-media-generator"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
REMOTE_URL = f"https://{TOKEN}@github.com/{GITHUB_REPO}.git" if TOKEN else ""
PULL_INTERVAL = 300  # 5 minutes in seconds

# Logging
log_dir = os.path.join(REPO_DIR, "config")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "harvester.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("Harvester")

def git_pull():
    try:
        os.chdir(REPO_DIR)
        # Ensure remote URL has token
        subprocess.run(
            ["git", "remote", "set-url", "origin", REMOTE_URL],
            check=True, capture_output=True
        )
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            logger.info(f"Pull successful: {result.stdout.strip()}")
            return True, result.stdout.strip()
        else:
            logger.error(f"Pull failed: {result.stderr.strip()}")
            return False, result.stderr.strip()
    except Exception as e:
        logger.error(f"Exception during pull: {e}")
        return False, str(e)

def main():
    logger.info("=== Harvester service started ===")
    print(f"[{datetime.now()}] Harvester service started")
    while True:
        success, msg = git_pull()
        status = "✅" if success else "❌"
        print(f"[{datetime.now()}] {status} {msg}")
        time.sleep(PULL_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Harvester service stopped by user")
        print("\nHarvester stopped.")
