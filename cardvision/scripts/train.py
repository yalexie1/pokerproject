"""
Fine-tune YOLOv8 on the playing card dataset.

Usage (from repo root):
  python cardvision/scripts/train.py

Model weights are saved to cardvision/runs/train/weights/best.pt.
Copy best.pt to cardvision/models/best.pt when done.
"""

import shutil
from pathlib import Path

from ultralytics import YOLO

DATASET_YAML = Path(__file__).parent.parent / "data" / "dataset.yaml"
RUNS_DIR = Path(__file__).parent.parent / "runs"
MODELS_DIR = Path(__file__).parent.parent / "models"


def main():
    model = YOLO("yolov8n.pt")  # nano pretrained on COCO; upgrade to yolov8s.pt for better accuracy

    results = model.train(
        data=str(DATASET_YAML),
        epochs=100,
        imgsz=640,
        batch=16,          # reduce to 8 if you hit memory errors
        patience=20,       # early stop after 20 epochs with no improvement
        device="mps",      # Apple Silicon GPU; change to "cpu" on Intel Mac or "0" for CUDA
        # Augmentation — tuned for card detection
        hsv_h=0.02,        # subtle hue jitter (cards have defined colors)
        hsv_s=0.6,         # saturation jitter (lighting variation)
        hsv_v=0.4,         # brightness jitter (dim/bright environments)
        degrees=15,        # rotation (tilted cards)
        flipud=0.0,        # never flip upside-down (changes card identity)
        fliplr=0.5,        # horizontal flip is fine
        mosaic=1.0,        # combine multiple cards per training image
        scale=0.5,         # zoom in/out
        translate=0.1,
        project=str(RUNS_DIR),
        name="train",
        exist_ok=True,
    )

    # Copy best weights to models/
    best_src = RUNS_DIR / "train" / "weights" / "best.pt"
    if best_src.exists():
        MODELS_DIR.mkdir(exist_ok=True)
        dest = MODELS_DIR / "best.pt"
        shutil.copy2(best_src, dest)
        print(f"\nBest model saved to: {dest}")
        print(f"mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A'):.3f}")
    else:
        print("Training complete. Locate weights in cardvision/runs/train/weights/best.pt")


if __name__ == "__main__":
    main()
