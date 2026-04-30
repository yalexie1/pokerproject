"""
Flask web server for the PokerVision card detection UI.

Routes:
  GET  /                   → serve index.html
  GET  /api/latest         → return latest.json detections
  GET  /api/status         → watcher health / model status
  POST /api/upload         → accept drag-and-drop image, run inference, return detections
  GET  /static/results/<f> → serve annotated result images (via Flask static)

Run:
  python cardvision/server/app.py
  Open http://localhost:5001
"""

import json
import sys
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Allow imports from the cardvision package
sys.path.insert(0, str(Path(__file__).parent.parent))

from inference.detector import CardDetector
from inference.overlay import draw_overlay, card_list_text

STATIC_DIR = Path(__file__).parent / "static"
RESULTS_DIR = STATIC_DIR / "results"
LATEST_JSON = STATIC_DIR / "latest.json"
DEFAULT_MODEL = Path(__file__).parent.parent / "models" / "best.pt"
UPLOAD_DIR = STATIC_DIR / "uploads"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")
CORS(app)

# Load model once at startup (None if model file doesn't exist yet)
_detector: CardDetector | None = None


def get_detector() -> CardDetector | None:
    global _detector
    if _detector is None and DEFAULT_MODEL.exists():
        _detector = CardDetector(str(DEFAULT_MODEL))
    return _detector


@app.route("/")
def index():
    return send_from_directory(str(STATIC_DIR), "index.html")


@app.route("/api/latest")
def api_latest():
    if not LATEST_JSON.exists():
        return jsonify({"detections": [], "image_filename": None, "timestamp": None})
    return jsonify(json.loads(LATEST_JSON.read_text()))


@app.route("/api/status")
def api_status():
    detector = get_detector()
    return jsonify({
        "model_loaded": detector is not None,
        "model_path": str(DEFAULT_MODEL),
        "latest_result": LATEST_JSON.exists(),
    })


@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "image" not in request.files:
        return jsonify({"error": "No image field in request"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    detector = get_detector()
    if detector is None:
        return jsonify({"error": "Model not loaded. Train a model first."}), 503

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix.lower() or ".jpg"
    upload_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    file.save(str(upload_path))

    try:
        detections = detector.detect(str(upload_path))
        annotated = draw_overlay(str(upload_path), detections)

        result_name = f"result_{uuid.uuid4().hex[:8]}.jpg"
        annotated.save(str(RESULTS_DIR / result_name))

        payload = {
            "timestamp": int(time.time()),
            "image_filename": result_name,
            "source_filename": file.filename,
            "detections": detections,
            "card_summary": card_list_text(detections),
        }
        LATEST_JSON.write_text(json.dumps(payload, indent=2))
        return jsonify(payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        upload_path.unlink(missing_ok=True)


if __name__ == "__main__":
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print("PokerVision server starting at http://localhost:5001")
    if not DEFAULT_MODEL.exists():
        print(f"  Warning: model not found at {DEFAULT_MODEL}")
        print("  Train a model first, or place best.pt in cardvision/models/")
    app.run(host="0.0.0.0", port=5001, debug=False)
