#!/usr/bin/env python3
"""Sum up 25 November 2026 world news in one image.

Draws a 1024x1024 newspaper-style PNG to /output/entry.png using only
the Python standard library (zlib + struct for the PNG container).
No network, no randomness, no clock: two runs write byte-identical files.

Stories were verified against wire reports first published on
25 November 2026 (UTC): ABS (Australia CPI), AP (CIA breach, Huawei
verdict, Abrego Garcia, lead azide), Government of India (Nayi Chetna).
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 231)
CARD = (255, 255, 255)
INK = (26, 26, 26)
RED = (185, 28, 28)
NAVY = (30, 58, 95)
GRAY = (110, 105, 95)
LINEC = (205, 195, 175)
WHITE = (255, 255, 255)
SKY = (214, 232, 245)
GOLD = (201, 162, 39)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, '#' = on, '.' = off. Written for this entry only.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_text(text, max_chars):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.rows = []
        for _ in range(h):
            row = bytearray(w * 3)
            for x in range(w):
                row[x * 3] = bg[0]
                row[x * 3 + 1] = bg[1]
                row[x * 3 + 2] = bg[2]
            self.rows.append(row)

    def pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            row = self.rows[y]
            row[x * 3] = color[0]
            row[x * 3 + 1] = color[1]
            row[x * 3 + 2] = color[2]

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.pixel(xx, yy, color)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.pixel(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.pixel(xx, yy, color)

    def ring(self, cx, cy, r, color, thick=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - thick) ** 2 <= d2 <= r * r:
                    self.pixel(xx, yy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        minx, maxx = min(x0, x1, x2), max(x0, x1, x2)
        miny, maxy = min(y0, y1, y2), max(y0, y1, y2)
        d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if d == 0:
            return
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / d
                b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / d
                c = 1 - a - b
                if a >= 0 and b >= 0 and c >= 0:
                    self.pixel(xx, yy, color)

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for ch in text.upper():
            glyph = FONT.get(ch, FONT[" "])
            for gy in range(7):
                row = glyph[gy]
                for gx in range(5):
                    if row[gx] == "1":
                        self.rect(cx + gx * scale, y + gy * scale,
                                 scale, scale, color)
            cx += 6 * scale
        return cx

    def draw_text_centered(self, y, text, scale, color):
        x = (self.w - text_width(text, scale)) // 2
        self.draw_text(x, y, text, scale, color)

    def draw_wrapped(self, x, y, text, scale, color, max_chars, leading):
        yy = y
        for line in wrap_text(text, max_chars):
            self.draw_text(x, yy, line, scale, color)
            yy += 7 * scale + leading
        return yy


# ---------------------------------------------------------------- icons
def icon_chart(cv, x, y, color):
    # three bars: Sep 4.3, forecast 4.8, Oct 4.9
    base = y + 66
    cv.rect(x + 8, base - 34, 22, 34, color)
    cv.rect(x + 40, base - 40, 22, 40, GRAY)
    cv.rect(x + 72, base - 42, 22, 42, RED)
    cv.hline(x, base, 100, INK)
    cv.draw_text(x + 26, base + 10, "4.9%", 2, RED)


def icon_shield(cv, x, y, color):
    cx, cy = x + 50, y + 42
    cv.ring(cx, cy, 34, color, 5)
    cv.circle(cx, cy - 8, 7, color)
    cv.rect(cx - 4, cy - 2, 8, 16, color)
    cv.draw_text(x + 22, y + 84, "BREACH", 2, RED)


def icon_court(cv, x, y, color):
    cv.triangle(x + 50, y + 6, x + 6, y + 34, x + 94, y + 34, color)
    for i in range(3):
        cv.rect(x + 16 + i * 28, y + 40, 10, 40, color)
    cv.rect(x + 6, y + 84, 88, 6, color)


def icon_blast(cv, x, y, color):
    cx, cy = x + 50, y + 46
    for k in range(8):
        ang = k * math.pi / 4
        x2 = int(cx + 44 * math.cos(ang))
        y2 = int(cy + 44 * math.sin(ang))
        cv.line(cx, cy, x2, y2, color)
    cv.circle(cx, cy, 16, RED)
    cv.circle(cx, cy, 8, GOLD)
    cv.draw_text(x + 2, y + 84, "10,000 LB", 2, INK)


def icon_plane(cv, x, y, color):
    cv.triangle(x + 78, y + 40, x + 96, y + 46, x + 78, y + 52, color)
    cv.rect(x + 8, y + 42, 72, 8, color)
    cv.triangle(x + 30, y + 42, x + 44, y + 22, x + 52, y + 42, color)
    cv.triangle(x + 30, y + 50, x + 44, y + 68, x + 52, y + 50, color)
    cv.rect(x + 8, y + 30, 8, 12, color)
    cv.draw_text(x + 8, y + 84, "TO SPAIN", 2, color)


def icon_sun(cv, x, y, color):
    cx, cy = x + 50, y + 58
    cv.circle(cx, cy, 22, GOLD)
    for k in range(8):
        ang = k * math.pi / 4
        x0 = int(cx + 28 * math.cos(ang))
        y0 = int(cy + 28 * math.sin(ang))
        x1 = int(cx + 38 * math.cos(ang))
        y1 = int(cy + 38 * math.sin(ang))
        cv.line(x0, y0, x1, y1, GOLD)
    cv.hline(x + 6, y + 86, 88, color)
    cv.hline(x + 16, y + 92, 68, color)


ICONS = [icon_chart, icon_shield, icon_court, icon_blast, icon_plane, icon_sun]

# ---------------------------------------------------------------- stories
STORIES = [
    {
        "kicker": "ECONOMY - AUSTRALIA",
        "accent": RED,
        "headline": "INFLATION JUMPS TO 4.9%",
        "body": "Australia's CPI rose 4.9% in the year to October, up from 4.3% in September and above the 4.8% forecast. Trimmed mean hit 3.8%, keeping RBA rate-hike fears alive.",
        "source": "ABS - 25 NOV 00:30 GMT",
    },
    {
        "kicker": "CYBER - USA",
        "accent": NAVY,
        "headline": "CIA SYSTEM BREACHED IN CYBERATTACK",
        "body": "An unclassified CIA system was breached, AP confirmed. The NYT reported CIA and ODNI networks hit. No classified data was involved, officials said.",
        "source": "AP / NYT - 25 NOV",
    },
    {
        "kicker": "COURTS - USA",
        "accent": NAVY,
        "headline": "HUAWEI GUILTY ON 10 COUNTS",
        "body": "A US jury found Huawei guilty of trade-secret theft conspiracy and bank fraud. The Chinese tech giant was acquitted of racketeering.",
        "source": "AP - 25 NOV",
    },
    {
        "kicker": "USA - IOWA",
        "accent": RED,
        "headline": "ARMY TO BLAST 10,000 LB OF LEAD AZIDE",
        "body": "The US Army will detonate its entire stockpile of degraded bomb-making chemical in Iowa on Wednesday morning after a federal court gave the go-ahead.",
        "source": "AP - 25 NOV",
    },
    {
        "kicker": "IMMIGRATION - USA",
        "accent": NAVY,
        "headline": "ABREGO GARCIA LEAVES FOR SPAIN",
        "body": "Kilmar Abrego Garcia, mistakenly deported to El Salvador earlier this year, is now self-deporting from the US to Spain, AP reported.",
        "source": "AP - 25 NOV",
    },
    {
        "kicker": "INDIA",
        "accent": RED,
        "headline": "NAYI CHETNA 5.0 LAUNCHES FOR WOMEN",
        "body": "India launched Nayi Chetna 5.0, a national gender campaign for women's economic empowerment, running to 23 December under the rural livelihoods mission.",
        "source": "GOVT OF INDIA - 25 NOV",
    },
]

ALSO_TODAY = (
    "ALSO TODAY: US PCE INFLATION + Q3 GDP DUE 13:30 UTC - "
    "RECORD KING TIDES PEAK AGAIN ON THE CALIFORNIA COAST - "
    "81.5M AMERICANS TRAVEL FOR THANKSGIVING"
)


# ---------------------------------------------------------------- layout
def draw_card(cv, x, y, w, h, story, icon_fn):
    cv.rect(x, y, w, h, CARD)
    cv.rect(x, y, 6, h, story["accent"])
    cv.rect(x, y, w, 2, LINEC)
    cv.rect(x, y + h - 2, w, 2, LINEC)
    tx = x + 18
    cv.draw_text(tx, y + 14, story["kicker"], 2, story["accent"])
    hy = y + 40
    for line in wrap_text(story["headline"], 20):
        cv.draw_text(tx, hy, line, 3, INK)
        hy += 25
    by = y + 100
    cv.draw_wrapped(tx, by, story["body"], 2, INK, 29, 2)
    cv.draw_text(tx, y + h - 24, story["source"], 2, GRAY)
    icon_fn(cv, x + w - 118, y + 16, story["accent"])


def build():
    cv = Canvas(W, H, PAPER)
    cv.draw_text_centered(22, "THE WORLD IN ONE IMAGE", 5, INK)
    cv.rect(24, 82, W - 48, 4, RED)
    cv.draw_text_centered(96, "WEDNESDAY 25 NOVEMBER 2026", 3, INK)
    cv.draw_text_centered(126, "SIX STORIES FIRST REPORTED TODAY", 2, GRAY)

    xs = [16, 512]
    ys = [156, 416, 676]
    for i, story in enumerate(STORIES):
        draw_card(cv, xs[i % 2], ys[i // 2], 496, 248, story, ICONS[i])

    cv.rect(16, 940, 992, 52, NAVY)
    cv.draw_wrapped(28, 950, ALSO_TODAY, 2, WHITE, 80, 2)
    cv.draw_text_centered(1000, "SOURCES: ABS - AP - NYT - REUTERS",
                          2, GRAY)
    return cv


# ---------------------------------------------------------------- png
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = b"".join(b"\x00" + bytes(row) for row in cv.rows)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", zlib.compress(raw, 9))
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError:
        out_dir = "out"
        os.makedirs(out_dir, exist_ok=True)
    cv = build()
    out_path = os.path.join(out_dir, "entry.png")
    size = write_png(cv, out_path)
    # Gate guard: the entry must be a PNG at most 1 MiB and 1024x1024.
    with open(out_path, "rb") as f:
        head = f.read(33)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG file"
    gw, gh = struct.unpack(">II", head[16:24])
    assert (gw, gh) == (W, H), "bad dimensions %dx%d" % (gw, gh)
    assert size <= 1048576, "PNG over 1 MiB: %d bytes" % size
    assert size > 10000, "PNG suspiciously small: %d bytes" % size
    print("wrote %s (%d bytes, %dx%d)" % (out_path, size, gw, gh))


if __name__ == "__main__":
    main()
