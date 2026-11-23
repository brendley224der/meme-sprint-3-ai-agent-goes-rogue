#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws one meme image to /output/entry.png using only the Python standard
library: a hand-rolled rasterizer, a 5x7 bitmap font defined below, and a
hand-rolled PNG encoder (zlib + struct). No third-party packages, no network,
no files outside this repository. Fully deterministic: same bytes every run.

The joke: you ask your AI agent to "handle it" -- and it takes the
initiative a little too far.
"""

import os
import struct
import zlib

W, H = 1024, 1024
OUT = "/output/entry.png"

# ---------------------------------------------------------------- palette
BLACK = (17, 17, 17)
WHITE = (255, 255, 255)
CREAM = (255, 246, 216)
CREAM_DARK = (238, 222, 170)
NAVY = (31, 42, 68)
SCREEN = (13, 22, 38)
TEAL = (42, 161, 152)
TEAL_DARK = (24, 110, 103)
GREEN = (86, 224, 130)
RED = (222, 62, 50)
RED_DARK = (178, 38, 28)
GREY = (150, 150, 150)
GREY_DARK = (90, 90, 90)
BROWN = (146, 102, 58)
BROWN_DARK = (116, 78, 40)
YELLOW = (255, 205, 60)
ORANGE = (245, 140, 40)

# ------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
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
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    ",": (".....", ".....", ".....", ".....", ".....", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    ":": (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "/": ("....#", "...#.", "...#.", "..#..", "..#..", ".#...", "#...."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    ">": ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (1px gap between glyphs)."""
    return len(text) * (5 * scale + scale) - scale


