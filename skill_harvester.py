#!/usr/bin/env python
"""
skill_harvester.py – Self‑Update Protocol for AMR OMNI System

1. **GitHub‑based updater**: pulls new “Skills” (modules) into the extras/ folder.
2. **Sequential Execution**: runs newly acquired skills one at a time (AMD Ryzen 5 2400G‑friendly).
3. **Dependency Auto‑Resolver**: automatically runs `pip install` for any requirements.
4. **Knowledge Sync**: queries Gemini/GPT for system improvements and logs them.
"""

import os
import sys
import json
import subprocess
import logging
from typing import List, Dict, Any, Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRAS_DIR = os.path.join(BASE_DIR, "extras")
SKILLS_JSON = os.path.join(BASE_DIR, "skiles.json")
REQUREMENTS_TXT = os.path.join(BASE_DIR, "requirements.txt")
LOG_PATH = os.path.join(BASE_DIR, "config", "skill_harvester.log")

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("SkillHarvester")


# ---------------------------------------------------------------------------
# 1. GitHub‑based skill fetcher
# ---------------------------------------------------------------------------

def fetch_new_skills(repo_url: str, branch: str = "main") -> List[str]:
    """
    Clone or pull the latest skills from a GitHub repository into extras/.
    Returns list of newly added skill module paths.
    """
    os.makedirs(EXTRAS_DIR, exist_ok=True)

    # If extras/.git exists, do a pull; otherwise clone.
    git_dir = os.path.join(EXTRAS_DIR, ".git")
    try:
        if os.path.exists(git_dir):
            logger.info("Pulling latest skills from GitHub...")
            subprocess.check_call(["git", "-C", EXTRAS_DIR, "pull", "origin", branch])
        else:
            logger.info(f"Cloning skills repo {repo_url}...")
            subprocess.check_call(["git", "clone", "-b", branch, repo_url, EXTRAS_DIR])

        # Discover new .py files
        new_skills = []
        for root, _dirs, files in os.walk(EXTRAS_DIR):
            for f in files:
                if f.endswith(".py") and not f.startswith("_"):
                    new_skills.append(os.path.join(root, f))
        logger.info(f"Discovered {len(new_skills)} skill modules")
        return new_skills

    except Exception as e:
        logger.error(f"GitHub fetch failed: {e}")
        return []


# ---------------------------------------------------------------------------
# 2. Sequential execution (low‑resource friendly)
# ---------------------------------------------------------------------------

def run_skill_sequentially(skill_path: str) -> bool:
    """
    Execute a skill module alone (one at a time) to respect 8 GB RAM.
    Returns True on success.
    """
    logger.info(f"Running skill sequentially: {skill_path}")
    try:
        # Use subprocess to isolate each skill
        subprocess.check_call([sys.executable, skill_path])
        logger.info(f"Skill {os.path.basename(skill_path)} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Skill {skill_path} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error running {skill_path}: {e}")
        return False


# ---------------------------------------------------------------------------
# 3. Dependency Auto‑Resolver
# ---------------------------------------------------------------------------

def install_dependencies(skill_path: str) -> None:
    """
    Check for a requirements.txt next to the skill or in its package.
    If none, scan the .py file for import statements and try to pip‑install missing ones.
    """
    skill_dir = os.path.dirname(skill_path)

    # Look for local requirements.txt
    local_req = os.path.join(skill_dir, "requirements.txt")
    if os.path.exists(local_req):
        logger.info(f"Installing dependencies from {local_req}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", local_req])
        return

    # Fallback: scan imports (very naive)
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Very simple: look for "import xxx" or "from xxx import"
        imports = set()
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("import "):
                imports.add(line.split()[1].split(".")[0])
            elif line.startswith("from "):
                imports.add(line.split()[1].split(".")[0])
        if imports:
            logger.info(f"Attempting to pip‑install discovered imports: {imports}")
            for pkg in imports:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                except Exception:
                    logger.warning(f"Could not install {pkg}")
    except Exception as e:
        logger.warning(f"Dependency scan failed: {e}")


# ---------------------------------------------------------------------------
# 4. Knowledge Sync – query Gemini/GPT for improvements
# ---------------------------------------------------------------------------

def knowledge_sync(query: str) -> Optional[Dict[str, Any]]:
    """
    Send a query to an LLM (Gemini via OpenRouter) and return JSON suggestions.
    Uses the ANTHROPIC_AUTH_TOKEN (OpenRouter key) from environment.
    """
    import requests

    api_key = os.getenv("ANTHROPIC_AUTH_TOKEN")
    if not api_key:
        logger.warning("No OpenRouter API key found for knowledge sync")
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [{"role": "user", "content": query}],
        "response_format": {"type": "json_object"},
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        suggestion = data["choices"][0]["message"]["content"]
        logger.info(f"Knowledge sync received: {suggestion[:200]}...")
        return json.loads(suggestion)
    except Exception as e:
        logger.error(f"Knowledge sync failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def harvest(repo_url: str = "https://github.com/yourname/skills-repo.git") -> None:
    """Full harvest cycle: fetch → install deps → run sequentially → sync knowledge."""
    logger.info("🚀 Starting skill harvest cycle...")

    # 1. Fetch new skills
    new_skills = fetch_new_skills(repo_url)
    if not new_skills:
        logger.info("No new skills to process.")
        return

    # 2. Process each skill sequentially (low‑resource)
    for skill in new_skills:
        logger.info(f"Processing skill: {os.path.basename(skill)}")

        # Install dependencies first
        install_dependencies(skill)

        # Run the skill alone
        success = run_skill_sequentially(skill)
        if not success:
            logger.warning(f"Skill {skill} failed, continuing with next...")

    # 3. Knowledge sync for system‑wide improvements
    improvement_query = (
        "Analyze the AMR OMNI System (Flask + Playwright + n8n + OpenRouter) "
        "and suggest three concrete improvements for performance, reliability, "
        "or user experience. Return JSON with keys: improvements (list), "
        "priority (high/medium/low)."
    )
    suggestions = knowledge_sync(improvement_query)
    if suggestions:
        logger.info(f"System improvement suggestions: {suggestions}")

    logger.info("✅ Skill harvest cycle complete.")


if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/mtrust199-del/amr-media-generator.git"
    harvest(repo)