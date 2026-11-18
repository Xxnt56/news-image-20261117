#!/usr/bin/env python3
"""The World in One Day -- make.fun news-image-20261117 entry.

Draws a newspaper front page that sums up Tuesday 17 November 2026 in one
1024x1024 image, using only the Python standard library (no network, no
external packages, no image files): a tiny framebuffer, a 5x7 bitmap font,
and a hand-written PNG encoder. Deterministic: two runs write identical
bytes. Writes to $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).
"""

import os
import struct
import zlib
from pathlib import Path

W = 1024
H = 1024

PAPER = (247, 243, 232)
INK = (17, 17, 17)
GREY = (90, 90, 88)
RED = (192, 57, 43)
NAVY = (27, 58, 92)
SKY = (173, 216, 240)
SEA = (46, 111, 164)
SAND = (232, 205, 158)
WHITE = (255, 255, 255)
GOLD = (212, 175, 55)
GREEN = (39, 174, 96)
DARK = (30, 39, 46)
PINK = (250, 219, 216)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, '#' = ink. Uppercase, digits and common punctuation.
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
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
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
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}

CHAR_W = 6  # 5 px glyph + 1 px gap, before scaling


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


def draw_text(fb, x, y, text, scale, color):
    """Draw one line of text (uppercased) at (x, y); returns width drawn."""
    text = text.upper()
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    fb.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
        cx += CHAR_W * scale
    return cx - x - scale


