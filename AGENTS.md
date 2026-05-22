# AGENTS.md

This file provides guidance to OpenCode when working with code in this repository.

## What Achievements Is

A PinSheet plugin that tracks and surfaces achievements, badges, and personal milestones from round data. Runs as a hook on `on_round_saved` to detect accomplishments (first birdie, best round, 100th round, streaks, etc.) and displays them in a dedicated screen.

## Before you start

- All relevant project documentation can be found in `docs/`
- Reference the parent PinSheet repo (`source/plugin.py`, `source/plugin_loader.py`) for plugin API conventions
- Backlog items are priority-tagged `[P0]` / `[P1]` / `[P2]` in `docs/BACKLOG.md`. Ideas are tagged `[I*]` in `docs/IDEAS.md`.

### Claude memory files (ignore)
This project may contain Claude Code artifacts (`CLAUDE.md`, `.claude/`). These are managed by a different tool. OpenCode must never read, write, or modify them.

### Session memory files (gitignored)
The session memory files (`docs/HANDOFF.md`, `docs/SESSION_LOG.md`, `docs/DECISIONS.md`, `docs/BACKLOG.md`) are excluded via `.gitignore`. They remain local and are not committed. Edits to these files affect local state only.

### Nested repo isolation
**CRITICAL:** Achievements is a standalone git repository nested inside the parent PinSheet repo at `plugins/achievements/`. The parent's `.gitignore` excludes `plugins/`. NEVER commit achievements files from the parent repo.

## Git workflow

**CRITICAL:** NEVER push changes or create pull requests without explicit user consent. Always ask before running `git push` or `gh pr create`.

Uses **main + feature branch** workflow:
1. Start from `main`: `git checkout main && git pull origin main && git checkout -b feature/my-feature`
2. Work, commit, push
3. Open PR to `main`
4. Merge when ready

## Commands

**Run tests:**
```bash
PYTHONPATH=source:plugins pytest plugins/achievements/tests/ -v
```

**Compile a single file:**
```bash
python -m py_compile plugins/achievements/plugin.py
```
