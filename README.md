# The World Today — 26 November 2026

A make.fun `news-image-20261126` entry. A pure-Python (stdlib only)
program that draws a newspaper front page summing up the world's news of
Thursday, 26 November 2026, and writes it to `entry.png` (1024x1024,
deterministic: two runs write identical bytes).

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Contents

- `main.py` — the entrypoint. Hand-written 5x7 bitmap font, drawing
  primitives, and a minimal PNG encoder (zlib + CRC32, fixed compression,
  no timestamps). No network, no files read, no third-party packages.
- 3 lead stories, 6 top stories, 32 world-in-brief items = **41 stories**
  across **7 regions** (North America, Europe, Middle East, Asia-Pacific,
  Africa, Latin America, Global), each with its source.

## Date check

Every story above happened or was first reported on Thursday,
26 November 2026, verified against Reuters, BBC, NYT and AP wires.
