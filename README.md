[![Release](https://img.shields.io/github/v/release/BitNinja01/pinsheet-achievements.svg?style=for-the-badge&color=green)](https://github.com/BitNinja01/pinsheet-achievements/releases)
[![Downloads](https://img.shields.io/github/downloads/BitNinja01/pinsheet-achievements/total.svg?style=for-the-badge&color=green)](https://github.com/BitNinja01/pinsheet-achievements/releases)
[![CI](https://img.shields.io/github/actions/workflow/status/BitNinja01/pinsheet-achievements/ci.yml?branch=dev&style=for-the-badge&label=CI)](https://github.com/BitNinja01/pinsheet-achievements/actions)
[![Platform](https://img.shields.io/badge/Platforms-Linux%20|%20macOS%20|%20Windows-white.svg?style=for-the-badge&color=green)](https://github.com/BitNinja01/pinsheet-achievements)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&color=green)](https://www.python.org/downloads/)

<p align="center">
  <img src="docs/img/logo_light.svg#gh-light-mode-only" alt="Achievements Logo" width="500">
  <img src="docs/img/logo_dark.svg#gh-dark-mode-only" alt="Achievements Logo" width="500">
</p>

---

> Numbers matter. Celebrating them matters more.

---

A plugin for [PinSheet](https://github.com/BitNinja01/pinsheet), the golf stats and round tracking app. Tracks achievements, badges, and personal milestones from your golf rounds.

- **Replaces the built-in bests section** — richer personal best detection that surfaces what matters: best round, best differential, most GIR, fewest putts, and more
- **Milestone badges** — first round, 10th/50th/100th round, century of birdies, and other milestones worth celebrating
- **Streak tracking** — consecutive rounds with FIR, GIR, par-or-better, or anything else worth keeping alive
- **Achievement gallery** — browse earned and locked badges in-app, with context for what it takes to unlock each one
- **All local, all personal** — your achievements stay on your machine, no accounts, no leaderboards, no network

### Setup

Requires PinSheet v2.1.0+.

---

## Installation

### Prerequisites

- **Python 3.11+**
- **PinSheet v2.1.0+** — the parent app must be installed and its plugin system available

**PinSheet's launcher (`launch.sh`/`launch.bat`) auto-installs plugin dependencies at startup** — no manual `pip install` needed when running inside PinSheet. The steps below just place the files in the right directory.

### Option 1: Release zip (recommended)

Download the latest release from the [releases page](https://github.com/BitNinja01/pinsheet-achievements/releases) and extract it into PinSheet's `plugins/` directory:

```bash
# From your PinSheet install directory
mkdir -p plugins
cd plugins
wget https://github.com/BitNinja01/pinsheet-achievements/releases/latest/download/achievements_X.Y.Z.zip
unzip achievements_X.Y.Z.zip -d achievements
```

### Option 2: Git clone

```bash
# From your PinSheet install directory
mkdir -p plugins
cd plugins
git clone https://github.com/BitNinja01/pinsheet-achievements.git achievements
```

For standalone use outside PinSheet, run `pip install -r requirements.txt` from the achievements directory.

### Verify installation

Launch PinSheet — if installed correctly, you'll see Achievements listed under plugin bindings. Press `b` on the dashboard to open the achievement gallery.
