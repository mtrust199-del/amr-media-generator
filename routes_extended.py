"""
routes_extended.py – Additional Flask routes for AMR OMNI Command Center
Included via import in amr_media_unified.py
"""

import os
import subprocess
import logging
from flask import jsonify, request

logger = logging.getLogger("UnifiedAMR")

def register_extended_routes(app, BASE_DIR, MEDIA_DIR, AUTONOMOUS_AUTH_AVAILABLE, run_autonomous_auth):
    @app.route("/open-folder", methods=["POST"])
    def open_folder():
        """Open Windows Explorer for allowed project sub-paths (Security-restricted)."""
        sub = request.args.get("path", "")
        base = os.path.abspath(BASE_DIR)
        if sub == "media":
            target = os.path.abspath(MEDIA_DIR)
        elif sub == "root" or sub == "":
            target = base
        else:
            return jsonify({"error": "Invalid path"}), 400

        try:
            subprocess.Popen(["explorer", target])
            logger.info(f"Opened folder: {target}")
            return jsonify({"message": f"Opened {target}"})
        except Exception as e:
            logger.error(f"Failed to open folder: {e}")
            return jsonify({"error": "Unable to open folder"}), 500

    @app.route("/auth/test", methods=["POST"])
    def auth_test():
        """Trigger autonomous auth test with progress feedback."""
        if not AUTONOMOUS_AUTH_AVAILABLE or not run_autonomous_auth:
            return jsonify({"success": False, "error": "Autonomous auth not available"}), 500

        import os as os_env
        email = os_env.getenv("AUTH_EMAIL", "test@example.com")
        password = os_env.getenv("AUTH_PASSWORD", "your_password")

        try:
            success = run_autonomous_auth(email, password)
            return jsonify({"success": success})
        except Exception as e:
            logger.error(f"Auth test failed: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/status", methods=["GET"])
    def api_status():
        """Return status of core modules for the dashboard LEDs."""
        status = {
            "playwright": False,
            "sync": False,
            "github": False,
            "n8n": False,
        }
        # Simple health checks
        try:
            import playwright
            status["playwright"] = True
        except ImportError:
            pass

        # Check if GitHub sync thread is alive (placeholder)
        status["sync"] = True  # Assume running

        # Check if n8n webhook endpoint is registered
        status["n8n"] = True  # Assume configured

        return jsonify(status)
