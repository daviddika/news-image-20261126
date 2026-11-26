# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/daviddika/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/daviddika/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

Entry for the make.fun bounty **news-image-20261126** — "Sum up 26 November's
world news in one image" ($100).

**Entrant:** Mahardika (@dika-david)

## Design

A newspaper-front-page editorial infographic, 1024×1024, in a newsprint
palette (cream paper, black ink, one red accent). The masthead names the
date **THURSDAY, 26 NOVEMBER 2026**; 3 lead stories and 6 top stories sit
above a "World in Brief" grid carrying the other 32 stories — **41
sourced stories in total across 7 regions** (North America, Europe,
Middle East, Asia-Pacific, Africa, Latin America, Global), each with its
source and a confidence marker (● HIGH / ◐ MEDIUM). Claims are worded as
claims. Every story above happened or was first reported on Thursday,
26 November 2026, verified against Reuters, BBC, NYT and AP wires. All
graphics are drawn in code — no photographs or copied artwork.

## Files

- `main.py` — the entrypoint. Hand-written 5×7 bitmap font, drawing
  primitives, and a minimal PNG encoder (zlib + CRC32, fixed compression,
  no timestamps). Pure Python standard library, no network, no files read,
  no third-party packages. Writes `entry.png` (1024×1024, deterministic:
  two runs write identical bytes) to `$MAKEFUN_OUTPUT_DIR` (default
  `/output`).
- `README.md` — this file
- `LICENSE` — MIT
- `.gitignore`
- `.makefun/owner.json` — entrant wallet

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=2vjd5xyx&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
