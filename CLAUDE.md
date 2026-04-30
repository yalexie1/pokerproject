# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Two components live in this repo:

1. **`poker.html`** — A self-contained Texas Hold'em poker game (HTML + CSS + JS, no external dependencies).
2. **`cardvision/`** — A Python computer vision system that detects playing cards in iPhone photos using YOLOv8 and displays results in a browser UI with bounding-box overlays.

## Running the Poker Game

No build step required. Open directly in a browser:

```
open poker.html
```

## CardVision — Card Detection Subsystem

### Setup (one-time)

```bash
cd cardvision
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the System

Two terminal processes are needed simultaneously:

```bash
# Terminal 1 — watch a folder for new iPhone photos (AirDrop target)
python cardvision/watch/folder_watcher.py --watch-dir ~/Desktop/CardDrop

# Terminal 2 — start the web UI
python cardvision/server/app.py
# Then open http://localhost:5001
```

You can also drag and drop photos directly in the browser without the watcher.

### Training a Model

1. Collect and annotate iPhone photos (see `cardvision/README.md` for the full workflow).
2. Place annotated images + YOLO `.txt` labels in `cardvision/data/raw/`.
3. Run `python cardvision/scripts/organize_data.py` to create train/val splits.
4. Run `python cardvision/scripts/train.py` — weights saved to `cardvision/runs/train/weights/best.pt`.
5. Copy `best.pt` to `cardvision/models/best.pt`.

### Quick Single-Image Test

```bash
python cardvision/scripts/predict.py --image path/to/photo.jpg
```

### Large Files Policy

The following are **gitignored** — share via the Google Drive link in `cardvision/README.md`:
- `cardvision/data/raw/` — raw iPhone photos
- `cardvision/data/train/images/` and `cardvision/data/val/images/` — annotated images
- `cardvision/models/*.pt` — trained model weights
- `cardvision/runs/` — YOLOv8 training output

Only commit: YOLO label `.txt` files, `dataset.yaml`, and Python source code.

## Git & GitHub Workflow

This project uses Git with a remote on GitHub (`yalexie1/pokerproject`). **After every meaningful change, commit and push.**

### Rules
- Commit after every meaningful unit of work (new feature, bug fix, refactor, content update).
- Never batch unrelated changes into a single commit.
- Push to `origin main` immediately after committing — do not let commits pile up locally.
- Write clean, concise commit messages in the imperative mood: `Add X`, `Fix Y`, `Remove Z`.
- Never use `--no-verify` or force-push unless the user explicitly requests it.

### Workflow
```bash
git add <specific files>
git commit -m "Short imperative description"
git push origin main
```

### Large File Rule
Never commit files in `cardvision/data/raw/`, `cardvision/data/train/images/`, `cardvision/data/val/images/`, `cardvision/models/`, or `cardvision/runs/`. These are gitignored. Share model weights and datasets via Google Drive.
