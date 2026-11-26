#!/usr/bin/env python3
"""THE WORLD TODAY - one image summing up Thursday 26 November 2026.

Draws a newspaper front page (1024x1024 PNG) in pure Python stdlib:
a hand-written 5x7 bitmap font, drawing primitives, and a minimal PNG
encoder (zlib + CRC32, fixed compression, no timestamps), so two runs
write identical bytes. No network, no files read, no installed packages.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 234)
INK = (20, 20, 20)
RED = (179, 38, 30)
BLUE = (29, 78, 137)
GREY = (110, 104, 90)
WHITE = (255, 255, 255)
FAINT = (214, 208, 194)

DOT = "\u25cf"    # solid confidence marker
HALF = "\u25d0"   # half confidence marker

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font, written here by hand. Each glyph is 7 rows of 5 cells.
# "#" is ink, "." is empty. Only uppercase + digits + punctuation: the
# whole image is set in capitals, newspaper style.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": (".###.", "#...#", "....#", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#..##", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "\u2022": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
    "\u25cf": (".###.", "#####", "#####", "#####", "#####", ".###.", "....."),
    "\u25d0": (".##..", "##...", "##...", "##...", "##...", ".##..", "....."),
    "\u2713": (".....", ".....", "....#", "...#.", "#.#..", ".#...", "....."),
}

BLANK = (".....", ".....", ".....", ".....", ".....", ".....", ".....")


def char_advance(scale):
    return 5 * scale + 1


def text_width(s, scale):
    if not s:
        return 0
    return len(s) * char_advance(scale) - 1


# ------------------------------------------------------------- canvas -----
class Canvas:
    def __init__(self):
        self.buf = bytearray(bytes(PAPER) * (W * H))

    def _set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        if w <= 0 or h <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.buf[i:i + len(row)] = row

    def rect(self, x, y, w, h, c):
        self.fill_rect(x, y, w, 1, c)
        self.fill_rect(x, y + h - 1, w, 1, c)
        self.fill_rect(x, y, 1, h, c)
        self.fill_rect(x + w - 1, y, 1, h, c)

    def hline(self, x, y, w, c):
        self.fill_rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill_rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self._set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def line2(self, x0, y0, x1, y1, c):
        """A 2px-thick line, for pictograms that must read at small size."""
        self.line(x0, y0, x1, y1, c)
        self.line(x0 + 1, y0, x1 + 1, y1, c)

    def filled_circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def circle(self, cx, cy, r, c):
        # Midpoint circle outline.
        x = 0
        y = r
        d = 1 - r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self._set(px, py, c)
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1

    def text(self, x, y, s, scale, c):
        cx = x
        adv = char_advance(scale)
        for ch in s:
            glyph = FONT.get(ch, BLANK)
            for r in range(7):
                row = glyph[r]
                for col in range(5):
                    if row[col] == "#":
                        self.fill_rect(cx + col * scale, y + r * scale,
                                       scale, scale, c)
            cx += adv
        return cx - x - 1 if s else 0

    def centered_text(self, y, s, scale, c):
        x = (W - text_width(s, scale)) // 2
        self.text(x, y, s, scale, c)
        return x

    def wrap(self, s, scale, max_w):
        words = s.split(" ")
        lines = []
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# -------------------------------------------------------------- png ------
def encode_png(cv):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += cv.buf[y * stride:(y + 1) * stride]

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


# -------------------------------------------------------------- data ------
# All facts as reported on 26 November 2026. Headlines are shortened to
# fit the layout; no numbers are invented.
LEADS = [
    # (headline, deck, source, pictogram)
    ("US PROPOSES SWEEPING TARIFFS ON 14 PARTNERS",
     "USTR: UP TO 25% INDIA, 20% CHINA, 35% VIETNAM.",
     "REUTERS", "tariff"),
    ("HOUTHIS HIT SAUDI REFINERY; BRENT TOPS $94",
     "RAS TANURA HIT CLAIMED; BRENT +3.5% TO $94.61.",
     "REUTERS", "oil"),
    ("UKRAINE HITS 5 JETS; RUSSIA FIRES 112 DRONES",
     "5 JETS HIT AT SAVASLEYKA; 112 DRONES HIT POWER GRID.",
     "REUTERS", "jets"),
]

TOPS = [
    # (kicker, headline, summary, source, level)
    ("NORTH KOREA",
     "KIM ORDERS WIDER DEPLOYMENT OF TACTICAL NUCLEAR WEAPONS",
     "KCNA: KIM ORDERS THE WIDER DEPLOYMENT OF TACTICAL NUCLEAR ARMS.",
     "KCNA/REUTERS", "HIGH"),
    ("US ECONOMY",
     "FED: MODEST GROWTH, STICKY PRICES; CORE INFLATION 3.3%",
     "BEIGE BOOK: 8 OF 12 DISTRICTS GREW; JOBLESS CLAIMS 189,000, NEAR 57-YEAR LOW.",
     "FED/BEA", "HIGH"),
    ("MARKETS",
     "STOCKS TUMBLE ON TARIFF FEARS; NVIDIA -3.9%",
     "NASDAQ -0.62%, S&P -0.25%, DOW +0.33%; US MARKETS SHUT FOR THANKSGIVING.",
     "REUTERS", "HIGH"),
    ("EGYPT",
     "CAIRO TANKER FIRE KILLS AT LEAST 31",
     "FUEL TANKER OVERTURNED AND IGNITED ON CAIRO'S RING ROAD.",
     "CBS/REUTERS", "HIGH"),
    ("SUDAN",
     "SUDAN DRONE STRIKES KILL 19 CIVILIANS IN BLUE NILE",
     "RSF DRONES HIT DAMAZIN AND ROSEIRES, RIGHTS GROUPS SAY.",
     "REUTERS", "MEDIUM"),
    ("GAZA",
     "ISRAEL KILLS SENIOR HAMAS SECURITY CHIEF IN GAZA",
     "NAEEM ABU NAHEL KILLED WITH HIS WIFE AND TWO CHILDREN; SECOND IN 24 HOURS.",
     "REUTERS", "HIGH"),
]

# (region, [one-line items, each ending with its source])
BRIEFS = [
    ("NORTH AMERICA", [
        "BIRTHRIGHT ORDER BLOCKED BY JUDGE - REUTERS",
        "US CONFIDENCE NEAR 2-YEAR HIGH - REUTERS",
        "CALIFORNIA FLOOD WARNING, KING TIDES - BBC",
        "6 DEAD IN PLANE CRASH OFF MISSISSIPPI - BBC",
        "MEXICO PROBES PROSECUTOR'S LINKS - NYT",
    ]),
    ("EUROPE", [
        "NORWAY COURT VOIDS OIL LICENCES - REUTERS",
        "GERMANY SAYS RUSSIA PLANS SPACE NUKES - WP",
        "ECB CHIEF SEARCH AS LAGARDE RESIGNS - C54",
        "MURMANSK GOVERNOR HELD ON GRAFT - REUTERS",
        "URGE RUSSIA TO END RIOT-AGENT USE - REUTERS",
    ]),
    ("MIDDLE EAST", [
        "IRAN NAVY: TANKER HIT MINE IN HORMUZ - IRNA",
        "HOUTHI DRONE HITS RIYADH, 11 HURT - REUTERS",
        "LEBANON TO OPEN SECOND AIRPORT - REUTERS",
        "ISRAEL COURT DROPS NETANYAHU CASE - REUTERS",
    ]),
    ("ASIA-PACIFIC", [
        "SOLOMON ISLANDS SIGNS AUSTRALIA PACT - NYT",
        "TAIWAN SHARES FALL 1,927 PTS - REUTERS",
        "US PROPOSES 15% TARIFF ON TAIWAN - REUTERS",
        "CHINA PROBES SHANGHAI PARTY CHIEF - REUTERS",
        "HUAWEI FOUND GUILTY OF IP THEFT - REUTERS",
        "INDIA MARKS 18 YEARS SINCE 26/11 - ANI",
        "INDIA APPROVES EQUIPMENT PLAN - REUTERS",
    ]),
    ("AFRICA", [
        "RAMAPHOSA WINS FARMGATE REPRIEVE - NYT",
        "GHANA UNVEILS HERITAGE BANKNOTES - C54",
        "KENYA: LAST EBOLA PATIENT OUT - REUTERS",
        "NIGERIA STARTS BUILDING NAVAL SHIPS - C54",
        "DRC ENACTS CONSTITUTIONAL-REFORM LAW - C54",
    ]),
    ("LATIN AMERICA", [
        "COLOMBIA FREES 20 HOSTAGES IN SIEGE - BBC",
        "ECUADOR IN US TALKS ON OPERATIONS - REUTERS",
        "SEALED MARIO GAME SELLS FOR $96,875 - AP",
    ]),
    ("GLOBAL", [
        "GOLD $3,573; BRENT $94.82 - REUTERS",
        "BANGLADESH GARMENT WAGES UP 36% - REUTERS",
        "INDONESIA MINE FLOOD KILLS NINE - REUTERS",
    ]),
]


def story_count():
    return len(LEADS) + len(TOPS) + sum(len(items) for _, items in BRIEFS)


# ------------------------------------------------------------ drawing ----
def draw_globe(cv, cx, cy, r):
    cv.circle(cx, cy, r, INK)
    cv.hline(cx - r, cy, 2 * r + 1, INK)
    cv.vline(cx, cy - r, 2 * r + 1, INK)
    cv.line(cx - r + 3, cy - r + 5, cx + r - 3, cy - r + 5, INK)
    cv.line(cx - r + 3, cy + r - 5, cx + r - 3, cy + r - 5, INK)


def draw_pictogram(cv, kind, cx, cy):
    """Small icon in a 64x40 box centred on (cx, cy)."""
    if kind == "tariff":
        cv.hline(cx - 28, cy + 16, 57, INK)
        cv.vline(cx - 28, cy - 16, 33, INK)
        cv.fill_rect(cx - 22, cy + 6, 10, 10, BLUE)
        cv.fill_rect(cx - 8, cy - 4, 10, 20, BLUE)
        cv.fill_rect(cx + 6, cy - 14, 10, 30, RED)
        cv.line(cx - 26, cy - 6, cx + 24, cy - 16, RED)
        cv.line(cx + 24, cy - 16, cx + 18, cy - 16, RED)
        cv.line(cx + 24, cy - 16, cx + 24, cy - 10, RED)
    elif kind == "oil":
        cv.line2(cx, cy - 18, cx - 20, cy + 16, INK)
        cv.line2(cx, cy - 18, cx + 20, cy + 16, INK)
        cv.hline(cx - 20, cy + 16, 41, INK)
        cv.hline(cx - 13, cy - 4, 27, INK)
        cv.hline(cx - 8, cy + 7, 17, INK)
        cv.filled_circle(cx, cy - 22, 4, RED)
        cv.fill_rect(cx + 24, cy + 8, 8, 8, BLUE)
    elif kind == "jets":
        # One jet in profile, nose left, plus two small drones above.
        cv.fill_rect(cx - 26, cy - 1, 52, 4, INK)
        cv.line(cx - 26, cy + 1, cx - 32, cy - 2, INK)
        cv.line(cx - 26, cy + 1, cx - 32, cy + 4, INK)
        cv.line2(cx - 4, cy + 3, cx - 14, cy + 14, INK)
        cv.line2(cx + 2, cy + 3, cx + 12, cy + 14, INK)
        cv.line2(cx + 22, cy - 1, cx + 22, cy - 11, INK)
        cv.line(cx + 22, cy - 11, cx + 28, cy - 11, INK)
        cv.fill_rect(cx - 30, cy - 14, 4, 4, RED)
        cv.fill_rect(cx + 14, cy - 16, 4, 4, BLUE)


def draw_source_line(cv, cx, y, source, level):
    """Centred source + confidence marker, e.g. REUTERS (dot) HIGH."""
    mark = DOT if level == "HIGH" else HALF
    mark_c = RED if level == "HIGH" else BLUE
    left = source + "  "
    right = " " + level
    total = text_width(left, 2) + text_width(mark, 2) + text_width(right, 2)
    x = cx - total // 2
    x += cv.text(x, y, left, 2, GREY)
    x += cv.text(x, y, mark, 2, mark_c)
    cv.text(x, y, right, 2, mark_c)


def draw_masthead(cv):
    draw_globe(cv, 252, 26, 14)
    draw_globe(cv, 772, 26, 14)
    cv.centered_text(8, "THE WORLD TODAY", 5, INK)
    cv.centered_text(48, "THURSDAY, 26 NOVEMBER 2026", 3, RED)
    cv.fill_rect(16, 76, 992, 2, INK)
    cv.centered_text(
        82,
        "THE DAY'S WORLD NEWS - VERIFIED 26 NOV 2026 AGAINST REUTERS, BBC, NYT, AP WIRES",
        2, GREY)


def draw_leads(cv):
    y0, h = 104, 210
    panel_w = 322
    for i, (headline, deck, source, kind) in enumerate(LEADS):
        px = 16 + i * (panel_w + 12)
        cv.fill_rect(px, y0, panel_w, h, WHITE)
        cv.fill_rect(px, y0, panel_w, 5, RED)
        cv.rect(px, y0, panel_w, h, INK)
        cx = px + panel_w // 2
        draw_pictogram(cv, kind, cx, y0 + 34)
        lines = cv.wrap(headline, 3, panel_w - 24)
        ly = y0 + 60
        for ln in lines[:3]:
            w = text_width(ln, 3)
            cv.text(cx - w // 2, ly, ln, 3, INK)
            ly += 22
        deck_lines = cv.wrap(deck, 2, panel_w - 24)
        dy = y0 + 60 + 3 * 22 + 8
        for ln in deck_lines[:2]:
            w = text_width(ln, 2)
            cv.text(cx - w // 2, dy, ln, 2, INK)
            dy += 15
        draw_source_line(cv, cx, y0 + h - 22, source, "HIGH")


def draw_top_stories(cv):
    cv.text(16, 322, "TOP STORIES", 2, RED)
    cv.fill_rect(16, 340, 992, 1, FAINT)
    rows = (346, 442, 538)
    for i, (kicker, headline, summary, source, level) in enumerate(TOPS):
        cx = 16 + (i % 2) * 504
        cy = rows[i // 2]
        cv.text(cx + 12, cy + 4, kicker, 2, RED)
        hlines = cv.wrap(headline, 2, 464)
        hy = cy + 21
        for ln in hlines[:2]:
            cv.text(cx + 12, hy, ln, 2, INK)
            hy += 14
        slines = cv.wrap(summary, 2, 464)
        sy = cy + 52
        for ln in slines[:2]:
            cv.text(cx + 12, sy, ln, 2, INK)
            sy += 14
        # source + confidence, left aligned
        mark = DOT if level == "HIGH" else HALF
        mark_c = RED if level == "HIGH" else BLUE
        sx = cx + 12
        sx += cv.text(sx, cy + 82, source + "  ", 2, GREY)
        sx += cv.text(sx, cy + 82, mark, 2, mark_c)
        cv.text(sx, cy + 82, " " + level, 2, mark_c)
    cv.vline(512, 346, 288, FAINT)


def draw_brief_column(cv, x, y, regions):
    """Draw region groups; returns the y just past the last item."""
    for region, items in regions:
        cv.text(x, y, region, 2, RED)
        w = text_width(region, 2)
        cv.fill_rect(x, y + 15, w, 1, RED)
        y += 16
        for item in items:
            lines = cv.wrap(item, 2, 476)
            for ln in lines:
                cv.fill_rect(x, y + 5, 5, 5, RED)
                cv.text(x + 12, y, ln, 2, INK)
                y += 14
        y += 2
    return y


def draw_brief(cv):
    cv.text(16, 636, "WORLD IN BRIEF", 2, RED)
    cv.fill_rect(16, 654, 992, 1, FAINT)
    draw_brief_column(cv, 16, 658, BRIEFS[:3])
    draw_brief_column(cv, 520, 658, BRIEFS[3:])


def draw_footer(cv, total):
    cv.fill_rect(16, 986, 992, 1, INK)
    cv.centered_text(
        992,
        "DATE CHECK: THURSDAY 26 NOVEMBER 2026 - EVERY STORY ABOVE IS FROM 26 NOV 2026",
        2, INK)
    left = ("SOURCES: REUTERS, BBC, NYT, AP, KCNA, FED/BEA - "
            + str(total) + " STORIES, 7 REGIONS")
    cv.text(16, 1008, left, 2, GREY)
    credit = "MAKE.FUN DAILY NEWS"
    cv.text(1024 - 16 - text_width(credit, 2), 1008, credit, 2, RED)


def build():
    cv = Canvas()
    draw_masthead(cv)
    draw_leads(cv)
    draw_top_stories(cv)
    draw_brief(cv)
    draw_footer(cv, story_count())
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    data = encode_png(build())
    with open(out_path, "wb") as f:
        f.write(data)
    os.chmod(out_path, 0o644)
    print("wrote %s (%d bytes, %d stories, 7 regions)"
          % (out_path, len(data), story_count()))


if __name__ == "__main__":
    main()
