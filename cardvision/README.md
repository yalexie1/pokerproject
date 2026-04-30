# CardVision

Playing card detection using YOLOv8. Detects rank + suit from iPhone photos (partial or full cards) and displays results in a browser UI with broadcast-style bounding-box overlays.

## Quick Start

```bash
# 1. Set up Python environment (one-time)
cd cardvision
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Get the trained model (see Model Weights section below)
#    Place best.pt in: cardvision/models/best.pt

# 3. Start the web server
python server/app.py
# Open http://localhost:5001 — drag and drop a card photo to test
```

## Project Structure

```
cardvision/
├── data/
│   ├── raw/              # Raw iPhone photos (gitignored)
│   ├── train/            # Train split: images/ (gitignored) + labels/ (committed)
│   ├── val/              # Val split:   images/ (gitignored) + labels/ (committed)
│   └── dataset.yaml      # YOLOv8 52-class config
├── inference/
│   ├── detector.py       # CardDetector class — wraps YOLO model
│   └── overlay.py        # Draws bounding boxes onto images
├── scripts/
│   ├── organize_data.py  # Split raw/ into train/val
│   ├── train.py          # Fine-tune YOLOv8
│   └── predict.py        # CLI inference on a single image
├── server/
│   ├── app.py            # Flask web server
│   └── static/           # index.html + style.css
├── watch/
│   └── folder_watcher.py # AirDrop folder → auto-inference
└── models/
    └── best.pt           # Trained weights (gitignored)
```

## 52 Classes

Cards are named `{rank}{suit}`:
- Ranks: `2 3 4 5 6 7 8 9 T J Q K A`
- Suits: `c` (clubs), `d` (diamonds), `h` (hearts), `s` (spades)
- Examples: `Ah` = Ace of Hearts, `Kd` = King of Diamonds, `Tc` = 10 of Clubs

## Data Collection Workflow

### Option A: Roboflow (recommended for collaboration)
1. Create a free Roboflow account and a new project with 52 classes (use the names above).
2. Upload iPhone photos — both collaborators can upload and annotate simultaneously.
3. Export in **YOLOv8 format** → download → unzip into `cardvision/data/`.
4. Run `python scripts/organize_data.py` to create train/val splits.

### Option B: LabelImg (local)
1. Install: `pip install labelImg`
2. Run: `labelImg data/raw/ data/raw/ YOLO`
3. Set class list to the 52 card names.
4. Draw bounding boxes, save `.txt` label files alongside images.
5. Run `python scripts/organize_data.py` to split.

### How Many Photos?
- Minimum: ~30 photos per card (1,560 total)
- Recommended: ~60 photos per card (3,120 total)
- YOLOv8's built-in augmentation (mosaic, rotation, brightness jitter) effectively multiplies your dataset ~10x, so 40 real photos per card is sufficient for good accuracy.

### Collection Tips
For each card, vary:
- **Lighting**: natural, indoor overhead, dim
- **Angle**: straight-on, 15°, 30° rotation
- **Distance**: card fills 60% of frame, card fills 30%
- **Occlusion**: corner only, half-hidden under another card
- **Background**: felt, table, hand, desk

## Training

```bash
# From the repo root
python cardvision/scripts/train.py
```

Weights saved to `cardvision/runs/train/weights/best.pt` → automatically copied to `cardvision/models/best.pt`.

**Training settings** (edit `scripts/train.py` to adjust):
- Model: `yolov8n.pt` (nano, fast) — upgrade to `yolov8s.pt` if accuracy is insufficient
- Epochs: 100 (early stop at patience=20)
- Device: `mps` (Apple Silicon) — change to `cpu` for Intel Mac

## Running the Full System

### Web UI only (manual upload)
```bash
python cardvision/server/app.py
# Open http://localhost:5001
```

### With automatic AirDrop detection
```bash
# Terminal 1
python cardvision/watch/folder_watcher.py --watch-dir ~/Desktop/CardDrop

# Terminal 2
python cardvision/server/app.py
```

AirDrop photos from iPhone to `~/Desktop/CardDrop`. The browser auto-updates within 3 seconds.

### CLI inference (quick test)
```bash
python cardvision/scripts/predict.py --image path/to/photo.jpg
```

## Model Weights

`models/best.pt` is gitignored (too large for git). Share via:

> **Google Drive:** *(add link here once you have a trained model)*

Place the downloaded `best.pt` in `cardvision/models/`.

## Collaboration

| Area | Owner |
|------|-------|
| `scripts/`, `inference/`, `watch/` | ML/inference person |
| `server/` (Flask + UI) | Frontend person |
| `data/` annotation | Both — split the 52 cards |

**Key interface contract:** `CardDetector.detect()` returns:
```python
[{"class": "Ah", "confidence": 0.97, "bbox": [x1, y1, x2, y2]}, ...]
```
Both sides depend on this schema — agree before changing it.
