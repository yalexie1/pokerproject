"""
Organize annotated images into YOLOv8 train/val splits.

Usage:
  python cardvision/scripts/organize_data.py

Expects:
  - cardvision/data/raw/{class_name}/*.jpg (one folder per card class)
  OR
  - cardvision/data/raw/images/*.jpg  with cardvision/data/raw/labels/*.txt  (flat layout)

Writes:
  - cardvision/data/train/images/  and  cardvision/data/train/labels/
  - cardvision/data/val/images/    and  cardvision/data/val/labels/

Images are copied (not moved). Labels must have the same stem as the image.
"""

import os
import shutil
import random
from pathlib import Path

VAL_SPLIT = 0.2
SEED = 42

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"


def collect_pairs(raw_dir: Path) -> list[tuple[Path, Path]]:
    """Return (image_path, label_path) pairs from raw_dir."""
    pairs = []
    image_exts = {".jpg", ".jpeg", ".png"}

    # Support flat layout: raw/images/*.jpg + raw/labels/*.txt
    flat_images = raw_dir / "images"
    flat_labels = raw_dir / "labels"
    if flat_images.exists():
        for img in flat_images.iterdir():
            if img.suffix.lower() in image_exts:
                label = flat_labels / (img.stem + ".txt")
                if label.exists():
                    pairs.append((img, label))
        return pairs

    # Support class-folder layout: raw/{class_name}/*.jpg
    # Labels sit alongside the images as same-stem .txt files
    for class_dir in raw_dir.iterdir():
        if not class_dir.is_dir():
            continue
        for img in class_dir.iterdir():
            if img.suffix.lower() in image_exts:
                label = img.with_suffix(".txt")
                if label.exists():
                    pairs.append((img, label))
    return pairs


def split_and_copy(pairs: list[tuple[Path, Path]], data_dir: Path, val_split: float):
    random.seed(SEED)
    random.shuffle(pairs)
    n_val = max(1, int(len(pairs) * val_split))
    splits = {"val": pairs[:n_val], "train": pairs[n_val:]}

    for split, split_pairs in splits.items():
        img_out = data_dir / split / "images"
        lbl_out = data_dir / split / "labels"
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)
        for img, lbl in split_pairs:
            shutil.copy2(img, img_out / img.name)
            shutil.copy2(lbl, lbl_out / lbl.name)
        print(f"  {split}: {len(split_pairs)} images")


def main():
    pairs = collect_pairs(RAW_DIR)
    if not pairs:
        print(f"No labeled image/label pairs found in {RAW_DIR}")
        print("Each image (.jpg/.png) needs a matching .txt label in YOLO format.")
        return

    print(f"Found {len(pairs)} labeled pairs. Splitting {1-VAL_SPLIT:.0%}/{VAL_SPLIT:.0%} train/val...")
    split_and_copy(pairs, DATA_DIR, VAL_SPLIT)
    print("Done. Run scripts/train.py to start training.")


if __name__ == "__main__":
    main()
