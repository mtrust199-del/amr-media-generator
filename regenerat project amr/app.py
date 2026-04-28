#!/usr/bin/env python
"""
Amr Media Generator - Main Flask Application (v1.0 unified)
Integrates intelligent agent, translator, backup manager, and version manager.
"""

import os
import sys
import json
import atexit
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file

# --- Internal modules with safe imports ---
try:
    from smart_agent import SmartAgent
except Exception as e:
    print(f"Warning: smart_agent not loaded: {e}")
    SmartAgent = None

try:
    from translator import ArabicTranslator
except Exception as e:
    print(f"Warning: translator not loaded: {e}")
    ArabicTranslator = None

try:
    from backup_manager import BackupManager
except Exception as e:
    print(f"Warning: backup_manager not loaded: {e}")
    BackupManager = None

try:
    from version_manager import get_current_version, update_version
except Exception as e:
    print(f"Warning: version_manager not loaded: {e}")
    def get_current_version(): return "1.0"
    def update_version(v): pass

try:
    from config_loader import ConfigLoader
except Exception as e:
    print(f"Warning: config_loader not loaded: {e}")
    ConfigLoader = None

# --- Veo 3.1 Generator ---
try:
    from veo_generator import VeoGenerator
    veo_gen = VeoGenerator()
    print("✅ Veo 3.1 Generator loaded")
except Exception as e:
    print(f"Warning: veo_generator not loaded: {e}")
    VeoGenerator = None
    veo_gen = None

# --- Chat Translation Intermediary (Free, Stable) ---
try:
    from translate import Translator
    translator_arabic = Translator()
    print("✅ Chat translation intermediary loaded (Google Translate)")
except Exception as e:
    print(f"Warning: translate not loaded: {e}")
    translator_arabic = None

# --- Configuration ---
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
MEDIA_DIR = os.path.join(BASE_DIR, "media")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
CONFIG_DIR = os.path.join(BASE_DIR, "config")

for d in (STATIC_DIR, TEMPLATES_DIR, MEDIA_DIR, BACKUP_DIR, CONFIG_DIR):
    os.makedirs(d, exist_ok=True)

# --- Messaging handler ---
try:
    from messaging_handler import whatsapp_webhook_handler
except Exception as e:
    print(f"Warning: messaging_handler not loaded: {e}")
    whatsapp_webhook_handler = None

# --- Flask App ---
app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATES_DIR)

# --- Component instances (with None checks) ---
agent = SmartAgent() if SmartAgent else None
translator = ArabicTranslator() if ArabicTranslator else None
backup = BackupManager() if BackupManager else None
config_loader = ConfigLoader.get_instance() if ConfigLoader else None

# --- In-memory platforms store (persists while server runs) ---
platforms_store = {
    "1": {"name": "يوتيوب", "platform": "youtube", "connected": False},
    "2": {"name": "جوجل ميل", "platform": "gmail", "connected": False},
    "3": {"name": "واتساب", "platform": "whatsapp", "connected": False},
    "4": {"name": "تليجرام", "platform": "telegram", "connected": False},
    "5": {"name": "arena ai", "platform": "arena", "connected": False, "login_url": "https://arena.ai/"},
}

