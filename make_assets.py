#!/usr/bin/env python3
"""Generates favicons and 1200x630 share images (Open Graph). Run: python3 make_assets.py"""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import numpy as np

I = "assets/img"
RED = (224, 57, 57)
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

def cover(img, w, h, focus=(0.5, 0.5)):
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = round((img.width - w) * focus[0]); y = round((img.height - h) * focus[1])
    return img.crop((x, y, x + w, y + h))

def grade(img):
    """warm tint + film grain + vignette, echoing the hero"""
    img = img.convert("RGB")
    tint = Image.new("RGB", img.size, (122, 70, 50))
    img = ImageChops.multiply(img, Image.blend(Image.new("RGB", img.size, (255, 255, 255)), tint, 0.6))
    a = np.asarray(img).astype("float32")
    rng = np.random.default_rng(7)
    a += rng.normal(0, 9, a.shape[:2])[..., None]
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a *= (1 - 0.55 * np.clip(d - 0.55, 0, 1))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))

def spaced(draw, xy, text, font, fill, track=6):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track

def og_page(label, out):
    base = grade(cover(Image.open(f"{I}/hero-poster.jpg"), 1200, 630))
    logo = Image.open(f"{I}/logo-white.png").convert("RGBA")
    lw = 600; logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    base = base.convert("RGBA"); base.alpha_composite(logo, (90, 215))
    d = ImageDraw.Draw(base)
    spaced(d, (96, 560), label.upper(), ImageFont.truetype(BOLD, 28), RED, 7)
    base.convert("RGB").save(f"{I}/{out}", quality=88, optimize=True)

def glow_bg(w=1200, h=630, cx=0.5, cy=0.42):
    """sepia glow on black with fine grain + vignette, matching the home title card"""
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - cx * w) / (w * 0.62)) ** 2 + ((yy - cy * h) / (h * 0.75)) ** 2)
    stops = [(0, (107, 64, 48)), (0.35, (58, 33, 24)), (0.7, (21, 11, 8)), (1.0, (0, 0, 0))]
    a = np.zeros((h, w, 3), "float32")
    for (d0, c0), (d1, c1) in zip(stops, stops[1:]):
        m = (d >= d0) & (d < d1); t = ((d - d0) / (d1 - d0))[m][:, None]
        a[m] = np.array(c0) * (1 - t) + np.array(c1) * t
    a += np.random.default_rng(11).normal(0, 6, (h, w))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8")).convert("RGBA")

def og_v2(label, out, portrait=False):
    base = glow_bg(cx=0.68 if portrait else 0.5)
    logo = Image.open(f"{I}/logo-white.png").convert("RGBA")
    if portrait:
        hs = Image.open(f"{I}/headshot.jpg").convert("L")
        hs = cover(hs, 480, 630, (0.5, 0.15))
        a = np.asarray(hs).astype("float32")
        fade = np.clip((480 - np.arange(480)) / 200, 0, 1)[None, :]
        warm = np.stack([a * 1.0, a * 0.82, a * 0.72], -1)
        ph = Image.fromarray(np.clip(warm, 0, 255).astype("uint8")).convert("RGBA")
        ph.putalpha(Image.fromarray((fade * 255 * np.ones((630, 1))).astype("uint8")))
        base.alpha_composite(ph, (0, 0))
        lw, lx = 560, 570
    else:
        lw, lx = 640, 280
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    ly = 215 if not portrait else 200
    base.alpha_composite(logo, (lx, ly))
    d = ImageDraw.Draw(base)
    f = ImageFont.truetype(BOLD, 22)
    txt = label.upper(); tw = sum(d.textlength(c, font=f) + 5 for c in txt) - 5
    spaced(d, (lx + (lw - tw) / 2, ly + logo.height + 40), txt, f, RED, 5)
    base.convert("RGB").save(f"{I}/{out}", quality=88, optimize=True)

def og_film(title, src, out, focus=(0.5, 0.5)):
    base = cover(Image.open(src), 1200, 630, focus).convert("RGB")
    sh = Image.new("L", base.size, 0); g = ImageDraw.Draw(sh)
    for y in range(630):
        g.line([(0, y), (1200, y)], fill=int(max(0, (y - 330) / 300) * 215))
    base = Image.composite(Image.new("RGB", base.size, (0, 0, 0)), base, sh).convert("RGBA")
    d = ImageDraw.Draw(base)
    spaced(d, (60, 500), title.upper(), ImageFont.truetype(BOLD, 52), (255, 255, 255), 5)
    spaced(d, (62, 566), "A FILM BY J. PENBERTH RABOLD", ImageFont.truetype(BOLD, 22), RED, 5)
    base.convert("RGB").save(f"{I}/{out}", quality=88, optimize=True)

def favicons():
    """Simple monogram: brand-red J on black. Legible at 16px, unlike the hairline signature."""
    S = 512
    tile = Image.new("RGB", (S, S), (0, 0, 0))
    d = ImageDraw.Draw(tile)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 400)
    l, t, r, b = d.textbbox((0, 0), "J", font=f)
    d.text(((S - (r - l)) / 2 - l, (S - (b - t)) / 2 - t), "J", font=f, fill=RED)
    tile.save(f"{I}/favicon-512.png", optimize=True)
    for n in (180, 64, 32, 16):
        tile.resize((n, n), Image.LANCZOS).save(f"{I}/{'apple-touch-icon' if n == 180 else 'favicon-' + str(n)}.png", optimize=True)
    tile.resize((64, 64), Image.LANCZOS).save("favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

if __name__ == "__main__":
    favicons()
    og_v2("Writer | Director | Filmmaker", "og-v2-home.jpg", True)
    og_v2("Biography", "og-v2-biography.jpg", True)
    for label, out in (("Filmography", "og-v2-filmography.jpg"), ("Writing", "og-v2-writing.jpg"),
                       ("Credits", "og-v2-credits.jpg"), ("Contact", "og-v2-contact.jpg")):
        og_v2(label, out)
    # Dallas & Allegra: its own key art, cropped to the share ratio (title sits near the top)
    cover(Image.open(f"{I}/da/hero-skyline-wide.jpg"), 1200, 630, (0.5, 0.12)).convert("RGB").save(f"{I}/og-dallas-and-allegra.jpg", quality=88, optimize=True)
    if os.path.exists(f"{I}/stills/almost-super.jpg"):
        og_film("Almost Super", f"{I}/stills/almost-super.jpg", "og-almost-super.jpg")
    print("assets written:", sorted(f for f in os.listdir(I) if f.startswith(("og-", "favicon", "apple"))))
