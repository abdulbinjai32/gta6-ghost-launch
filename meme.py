#!/usr/bin/env python3
"""GTA 6 launch-week meme for make.fun bounty gta6-meme-x-01.

The joke: a fan waited 13 years for GTA 6, died, came back as the make.fun
ghost ... and the 150 GB download is STILL stuck at 99%. The official make.fun
ghost mark is the main character, floating in a Vice City synthwave sunset with
the striped sun as a halo behind it.

Deterministic: fixed-seed stars only, no network. Pure Pillow.
Run:  python3 meme.py   -> writes meme.png (1080x1080).
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
W = H = 1080
HORIZON = 716

# make.fun brand
MAGENTA = (196, 28, 131)      # #C41C83
CANVAS = (17, 20, 27)         # #11141B
INK = (224, 229, 239)         # #E0E5EF
NEAR_BLACK = (8, 9, 15)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_FREE = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"

# composition anchors
GHOST_CX, GHOST_CY, GHOST_SIZE = W // 2, 555, 440
SUN_CX, SUN_CY, SUN_R = W // 2, 555, 305


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def gradient_column(stops, height):
    """1px wide vertical gradient; stops = [(frac, (r,g,b)), ...]."""
    col = Image.new("RGB", (1, height))
    px = col.load()
    for y in range(height):
        f = y / max(1, height - 1)
        for i in range(len(stops) - 1):
            f0, c0 = stops[i]
            f1, c1 = stops[i + 1]
            if f0 <= f <= f1:
                t = (f - f0) / (f1 - f0) if f1 > f0 else 0
                px[0, y] = lerp(c0, c1, t)
                break
        else:
            px[0, y] = stops[-1][1]
    return col


def draw_sky(img):
    stops = [
        (0.00, (9, 11, 24)),
        (0.30, (34, 17, 66)),
        (0.55, (92, 26, 110)),
        (0.78, (168, 33, 122)),
        (0.92, (226, 74, 110)),
        (1.00, (255, 158, 92)),
    ]
    sky = gradient_column(stops, HORIZON).resize((W, HORIZON), Image.BILINEAR)
    img.paste(sky, (0, 0))
    floor_stops = [(0.0, (12, 10, 22)), (1.0, (5, 5, 10))]
    fh = H - HORIZON
    floor = gradient_column(floor_stops, fh).resize((W, fh), Image.BILINEAR)
    img.paste(floor, (0, HORIZON))


def draw_stars(img):
    rng = random.Random(6)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(90):
        x = rng.randint(0, W)
        y = rng.randint(0, int(HORIZON * 0.42))
        r = rng.choice([1, 1, 1, 2])
        a = rng.randint(90, 220)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(235, 238, 250, a))


def draw_sun(img):
    cx, cy, R = SUN_CX, SUN_CY, SUN_R
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad_stops = [(0.0, (255, 236, 170)), (0.45, (255, 178, 92)),
                  (0.75, (255, 110, 120)), (1.0, (230, 60, 140))]
    box = 2 * R
    col = gradient_column(grad_stops, box).resize((box, box), Image.BILINEAR)
    mask = Image.new("L", (box, box), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, box - 1, box - 1], fill=255)
    sun = Image.new("RGBA", (box, box), (0, 0, 0, 0))
    sun.paste(col, (0, 0), mask)
    # scanline slits in lower half (gaps grow toward bottom)
    sd = ImageDraw.Draw(sun)
    y = int(box * 0.52)
    gap = 3
    while y < box:
        sd.rectangle([0, y, box, y + gap], fill=(0, 0, 0, 0))
        y += gap + 13
        gap = min(gap + 2, 22)
    layer.paste(sun, (cx - R, cy - R), sun)
    # clip below horizon
    la = layer.load()
    for yy in range(HORIZON, H):
        for xx in range(max(0, cx - R), min(W, cx + R)):
            r, g, b, a = la[xx, yy]
            la[xx, yy] = (r, g, b, 0)
    img.alpha_composite(layer)


def draw_grid(img):
    d = ImageDraw.Draw(img, "RGBA")
    vpx, vpy = W // 2, HORIZON
    n = 12
    for i in range(1, n + 1):
        t = i / n
        y = HORIZON + int((H - HORIZON) * (t ** 1.9))
        a = int(60 + 150 * t)
        d.line([(0, y), (W, y)], fill=MAGENTA + (a,), width=2)
    for k in range(-9, 10):
        xb = W // 2 + k * 130
        d.line([(vpx, vpy), (xb, H)], fill=MAGENTA + (90,), width=2)
    d.line([(0, HORIZON), (W, HORIZON)], fill=(255, 120, 160, 200), width=3)


def draw_bottom_scrim(img):
    """Clean dark footer panel so grid lines never cross the bottom text."""
    col = Image.new("RGBA", (1, H), (0, 0, 0, 0))
    px = col.load()
    for y in range(H):
        if y < 736:
            a = 0
        elif y < 786:
            a = int(238 * (y - 736) / 50)
        else:
            a = 238
        px[0, y] = CANVAS + (a,)
    scrim = col.resize((W, H), Image.BILINEAR)
    img.alpha_composite(scrim)


def draw_frond(d, cx, cy, angle_deg, length, droop, maxw, color):
    a = math.radians(angle_deg)
    pts_l, pts_r = [], []
    steps = 22
    prev = None
    for i in range(steps + 1):
        t = i / steps
        x = cx + math.cos(a) * length * t
        y = cy + math.sin(a) * length * t + droop * length * (t ** 2)
        if prev is None:
            tx, ty = math.cos(a), math.sin(a)
        else:
            tx, ty = x - prev[0], y - prev[1]
            n = math.hypot(tx, ty) or 1
            tx, ty = tx / n, ty / n
        nx, ny = -ty, tx
        w = maxw * ((1 - t) ** 0.8) * (0.35 + 0.65 * math.sin(math.pi * min(t * 1.2, 1)))
        pts_l.append((x + nx * w, y + ny * w))
        pts_r.append((x - nx * w, y - ny * w))
        prev = (x, y)
    d.polygon(pts_l + pts_r[::-1], fill=color)


def draw_palm(img, base_x, base_y, crown_x, crown_y, scale, color):
    d = ImageDraw.Draw(img, "RGBA")
    ctrl_x = (base_x + crown_x) / 2 + (crown_x - base_x) * 0.15
    ctrl_y = (base_y + crown_y) / 2
    pts_l, pts_r = [], []
    steps = 24
    prev = None
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * base_x + 2 * (1 - t) * t * ctrl_x + t ** 2 * crown_x
        y = (1 - t) ** 2 * base_y + 2 * (1 - t) * t * ctrl_y + t ** 2 * crown_y
        if prev is None:
            tx, ty = crown_x - base_x, crown_y - base_y
        else:
            tx, ty = x - prev[0], y - prev[1]
        n = math.hypot(tx, ty) or 1
        nx, ny = -ty / n, tx / n
        w = (24 - 13 * t) * scale
        pts_l.append((x + nx * w, y + ny * w))
        pts_r.append((x - nx * w, y - ny * w))
        prev = (x, y)
    d.polygon(pts_l + pts_r[::-1], fill=color)
    for ang in [-168, -140, -112, -85, -58, -30, -8, 12]:
        length = 150 * scale * (0.85 + 0.3 * abs(math.sin(math.radians(ang))))
        draw_frond(d, crown_x, crown_y, ang, length, 0.55, 20 * scale, color)
    d.ellipse([crown_x - 10 * scale, crown_y - 4 * scale,
               crown_x + 8 * scale, crown_y + 12 * scale], fill=color)


def draw_glow(img, cx, cy, radius, color, alpha):
    """Soft radial scene-lighting glow behind the mark (background only)."""
    size = radius * 2
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(radius, 0, -2):
        a = int(alpha * (1 - r / radius) ** 1.6)
        gd.ellipse([radius - r, radius - r, radius + r, radius + r],
                   fill=color + (a,))
    img.alpha_composite(glow, (cx - radius, cy - radius))


def big_text(d, cx, cy, text, fnt, fill=INK, stroke=6, shadow=True):
    if shadow:
        d.text((cx + 4, cy + 6), text, font=fnt, fill=(0, 0, 0, 190),
               anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0, 190))
    d.text((cx, cy), text, font=fnt, fill=fill, anchor="mm",
           stroke_width=stroke, stroke_fill=NEAR_BLACK + (255,))


def fit_font(path, text, max_w, start):
    size = start
    while size > 20:
        f = font(path, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 2
    return font(path, 20)


def draw_loading_bar(img, d):
    lab = font(FONT_BOLD, 33)
    big_text(d, W // 2, 806, "GTA 6  ·  150 GB DOWNLOAD", lab, fill=INK, stroke=3)
    x0, x1, y0, y1 = 172, 792, 834, 870
    # lighter empty track so the unfilled 1% sliver is visible
    d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=(46, 49, 64, 255),
                        outline=INK + (255,), width=3)
    inner_w = x1 - x0 - 8
    fill_w = int(inner_w * 0.99)
    d.rounded_rectangle([x0 + 4, y0 + 4, x0 + 4 + fill_w, y1 - 4],
                        radius=14, fill=MAGENTA + (255,))
    # 99% sits cleanly OUTSIDE the bar, to the right
    pct = font(FONT_BOLD, 42)
    cy = (y0 + y1) // 2
    d.text((x1 + 30, cy + 3), "99%", font=pct, fill=(0, 0, 0, 190),
           anchor="lm", stroke_width=4, stroke_fill=(0, 0, 0, 190))
    d.text((x1 + 28, cy), "99%", font=pct, fill=INK, anchor="lm",
           stroke_width=4, stroke_fill=NEAR_BLACK + (255,))


def draw_wordmark(img, d, cx, cy):
    f = font(FONT_FREE, 54)
    left, dot, right = "make", ".", "fun"
    wl, wd, wr = f.getlength(left), f.getlength(dot), f.getlength(right)
    x = cx - (wl + wd + wr) / 2
    for seg, col in ((left, INK), (dot, MAGENTA), (right, INK)):
        d.text((x, cy), seg, font=f, fill=col, anchor="lm",
               stroke_width=3, stroke_fill=NEAR_BLACK + (255,))
        x += f.getlength(seg)


def main():
    img = Image.new("RGBA", (W, H), CANVAS + (255,))
    draw_sky(img)
    draw_stars(img)
    draw_sun(img)
    draw_grid(img)
    # palms frame the sides, clear of the ghost
    draw_palm(img, 108, HORIZON + 6, 150, 356, 1.05, NEAR_BLACK + (255,))
    draw_palm(img, 972, HORIZON + 6, 930, 340, 1.12, NEAR_BLACK + (255,))
    # glow + official ghost mark (as-is, uniform scale), sun halo behind
    draw_glow(img, GHOST_CX, GHOST_CY, 330, (255, 120, 170), 70)
    # clean footer panel drawn UNDER the mark so the ghost stays untouched
    draw_bottom_scrim(img)
    mark = Image.open(os.path.join(BASE, "assets", "mark-on-dark-1024.png")).convert("RGBA")
    mark = mark.resize((GHOST_SIZE, GHOST_SIZE), Image.LANCZOS)
    img.alpha_composite(mark, (GHOST_CX - GHOST_SIZE // 2, GHOST_CY - GHOST_SIZE // 2))

    d = ImageDraw.Draw(img, "RGBA")
    big_text(d, W // 2, 88, "WAITED 13 YEARS", font(FONT_BOLD, 92))
    big_text(d, W // 2, 190, "FOR GTA 6", font(FONT_BOLD, 92))
    draw_loading_bar(img, d)
    bottom = fit_font(FONT_BOLD, "DIED. CAME BACK. STILL LOADING.", 1010, 70)
    big_text(d, W // 2, 924, "DIED. CAME BACK. STILL LOADING.", bottom)
    draw_wordmark(img, d, W // 2, 1016)

    img.convert("RGB").save(os.path.join(BASE, "meme.png"), "PNG")
    print("wrote meme.png", img.size)


if __name__ == "__main__":
    main()
