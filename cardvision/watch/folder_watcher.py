"""
Watch a folder for new iPhone photos and run card detection automatically.

Usage:
  python cardvision/watch/folder_watcher.py --watch-dir ~/Desktop/CardDrop
  python cardvision/watch/folder_watcher.py --watch-dir ~/Desktop/CardDrop --model cardvision/models/best.pt

When a new image appears, the watcher:
  1. Waits 800ms (AirDrop writes are not atomic)
  2. Runs YOLOv8 inference
  3. Saves annotated result to cardvision/server/static/results/
  4. Writes cardvision/server/static/latest.json for the web UI
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers import Observer

SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR.parent / "server" / "static" / "results"
LATEST_JSON = SCRIPT_DIR.parent / "server" / "static" / "latest.json"
DEFAULT_MODEL = SCRIPT_DIR.parent / "models" / "best.pt"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic"}
SETTLE_DELAY = 0.8  # seconds to wait after file creation before reading


class CardDetectionHandler(FileSystemEventHandler):
    def __init__(self, model_path: str):
        super().__init__()
        from inference.detector import CardDetector
        from inference.overlay import draw_overlay
        self._detect = CardDetector(model_path).detect
        self._draw = draw_overlay
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() not in IMAGE_EXTS:
            return
        time.sleep(SETTLE_DELAY)
        self._process(path)

    def _process(self, image_path: Path):
        print(f"Processing {image_path.name}...")
        try:
            detections = self._detect(str(image_path))
            annotated = self._draw(str(image_path), detections)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_name = f"result_{timestamp}.jpg"
            annotated.save(str(RESULTS_DIR / result_name))

            payload = {
                "timestamp": int(time.time()),
                "image_filename": result_name,
                "source_filename": image_path.name,
                "detections": detections,
            }
            LATEST_JSON.write_text(json.dumps(payload, indent=2))

            cards = [d["class"] for d in detections]
            print(f"  Detected: {cards or 'none'} → {result_name}")
        except Exception as e:
            print(f"  Error processing {image_path.name}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Watch a folder for card photos")
    parser.add_argument("--watch-dir", required=True, help="Folder to watch for new images")
    parser.add_argument("--model", default=str(DEFAULT_MODEL), help="Path to best.pt")
    args = parser.parse_args()

    watch_dir = Path(args.watch_dir).expanduser()
    watch_dir.mkdir(parents=True, exist_ok=True)

    model_path = Path(args.model)
    if not model_path.exists():
        print(f"Model not found: {model_path}")
        print("Train first: python cardvision/scripts/train.py")
        return

    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    handler = CardDetectionHandler(str(model_path))
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()
    print(f"Watching {watch_dir} for new photos. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