def draw_text_center(fb, cx, y, text, scale, color):
    w = text_width(text, scale)
    draw_text(fb, cx - w // 2, y, text, scale, color)


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.upper().split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Framebuffer:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def put(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.put(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.put(xx, yy, color)

    def ring(self, cx, cy, r, thick, color):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - thick) ** 2 <= d2 <= (r + thick) ** 2:
                    self.put(xx, yy, color)

    def triangle(self, p1, p2, p3, color):
        (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
        minx, maxx = min(x1, x2, x3), max(x1, x2, x3)
        miny, maxy = min(y1, y2, y3), max(y1, y2, y3)
        denom = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if denom == 0:
            return
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                a = ((y2 - y3) * (xx - x3) + (x3 - x2) * (yy - y3)) / denom
                b = ((y3 - y1) * (xx - x3) + (x1 - x3) * (yy - y3)) / denom
                c = 1 - a - b
                if a >= 0 and b >= 0 and c >= 0:
                    self.put(xx, yy, color)


def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(fb, path):
    raw = bytearray()
    stride = fb.w * 3
    for y in range(fb.h):
        raw.append(0)  # filter: none
        raw += fb.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", fb.w, fb.h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += _chunk(b"IEND", b"")
    Path(path).write_bytes(data)

# ---------------------------------------------------------------- scenes
# Each scene paints a small flat illustration inside (x, y, w, h).

def scene_bridge(fb, x, y, w, h):
    fb.fill_rect(x, y, w, h, SKY)
    fb.fill_rect(x, y + h * 2 // 3, w, h // 3, SEA)
    fb.fill_rect(x, y + h * 2 // 3 - 4, w, 4, (200, 220, 235))
    # deck, left span standing, right span dropped into the water
    fb.fill_rect(x + 8, y + 22, w // 2 - 30, 10, DARK)
    fb.fill_rect(x + 8, y + 32, 6, h * 2 // 3 - 32, DARK)
    fb.fill_rect(x + w // 2 - 28, y + 32, 6, h * 2 // 3 - 32, DARK)
    fb.line(x + w // 2 + 30, y + 22, x + w - 20, y + h * 2 // 3 + 6, DARK)
    fb.line(x + w // 2 + 30, y + 32, x + w - 20, y + h * 2 // 3 + 16, DARK)
    # blast at the break
    cx, cy = x + w // 2 + 4, y + 26
    fb.disc(cx, cy, 12, (255, 176, 32))
    fb.disc(cx, cy, 7, (255, 102, 0))
    fb.disc(cx, cy, 3, WHITE)
    # splash where the span went down
    fb.disc(x + w - 34, y + h * 2 // 3 + 8, 6, WHITE)
    fb.disc(x + w - 22, y + h * 2 // 3 + 12, 4, WHITE)


def scene_summit(fb, x, y, w, h):
    fb.fill_rect(x, y, w, h, NAVY)
    fb.disc(x + w - 26, y + 24, 12, GOLD)
    # four flags on poles: US, Japan, India, Australia
    flags = [(226, 44, 54), (255, 255, 255), (255, 153, 51), (0, 51, 153)]
    for i, col in enumerate(flags):
        fx = x + 26 + i * 52
        fb.vline(fx, y + 14, 52, GOLD)
        fb.fill_rect(fx + 2, y + 14, 40, 26, col)
        if i == 1:
            fb.disc(fx + 22, y + 27, 7, RED)
        if i == 0:
            fb.fill_rect(fx + 2, y + 14, 40, 5, WHITE)
            fb.fill_rect(fx + 2, y + 22, 40, 5, WHITE)
            fb.fill_rect(fx + 2, y + 30, 40, 5, WHITE)
    # round table with four seats
    fb.fill_rect(x + 60, y + h - 26, w - 120, 10, GOLD)
    for i in range(4):
        fb.disc(x + 78 + i * 100, y + h - 34, 7, WHITE)


def scene_chip(fb, x, y, w, h):
    fb.fill_rect(x, y, w, h, DARK)
    cx, cy = x + w // 2 - 8, y + h // 2
    # gold pins around the chip
    for i in range(5):
        fb.fill_rect(cx - 34 + i * 15, y + 12, 6, 12, GOLD)
        fb.fill_rect(cx - 34 + i * 15, y + h - 24, 6, 12, GOLD)
    for i in range(3):
        fb.fill_rect(x + 12, cy - 22 + i * 18, 12, 6, GOLD)
        fb.fill_rect(x + w - 30, cy - 22 + i * 18, 12, 6, GOLD)
    fb.fill_rect(cx - 32, cy - 26, 64, 52, GREEN)
    fb.fill_rect(cx - 24, cy - 18, 48, 36, (18, 120, 60))
    draw_text(fb, cx - 15, cy - 10, "AI", 2, WHITE)


def scene_jets(fb, x, y, w, h):
    fb.fill_rect(x, y, w, h, SKY)
    fb.disc(x + 60, y + 24, 14, WHITE)
    fb.disc(x + 78, y + 28, 10, WHITE)
    fb.disc(x + w - 90, y + 66, 12, WHITE)
    fb.disc(x + w - 72, y + 70, 9, WHITE)
    # Japanese flag on a pole
    fb.vline(x + w - 34, y + 10, 44, INK)
    fb.fill_rect(x + w - 32, y + 10, 24, 16, WHITE)
    fb.disc(x + w - 20, y + 18, 4, RED)
    # two fighter jets climbing, red dashed intercept path
    for jx, jy, s in ((x + 60, y + 62, 1), (x + 130, y + 44, 1)):
        fb.triangle((jx, jy), (jx + 46, jy + 8), (jx + 8, jy + 12), DARK)
        fb.triangle((jx + 12, jy + 4), (jx + 22, jy - 12), (jx + 26, jy + 6), DARK)
        fb.triangle((jx + 34, jy + 10), (jx + 40, jy + 22), (jx + 30, jy + 10), DARK)
    for t in range(0, 9):
        fb.disc(x + 150 + t * 18, y + 78 - t * 4, 2, RED)


def scene_measles(fb, x, y, w, h):
    fb.fill_rect(x, y, w, h, PINK)
    # spiky virus balls
    for cx, cy, r in ((x + 70, y + 46, 18), (x + 150, y + 34, 13),
                      (x + 220, y + 52, 15)):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                       (1, 1), (-1, -1), (1, -1), (-1, 1)):
            fb.line(cx, cy, cx + dx * (r + 8), cy + dy * (r + 8), RED)
        fb.disc(cx, cy, r, RED)
        fb.disc(cx - 5, cy - 5, 4, (255, 120, 120))
    # rising case bars
    base = y + h - 10
    for i, bh in enumerate((14, 24, 36)):
        fb.fill_rect(x + w - 96 + i * 28, base - bh, 20, bh, RED)


def scene_gaza(fb, x, y, w, h):
    fb.fill_rect(x, y, w, h, SAND)
    fb.disc(x + w - 40, y + 22, 14, (255, 196, 66))
    fb.fill_rect(x, y + h - 22, w, 22, (196, 154, 108))
    # crossing barrier, striped
    fb.fill_rect(x + 14, y + 30, 8, h - 52, INK)
    for i in range(6):
        col = RED if i % 2 == 0 else WHITE
        fb.fill_rect(x + 22 + i * 22, y + 30, 22, 10, col)
    # aid truck with a red cross
    tx, ty = x + 150, y + 52
    fb.fill_rect(tx, ty, 84, 44, WHITE)
    fb.fill_rect(tx + 84, ty + 16, 34, 28, (200, 220, 235))
    fb.fill_rect(tx + 30, ty + 12, 24, 8, RED)
    fb.fill_rect(tx + 38, ty + 4, 8, 24, RED)
    fb.disc(tx + 20, ty + 48, 9, INK)
    fb.disc(tx + 66, ty + 48, 9, INK)
    fb.disc(tx + 104, ty + 48, 9, INK)
    # stacked aid boxes
    for bx, by in ((x + 30, y + h - 44), (x + 56, y + h - 44),
                   (x + 43, y + h - 66)):
        fb.fill_rect(bx, by, 22, 20, (210, 180, 140))
        fb.fill_rect(bx + 9, by + 7, 4, 6, RED)
        fb.fill_rect(bx + 7, by + 9, 8, 2, RED)


SCENES = {
    "bridge": scene_bridge,
    "summit": scene_summit,
    "chip": scene_chip,
    "jets": scene_jets,
    "measles": scene_measles,
    "gaza": scene_gaza,
}

STORIES = [
    ("UKRAINE WAR", "bridge",
     "KERCH BRIDGE COLLAPSES",
     "Ukraine strike drops a road span into the sea; Russia hits Kyiv bridges in reply."),
    ("ASIA", "summit",
     "TRUMP OPENS ASIA TRIP",
     "Quad summit in Manila, then APEC in Shenzhen; Xi, Putin and Trump to meet Thursday."),
    ("TECH", "chip",
     "HUANG STAYS OUT AS NVIDIA BEATS",
     "Revenue $115.8bn, up 103%; board says it will not reinstate Jensen Huang as CEO."),
    ("JAPAN", "jets",
     "RUSSIAN JETS BREACH SKIES",
     "Japan scrambles fighters after Russian aircraft violate its airspace."),
    ("HEALTH", "measles",
     "US LOSES MEASLES STATUS",
     "Elimination status gone after 26 years; 5,400 cases and 10 deaths in 2026."),
    ("GAZA", "gaza",
     "WEST URGES GAZA AID ACCESS",
     "UK, Australia, Canada and Italy call on Israel to open crossings as crisis deepens."),
]

TICKER = ("ALSO: MONGOLIA'S PRESIDENT RESIGNS - DEPARDIEU PLEADS GUILTY - "
          "CRASH KILLS 19")

# ---------------------------------------------------------------- layout
def draw_panel(fb, x, y, w, h, story):
    kicker, scene_key, headline, dek = story
    fb.fill_rect(x, y, w, h, WHITE)
    fb.fill_rect(x, y, w, 3, INK)
    fb.fill_rect(x, y, 3, h, INK)
    fb.fill_rect(x + w - 3, y, 3, h, INK)
    fb.fill_rect(x, y + h - 3, w, 3, INK)
    scene_h = 96
    SCENES[scene_key](fb, x + 3, y + 3, w - 6, scene_h)
    fb.fill_rect(x + 3, y + 3 + scene_h, w - 6, 2, INK)
    ty = y + 3 + scene_h + 10
    draw_text(fb, x + 14, ty, kicker, 2, RED)
    ty += 24
    for line in wrap_text(headline, 3, w - 28):
        draw_text(fb, x + 14, ty, line, 3, INK)
        ty += 26
    ty += 2
    for line in wrap_text(dek, 2, w - 28):
        draw_text(fb, x + 14, ty, line, 2, GREY)
        ty += 18


def build():
    fb = Framebuffer(W, H, PAPER)
    # outer frame
    fb.fill_rect(8, 8, W - 16, 6, INK)
    fb.fill_rect(8, H - 14, W - 16, 6, INK)
    fb.fill_rect(8, 8, 6, H - 16, INK)
    fb.fill_rect(W - 14, 8, 6, H - 16, INK)
    # masthead
    draw_text_center(fb, W // 2, 30, "THE WORLD IN ONE DAY", 6, INK)
    fb.fill_rect(24, 84, W - 48, 3, INK)
    draw_text_center(fb, W // 2, 94, "TUESDAY 17 NOVEMBER 2026", 3, RED)
    draw_text_center(fb, W // 2, 126,
                     "SIX STORIES THAT DEFINED THE DAY - IN ONE IMAGE",
                     2, GREY)
    fb.fill_rect(24, 152, W - 48, 3, INK)
    # story grid: 2 columns x 3 rows
    gx, gy = 24, 166
    cw = (W - 2 * gx - 16) // 2
    ch = 258
    for i, story in enumerate(STORIES):
        px = gx + (i % 2) * (cw + 16)
        py = gy + (i // 2) * (ch + 12)
        draw_panel(fb, px, py, cw, ch, story)
    # footer ticker
    ty = 962
    fb.fill_rect(24, ty - 6, W - 48, 40, INK)
    draw_text(fb, 34, ty + 6, TICKER, 2, WHITE)
    return fb


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    write_png(build(), dest)
    size = os.path.getsize(dest)
    if size == 0 or size > 1048576:
        raise SystemExit(f"entry.png bad size: {size}")
    print(f"wrote {dest} ({size} bytes)")


if __name__ == "__main__":
    main()
