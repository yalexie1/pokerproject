# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

No build step required. Open directly in a browser:

```
open tictactoe.html
```

## Architecture

The entire project is a single self-contained file: `tictactoe.html` (HTML + CSS + JS, no external dependencies).

**Game state** (JS variables):
- `board` — 9-element array, each cell is `null`, `'X'`, or `'O'`
- `current` — whose turn it is (`'X'` or `'O'`)
- `gameOver` — boolean, blocks further moves after a win or draw
- `scores` — object tracking `{ X, O, D }` across rounds

**Win detection**: `WINS` constant holds all 8 winning lines (3 rows, 3 cols, 2 diagonals) as index triples. `checkWin()` iterates these against `board`.

**DOM**: Cells are `.cell` elements with `data-i` attributes (0–8). State changes are applied by toggling classes (`x`, `o`, `taken`, `win`) and setting `textContent`.

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
