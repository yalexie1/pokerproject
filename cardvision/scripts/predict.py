"""
Run card detection on a single image and save the annotated result.

Usage:
  python cardvision/scripts/predict.py --image path/to/photo.jpg
  python cardvision/scripts/predict.py --image photo.jpg --model cardvision/models/best.pt
  python cardvision/scripts/predict.py --image photo.jpg --conf 0.5
"""

import argparse
from pathlib import Path

from inference.detector import CardDetector
from inference.overlay import draw_overlay

DEFAULT_MODEL = Path(__file__).parent.parent / "models" / "best.pt"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def main():
    parser = argparse.ArgumentParser(description="Detect playing cards in an image")
    parser.add_argument("--image", required=True, help="Path to input image")
    parser.add_argument("--model", default=str(DEFAULT_MODEL), help="Path to best.pt")
    parser.add_argument("--conf", type=float, default=0.4, help="Confidence threshold (0–1)")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: image not found: {image_path}")
        return

    model_path = Path(args.model)
    if not model_path.exists():
        print(f"Error: model not found: {model_path}")
        print("Train a model first: python cardvision/scripts/train.py")
        return

    detector = CardDetector(str(model_path), conf_threshold=args.conf)
    detections = detector.detect(str(image_path))

    if not detections:
        print("No cards detected.")
    else:
        print(f"Detected {len(detections)} card(s):")
        for d in detections:
            print(f"  {d['class']:4s}  conf={d['confidence']:.2f}  bbox={d['bbox']}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    result_path = OUTPUT_DIR / f"{image_path.stem}_annotated{image_path.suffix}"
    annotated = draw_overlay(str(image_path), detections)
    annotated.save(str(result_path))
    print(f"\nAnnotated image saved to: {result_path}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
