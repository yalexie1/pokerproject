# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A poker game built as a self-contained web app (HTML + CSS + JS, no external dependencies).

## Running the App

No build step required. Open directly in a browser:

```
open poker.html
```

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