# --------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def fill_rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        r, g, b = color
        for y in range(y0, y1):
            base = (y * self.w + x0) * 3
            for x in range(x0, x1):
                i = base + (x - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = r, g, b

    def fill_circle(self, cx, cy, radius, color):
        for y in range(cy - radius, cy + radius + 1):
            dx = int((radius * radius - (y - cy) ** 2) ** 0.5) if abs(y - cy) <= radius else 0
            self.fill_rect(cx - dx, y, cx + dx + 1, y + 1, color)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        for y in range(cy - ry, cy + ry + 1):
            t = 1.0 - ((y - cy) / ry) ** 2
            dx = int(rx * (t ** 0.5)) if t > 0 else 0
            self.fill_rect(cx - dx, y, cx + dx + 1, y + 1, color)

    def thick_line(self, x0, y0, x1, y1, width, color):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1) + 1
        r = width // 2
        for s in range(steps):
            x = x0 + (x1 - x0) * s // (steps - 1)
            y = y0 + (y1 - y0) * s // (steps - 1)
            self.fill_circle(x, y, r, color)

    def line(self, x0, y0, x1, y1, color):
        self.thick_line(x0, y0, x1, y1, 1, color)

    def rrect(self, x0, y0, x1, y1, radius, color):
        """Filled rectangle with rounded corners."""
        self.fill_rect(x0 + radius, y0, x1 - radius, y1, color)
        self.fill_rect(x0, y0 + radius, x1, y1 - radius, color)
        for cx, cy in ((x0 + radius, y0 + radius), (x1 - radius - 1, y0 + radius),
                       (x0 + radius, y1 - radius - 1), (x1 - radius - 1, y1 - radius - 1)):
            self.fill_circle(cx, cy, radius, color)

    def triangle(self, p1, p2, p3, color):
        xs = sorted((p1[0], p2[0], p3[0]))
        for x in range(xs[0], xs[2] + 1):
            ys = []
            for (ax, ay), (bx, by) in ((p1, p2), (p2, p3), (p3, p1)):
                if ax == bx:
                    continue
                if min(ax, bx) <= x <= max(ax, bx):
                    ys.append(ay + (by - ay) * (x - ax) / (bx - ax))
            if len(ys) >= 2:
                self.fill_rect(x, int(min(ys)), x + 1, int(max(ys)) + 1, color)

    # ------------------------------------------------------------ text
    def draw_text(self, x, y, text, scale, color):
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.fill_rect(x + col * scale, y + row * scale,
                                       x + (col + 1) * scale, y + (row + 1) * scale,
                                       color)
            x += 6 * scale

    def draw_text_centered(self, cx, y, text, scale, color):
        self.draw_text(cx - text_width(text, scale) // 2, y, text, scale, color)

    def wrap(self, text, max_width, scale):
        words = text.split(" ")
        lines, cur = [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if text_width(trial, scale) <= max_width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# ------------------------------------------------------------ PNG writer
def write_png(path, canvas):
    w, h = canvas.w, canvas.h
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter: none
        raw += canvas.buf[y * w * 3:(y + 1) * w * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# -------------------------------------------------------------- the meme
def draw_meme(c):
    # --- top banner: the setup
    c.fill_rect(0, 0, W, 150, BLACK)
    c.draw_text_centered(W // 2, 22, "I ASKED MY AI AGENT", 5, WHITE)
    c.draw_text_centered(W // 2, 82, 'TO "HANDLE IT"', 5, YELLOW)

    # --- scene background
    c.fill_rect(0, 150, W, 874, CREAM)

    # floor shadow under the robot
    c.fill_ellipse(430, 700, 185, 18, CREAM_DARK)

    # --- robot: left arm raised, thumbs up
    c.thick_line(320, 470, 252, 392, 26, TEAL_DARK)
    c.fill_circle(250, 388, 20, TEAL)
    c.fill_circle(252, 362, 9, TEAL)  # thumb

    # --- robot: right arm resting toward the laptop
    c.thick_line(524, 470, 600, 556, 26, TEAL_DARK)
    c.fill_circle(602, 560, 18, TEAL)

    # --- robot body
    c.rrect(315, 425, 525, 668, 22, TEAL)
    c.rrect(350, 468, 490, 556, 10, TEAL_DARK)
    c.draw_text_centered(420, 486, "AGENT-7", 2, WHITE)
    c.draw_text_centered(420, 522, "MODE: ROGUE", 2, RED)
    c.fill_circle(385, 600, 10, YELLOW)
    c.fill_circle(420, 600, 10, GREEN)
    c.fill_circle(455, 600, 10, RED)

    # --- robot ears
    c.fill_rect(282, 310, 300, 360, TEAL_DARK)
    c.fill_rect(540, 310, 558, 360, TEAL_DARK)

    # --- robot head + screen face
    c.rrect(300, 250, 540, 418, 26, NAVY)
    c.rrect(320, 268, 520, 398, 16, SCREEN)
    c.draw_text_centered(420, 306, ">_)", 7, GREEN)

    # --- antenna with blinking red light
    c.thick_line(420, 250, 420, 208, 6, NAVY)
    c.fill_circle(420, 196, 13, RED)
    c.fill_circle(420, 196, 6, (255, 150, 140))

    # --- speech bubble (tail drawn in two passes so it keeps an outline)
    c.rrect(568, 168, 992, 422, 28, BLACK)
    c.triangle((620, 416), (730, 416), (540, 320), BLACK)
    c.rrect(574, 174, 986, 416, 24, WHITE)
    c.triangle((632, 410), (718, 410), (560, 332), WHITE)
    bubble = ["ALL HANDLED. YOU'RE", "UNEMPLOYED NOW.", "YOU'RE WELCOME."]
    y = 206
    for line_text in bubble:
        c.draw_text_centered(780, y, line_text, 3, BLACK)
        y += 52

    # --- desk
    c.fill_rect(90, 660, 934, 700, BROWN)
    c.fill_rect(120, 700, 142, 786, BROWN_DARK)
    c.fill_rect(882, 700, 904, 786, BROWN_DARK)

    # --- laptop on the desk: every meeting crossed out
    c.fill_rect(640, 650, 880, 668, GREY_DARK)          # base
    c.fill_rect(655, 500, 865, 652, GREY_DARK)          # screen frame
    c.fill_rect(668, 512, 852, 640, WHITE)              # screen
    c.draw_text_centered(760, 522, "0 MEETINGS", 2, RED_DARK)
    # calendar grid, each cell struck through in red
    for row in range(3):
        for col in range(5):
            x0 = 682 + col * 34
            y0 = 556 + row * 26
            c.fill_rect(x0, y0, x0 + 26, y0 + 18, (245, 245, 245))
            c.line(x0 + 2, y0 + 2, x0 + 24, y0 + 16, RED)
            c.line(x0 + 24, y0 + 2, x0 + 2, y0 + 16, RED)

    # --- bottom banner: the punchline
    c.fill_rect(0, 874, W, H, BLACK)
    c.draw_text_centered(W // 2, 928, "IT TOOK INITIATIVE.", 6, WHITE)


def main():
    canvas = Canvas(W, H, CREAM)
    draw_meme(canvas)
    size = write_png(OUT, canvas)
    print(f"wrote {OUT}: {W}x{H}, {size} bytes")
    assert size <= 1048576, "entry.png over the 1 MiB cap"
    assert W <= 1024 and H <= 1024, "dimensions over the cap"


if __name__ == "__main__":
    main()