# --- Logging ---
log_path = os.path.join(CONFIG_DIR, "app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("App")

# --- Startup/Shutdown ---
def startup():
    logger.info("Amr Media Generator v%s starting", get_current_version())
    if config_loader:
        config_loader.load_json_file(os.path.join(CONFIG_DIR, "backup.json"), watch=True)
        config_loader.load_json_file(os.path.join(CONFIG_DIR, "version.json"), watch=True)
    atexit.register(shutdown)

def shutdown():
    logger.info("Amr Media Generator shutting down")

startup()

# --- Routes ---

@app.route("/upload_to_youtube", methods=["POST"])
def upload_to_youtube():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data"}), 400
    try:
        from youtube_api import handle_upload
        result = handle_upload(data)
        return jsonify({"status": "success", "video_id": result["video_id"]})
    except Exception as e:
        logger.error(f"YouTube upload failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/whatsapp-webhook", methods=["POST"])
def whatsapp_webhook():
    from flask import request, Response
    data = request.form
    if whatsapp_webhook_handler:
        reply = whatsapp_webhook_handler(data)
    else:
        reply = "Messaging handler not available"
    # Twilio expects XML response
    twiml = f"<Response><Message>{reply}</Message></Response>"
    return Response(twiml, mimetype='application/xml')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": get_current_version()}), 200

@app.route("/get_platforms", methods=["GET"])
def get_platforms():
    # Return current state (with updated connected flags)
    return jsonify(platforms_store)

@app.route("/add_platform", methods=["POST"])
def add_platform():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data"}), 400
    new_id = str(max(int(k) for k in platforms_store.keys()) + 1 if platforms_store else 6)
    platforms_store[str(new_id)] = {
        "name": data.get("name"),
        "platform": data.get("platform", "unknown"),
        "connected": False,
        "login_url": data.get("url", "")
    }
    return jsonify({"status": "success", "id": str(new_id)})

@app.route("/login_platform/<p_id>", methods=["POST"])
def login_platform_route(p_id):
    global platforms_store
    platform = platforms_store.get(p_id)
    if not platform:
        return jsonify({"status": "error", "message": "المنصة غير موجودة"}), 404

    p_type = platform.get("platform")

    if p_type == "arena":
        # Arena.ai: mark as connected (frontend opened browser)
        platforms_store[p_id]["connected"] = True
        logger.info(f"Arena.ai (id={p_id}) marked as connected")
        return jsonify({"status": "success", "percent": 100, "platform": p_type})

    # For other platforms, run agent
    if agent:
        try:
            result = agent.process_natural_command(f"قم بتسجيل الدخول إلى {p_type}")
            platforms_store[p_id]["connected"] = True
        except Exception:
            pass
    else:
        # Simulate successful login for demo
        platforms_store[p_id]["connected"] = True

    return jsonify({"status": "success", "percent": 100, "platform": p_type})

@app.route("/process_command", methods=["POST"])
def process_command():
    data = request.json
    if not data:
        data = request.form

    raw_cmd = (data.get("command") or data.get("prompt") or "").strip()
    if not raw_cmd:
        return jsonify({"message": "يرجى كتابة أمر.", "action": "error"}), 400

    logger.info("Received command: %s", raw_cmd)

    # Translate Arabic command to English using translator (for internal processing)
    processed_cmd = raw_cmd
    if translator:
        try:
            # Use translator to understand the command
            processed_cmd = translator.translate(raw_cmd)
            logger.info(f"Translated command: {processed_cmd}")
        except Exception as e:
            logger.warning(f"Translation failed: {e}")

    # Simple response for now
    response_msg = f"تم استلام الأمر: {raw_cmd}"
    if translator:
        try:
            response_msg = translator.translate(raw_cmd)
        except Exception:
            pass

    return jsonify({
        "message": response_msg,
        "action": "success",
        "percent": 100,
        "version": get_current_version(),
    })

@app.route("/generate_nano", methods=["POST"])
def generate_nano():
    """Generate video using Nano Banana via Arena.ai"""
    data = request.json
    prompt = data.get("prompt", "") if data else ""
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    logger.info(f"Nano Banana generation request: {prompt}")

    # Generate a well-structured prompt for Arena.ai Nano Banana
    enhanced_prompt = f"""[Nano Banana Video Generation Prompt]
Original User Prompt: {prompt}

Technical Specifications:
- Resolution: 1080p HD
- Frame Rate: 30fps
- Duration: 30 seconds
- Style: Photorealistic, high-quality cinematic
- Audio: Background music (ambient)
- Format: MP4 (H.264)

Generation Parameters:
- Model: Nano Banana (Arena.ai)
- Quality: Maximum
- Seed: Random
- Sampling Steps: 50
- Guidance Scale: 7.5

Special Instructions:
- Ensure smooth transitions
- Maintain subject consistency
- Use natural lighting
- Include Arabic/English text overlays if requested

Arena.ai Direct Link: https://arena.ai/nano-banana?prompt={prompt}
"""

    return jsonify({
        "status": "success",
        "enhanced_prompt": enhanced_prompt,
        "arena_url": f"https://arena.ai/nano-banana?prompt={prompt}",
        "message": "تم تجهيز الprompt للتوليد باستخدام Nano Banana"
    })

@app.route("/get_credits", methods=["GET"])
def get_credits():
    """Redirect to Arena.ai credits page"""
    return jsonify({
        "credits_url": "https://arena.ai/credits",
        "message": "تم فتح صفحة الأرصدة"
    })

@app.route("/generate_veo", methods=["POST"])
def generate_veo():
    """Generate video using Google Veo 3.1 (user's exact API pattern)"""
    if not veo_gen:
        return jsonify({"error": "Veo 3.1 Generator not available. Check GOOGLE_API_KEY."}), 500

    data = request.json
    if not data:
        return jsonify({"error": "No JSON data"}), 400

    prompt = data.get("prompt", "")
    image_path = data.get("image")  # First frame for image-to-video
    last_frame_path = data.get("last_frame")  # Last frame for video-to-video

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    logger.info(f"Veo 3.1 generation request: {prompt[:100]}...")

    # Generate video using user's exact API pattern
    result = veo_gen.generate_video(
        prompt=prompt,
        image=image_path,
        last_frame=last_frame_path,
        duration_seconds=data.get("duration_seconds", 30),
        aspect_ratio=data.get("aspect_ratio", "16:9")
    )

    if result['success']:
        logger.info(f"Veo video generated successfully: {result.get('video_path')}")
        return jsonify({
            "status": "success",
            "video_path": result.get('video_path'),
            "message": "تم توليد الفيديو بنجاح باستخدام Veo 3.1",
            "model": "veo-3.1-generate-preview",
            "enhanced_prompt": veo_gen.enhance_prompt_for_veo(
                prompt,
                has_image=bool(image_path),
                has_last_frame=bool(last_frame_path)
            )
        })
    else:
        return jsonify({
            "status": "error",
            "message": result.get('message', 'Generation failed')
        }), 500

@app.route("/translate", methods=["POST"])
def translate_text():
    """Translation intermediary - free, stable service"""
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data"}), 400

    text = data.get("text", "")
    target_lang = data.get("target_lang", "en")  # Default: Arabic → English
    source_lang = data.get("source_lang", "ar")  # Default: Arabic

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Use googletrans (free, no API key needed)
    if translator_arabic:
        try:
            from googletrans import Translator
            translator = Translator()
            result = translator.translate(text, dest=target_lang, src=source_lang)
            return jsonify({
                "success": True,
                "original_text": text,
                "translated_text": result.text,
                "source_lang": result.src,
                "target_lang": result.dest,
                "pronunciation": result.pronunciation if hasattr(result, 'pronunciation') else None
            })
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return jsonify({"error": f"Translation failed: {str(e)}"}), 500
    else:
        # Fallback: simple echo (for testing)
        return jsonify({
            "success": True,
            "original_text": text,
            "translated_text": f"[Translation not available] {text}",
            "note": "Install googletrans: pip install googletrans"
        })

@app.route("/trigger_backup", methods=["POST"])
def trigger_backup():
    success = backup.create_backup() if backup else False
    return jsonify({"success": success, "message": "Backup triggered"})

@app.route("/version", methods=["GET"])
def version_info():
    return jsonify({
        "current_version": get_current_version(),
        "project_dir": str(BASE_DIR),
    })

# --- Media endpoints ---
@app.route("/media/<path:filename>")
def serve_media(filename):
    return send_file(os.path.join(MEDIA_DIR, filename), mimetype="image/png")

# --- Remote Control API ---
@app.route("/remote/control", methods=["POST"])
def remote_control():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data"}), 400
    cmd = data.get("command", "")
    action = data.get("action", "")
    logger.info(f"Remote control: {cmd} / {action}")
    return jsonify({
        "status": "success",
        "message": f"Command '{cmd}' received (demo mode)",
        "action": action
    })

@app.route("/remote/screenshot", methods=["GET"])
def remote_screenshot():
    return jsonify({"status": "demo", "image": None, "message": "Screenshot endpoint (demo)"})

# --- Run server ---
if __name__ == "__main__":
    print("\n" + "🚀" + "-" * 30)
    print("Amr Media Generation v{}".format(get_current_version()))
    print("Local: http://127.0.0.1:5000")
    print("-" * 30 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
