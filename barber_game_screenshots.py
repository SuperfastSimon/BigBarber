from __future__ import annotations
"""
barber_game_screenshots.py

Generates three stylized PNG screenshots for a "Viral Barber Game":
 - Precision Cut (first-person arcade POV)
 - Street Brawl (side-scrolling 2D fight)
 - Split-screen Game Menu & Character Concept Art

This script uses Pillow and numpy to draw stylized, cel-shaded-ish scenes with neon/glow
and depth-of-field effects. It does not rely on external image assets — everything is
procedurally drawn so you can run it locally.

Dependencies:
 - pillow (PIL)
 - numpy

Install: pip install pillow numpy

Usage: python barber_game_screenshots.py

Generated files:
 - precision_cut.png
 - street_brawl.png
 - game_menu.png

"""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, List
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

OUT = Path(".")
OUT.mkdir(parents=True, exist_ok=True)

def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    # Attempt to load a nice system font; fallback to default PIL font
    try:
        # Try a common modern font; adjust path depending on platform
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        else:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except Exception:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            return ImageFont.load_default()


def clamp(v, a, b):
    return max(a, min(b, v))


def rounded_rect(draw: ImageDraw.ImageDraw, xy: Tuple[int, int, int, int], r: int, fill=None, outline=None, width: int = 1):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def radial_gradient(size: Tuple[int, int], inner_color, outer_color, center=None):
    w, h = size
    cx, cy = center if center else (w // 2, h // 2)
    maxr = math.hypot(max(cx, w - cx), max(cy, h - cy))
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    y, x = np.ogrid[0:h, 0:w]
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    t = (d / maxr)[:, :, None]
    inner = np.array(inner_color, dtype=np.float32)
    outer = np.array(outer_color, dtype=np.float32)
    col = inner * (1 - t) + outer * t
    arr = col.astype(np.uint8)
    return Image.fromarray(arr)


def neon_text(base: Image.Image, pos: Tuple[int, int], text: str, font: ImageFont.FreeTypeFont, color: Tuple[int, int, int], glow: Tuple[int, int, int], glow_radius: int = 18):
    """Draw text with outer neon glow by layering blurred text"""
    # Create mask
    txt = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    d.text(pos, text, font=font, fill=color + (255,))
    # make glow by expanding and blurring
    glow_img = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dg = ImageDraw.Draw(glow_img)
    dg.text(pos, text, font=font, fill=glow + (255,))
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(glow_radius))
    base.paste(glow_img, (0, 0), glow_img)
    base.paste(txt, (0, 0), txt)


def draw_glowing_spark(draw_canvas: Image.Image, origin: Tuple[int, int], angle: float, length: int, color: Tuple[int, int, int], intensity: int = 3):
    # Draw a little lightning-like spark with glow layers
    layer = Image.new("RGBA", draw_canvas.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ox, oy = origin
    # create jagged line points
    points = []
    steps = max(3, length // 8)
    for i in range(steps + 1):
        t = i / steps
        r = t * length
        jitter = (random.random() - 0.5) * 6 * (1 - t)
        x = ox + math.cos(angle) * r - math.sin(angle) * jitter
        y = oy + math.sin(angle) * r + math.cos(angle) * jitter
        points.append((x, y))
    # draw multiple strokes with increasing opacity/width
    for i in range(intensity, 0, -1):
        width = i * 2
        alpha = int(60 * (i / intensity))
        col = color + (alpha,)
        ld.line(points, fill=col, width=width)
    glow = layer.filter(ImageFilter.GaussianBlur(4))
    draw_canvas.paste(glow, (0, 0), glow)
    draw_canvas.paste(layer, (0, 0), layer)


# ---------------------------------------------------------------------------
# Scene 1: Precision Cut (First-person POV)
# ---------------------------------------------------------------------------

def draw_precision_cut(filename: Path, size=(1280, 720)):
    w, h = size
    base = Image.new("RGBA", size, (20, 20, 22, 255))

    # Background: blurred barbershop scene (suggested with shapes)
    bg = radial_gradient(size, (30, 28, 35), (12, 12, 14), center=(int(w * 0.65), int(h * 0.3)))
    # add faint mirror/product shapes
    bg_draw = ImageDraw.Draw(bg)
    for i in range(8):
        x = int(w * (0.08 + i * 0.11))
        y = int(h * 0.25 + (i % 3) * 10)
        box = [x, y, x + 80, y + 160]
        rounded_rect(bg_draw, box, r=8, fill=(40 + i * 6, 36 + i * 4, 42 + i * 3))
    bg = bg.filter(ImageFilter.GaussianBlur(8))
    base.paste(bg, (0, 0))

    draw = ImageDraw.Draw(base)

    # Depth-of-field vignette to simulate focus on clipper
    vignette = Image.new("L", size, 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.ellipse([-int(w * 0.2), -int(h * 0.2), int(w * 1.2), int(h * 1.2)], fill=200)
    vignette = vignette.filter(ImageFilter.GaussianBlur(120))
    base.putalpha(ImageChops.multiply(base.split()[-1], vignette)) if False else None

    # Foreground: player's hand holding golden clippers
    # Hand
    hand_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hand_layer)
    # wrist
    hd.ellipse((w * 0.42, h * 0.62, w * 0.58, h * 0.80), fill=(210, 160, 120))
    # fingers (stylized)
    for i in range(4):
        hx = w * (0.52 + i * -0.03)
        hy = h * (0.48 + i * 0.05)
        hd.ellipse((hx, hy, hx + w * 0.06, hy + h * 0.08), fill=(210, 160, 120))
    # small darker shading
    hd.polygon([(w * 0.45, h * 0.68), (w * 0.60, h * 0.56), (w * 0.62, h * 0.72)], fill=(180, 130, 100, 160))

    # Clipper: golden body, black guard, electric accents
    cx, cy = int(w * 0.55), int(h * 0.48)
    bw, bh = int(w * 0.26), int(h * 0.14)
    # body
    hd.rounded_rectangle([cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2], radius=18, fill=(212, 175, 55))
    # blade/head
    hd.rectangle([cx - bw // 2 - 6, cy - bh // 2 - 10, cx - bw // 2 + 30, cy - bh // 2 + 14], fill=(220, 220, 225))
    # guard
    hd.rectangle([cx + 20, cy - 6, cx + bw // 2 - 6, cy + 6], fill=(30, 30, 36))
    # details
    hd.ellipse([cx + bw // 4, cy - bh // 6, cx + bw // 4 + 14, cy - bh // 6 + 14], fill=(0, 0, 0))

    # Sparks & combo-hit effects
    spark_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    for i in range(12):
        angle = random.uniform(-math.pi / 3, math.pi / 3) + (-math.pi / 2)
        length = random.randint(40, 140)
        origin = (cx - bw // 2 + 8, cy - 4 + random.randint(-10, 10))
        draw_glowing_spark(spark_layer, origin, angle, length, (35, 170, 255), intensity=random.randint(2, 4))

    # Combo-hit floating text
    font_big = load_font(72, bold=True)
    combo_txt = "PERFECT FADE!"
    neon_text(spark_layer, (int(w * 0.42), int(h * 0.18)), combo_txt, font_big, (255, 255, 255), (120, 200, 255), glow_radius=26)

    # Precision meter on side
    meter_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    md = ImageDraw.Draw(meter_layer)
    mx = int(w * 0.9)
    my0 = int(h * 0.18)
    my1 = int(h * 0.82)
    rounded_rect(md, [mx - 28, my0, mx + 28, my1], r=12, fill=(20, 20, 24), outline=(130, 130, 190), width=3)
    # fill level
    level = 0.86
    lv_top = my1 - int((my1 - my0 - 10) * level)
    rounded_rect(md, [mx - 22, lv_top, mx + 22, my1 - 6], r=10, fill=(60, 220, 200))
    # tick marks
    for t in range(6):
        y = my0 + 10 + t * ((my1 - my0 - 20) / 5)
        md.line([(mx - 28, y), (mx - 18, y)], fill=(80, 80, 100), width=2)

    # Time Limit bar on top, blinking red
    tbar_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    td = ImageDraw.Draw(tbar_layer)
    tb_w = int(w * 0.7)
    tb_h = 28
    tb_x = int((w - tb_w) / 2)
    tb_y = int(h * 0.04)
    rounded_rect(td, [tb_x, tb_y, tb_x + tb_w, tb_y + tb_h], r=14, fill=(40, 40, 44))
    time_frac = 0.12
    time_fill_w = int(tb_w * time_frac)
    # blinking effect (simulate by bright red + faint outer glow)
    td.rectangle([tb_x + 4, tb_y + 4, tb_x + 4 + time_fill_w - 8, tb_y + tb_h - 4], fill=(240, 40, 40))
    # small 'Time Limit' text
    font_small = load_font(20, bold=True)
    td.text((tb_x + 8, tb_y + 4), "TIME LIMIT", font=font_small, fill=(255, 220, 220))

    # Combine layers
    base = Image.alpha_composite(base, hand_layer)
    base = Image.alpha_composite(base, spark_layer)
    base = Image.alpha_composite(base, meter_layer)
    base = Image.alpha_composite(base, tbar_layer)

    # Add stronger DOF blur for background region to emphasize foreground clipper
    fg_mask = Image.new("L", size, 0)
    md2 = ImageDraw.Draw(fg_mask)
    md2.ellipse([int(w * 0.26), int(h * 0.26), int(w * 0.86), int(h * 0.84)], fill=255)
    blurred = base.filter(ImageFilter.GaussianBlur(10))
    combined = Image.composite(base, blurred, fg_mask)

    # Slight cel-shaded posterize for stylized look
    r, g, b, a = combined.split()
    rgb = Image.merge("RGB", (r, g, b)).convert("P", palette=Image.ADAPTIVE, colors=256).convert("RGB")
    final = Image.merge("RGBA", (*rgb.split(), a))

    final.save(filename)
    print(f"Saved {filename}")


# ---------------------------------------------------------------------------
# Scene 2: Street Brawl (Side-scrolling 2D fighting screenshot)
# ---------------------------------------------------------------------------

def draw_street_brawl(filename: Path, size=(1365, 768)):
    w, h = size
    img = Image.new("RGBA", (w, h), (8, 8, 10, 255))
    draw = ImageDraw.Draw(img)

    # Background: dark barbershop with neon sign
    bg = radial_gradient((w, h), (8, 8, 12), (2, 2, 4), center=(int(w * 0.2), int(h * 0.2)))
    bdraw = ImageDraw.Draw(bg)
    # floor and chairs
    bdraw.rectangle([0, int(h * 0.7), w, h], fill=(18, 14, 10))
    for i in range(4):
        x = 120 + i * 280
        bdraw.rectangle([x, int(h * 0.62), x + 120, int(h * 0.7)], fill=(36, 24, 18))
        bdraw.line([x + 10, int(h * 0.62), x + 110, int(h * 0.62)], fill=(60, 40, 30), width=3)
    # neon sign
    neon_text(bg, (int(w * 0.45), int(h * 0.12)), "IT'S A CUT-THROAT BUSINESS", load_font(48, bold=True), (255, 20, 30), (255, 40, 60), glow_radius=18)
    bg = bg.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, bg)

    # Ground shadow line
    draw.line([(0, int(h * 0.69)), (w, int(h * 0.69))], fill=(10, 8, 7), width=6)

    # Players: stylized 2D sprites with thick outlines (cartoony 90s)
    # Helper to draw a character block with outline and portrait
    def draw_character(center_x, base_y, archetype: str):
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        # Body color by archetype
        if archetype == "Tank":
            body = (170, 70, 60)
            pants = (40, 40, 60)
            face = (210, 160, 120)
        elif archetype == "Technician":
            body = (70, 140, 160)
            pants = (30, 30, 36)
            face = (230, 190, 150)
        else:
            body = (120, 110, 80)
            pants = (30, 60, 90)
            face = (220, 180, 140)

        # torso (big block)
        t_w = int(w * 0.12)
        t_h = int(h * 0.23)
        tx0 = center_x - t_w // 2
        ty0 = base_y - t_h
        tx1 = center_x + t_w // 2
        ty1 = base_y
        ld.rounded_rectangle([tx0, ty0, tx1, ty1], radius=18, fill=body, outline=(0, 0, 0), width=6)
        # head
        hx = center_x
        hy = ty0 - int(h * 0.07)
        ld.ellipse([hx - 36, hy - 36, hx + 36, hy + 36], fill=face, outline=(0, 0, 0), width=6)
        # arms
        if archetype == "Tank":
            # muscular arms crossed or delivering super
            ld.rectangle([tx0 - 40, ty0 + 20, tx0 + 10, ty0 + 50], fill=body, outline=(0, 0, 0), width=6)
            ld.rectangle([tx1 - 10, ty0 + 20, tx1 + 40, ty0 + 50], fill=body, outline=(0, 0, 0), width=6)
            # beard
            ld.rectangle([hx - 18, hy + 10, hx + 18, hy + 28], fill=(70, 40, 30), outline=(0, 0, 0), width=4)
        elif archetype == "Technician":
            # slender arms with shears
            ld.line([(tx1, ty0 + 30), (tx1 + 60, ty0 + 10)], fill=body, width=14)
            # glasses and moustache
            ld.rectangle([hx - 28, hy - 6, hx - 6, hy + 10], fill=(255, 255, 255), outline=(0, 0, 0), width=3)
            ld.rectangle([hx + 6, hy - 6, hx + 28, hy + 10], fill=(255, 255, 255), outline=(0, 0, 0), width=3)
            ld.line([(hx - 6, hy + 12), (hx + 6, hy + 12)], fill=(70, 40, 30), width=4)
        else:
            # brawler
            ld.rectangle([tx0 - 30, ty0 + 20, tx0 + 6, ty0 + 60], fill=body, outline=(0, 0, 0), width=6)
            ld.rectangle([tx1 - 6, ty0 + 20, tx1 + 30, ty0 + 60], fill=body, outline=(0, 0, 0), width=6)

        # legs
        ld.rectangle([tx0 + 10, ty1, tx0 + 40, ty1 + 90], fill=pants, outline=(0, 0, 0), width=6)
        ld.rectangle([tx1 - 40, ty1, tx1 - 10, ty1 + 90], fill=pants, outline=(0, 0, 0), width=6)

        return layer

    # Player 1 (Left) - Tank performing Super Move
    left_x = int(w * 0.28)
    base_y = int(h * 0.72)
    tank_layer = draw_character(left_x, base_y, "Tank")
    # super move: glowing fist + foam shockwave
    sl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sld = ImageDraw.Draw(sl)
    # glowing fist (big circle in front of left character)
    fcx = left_x + 140
    fcy = base_y - 80
    for r, a in [(80, (255, 180, 40)), (110, (255, 120, 40)), (160, (255, 60, 30))]:
        tmp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        td.ellipse([fcx - r, fcy - r, fcx + r, fcy + r], fill=a + (40,))
        tmp = tmp.filter(ImageFilter.GaussianBlur(24))
        sl = Image.alpha_composite(sl, tmp)
    # fist core
    sld.ellipse([fcx - 38, fcy - 38, fcx + 38, fcy + 38], fill=(255, 230, 150), outline=(30, 20, 10), width=6)
    # foam shockwave: multiple concentric rings of white/foam
    for i in range(5):
        rad = 160 + i * 48
        alpha = int(120 * (1 - i * 0.18))
        sld.ellipse([fcx - rad, fcy - rad, fcx + rad, fcy + rad], outline=(240, 240, 250, alpha), width=12)
    # foam particles
    for _ in range(60):
        ang = random.random() * math.tau
        rr = random.random() ** 0.9 * 260
        px = fcx + math.cos(ang) * rr + random.randint(-8, 8)
        py = fcy + math.sin(ang) * rr + random.randint(-8, 8)
        ir = random.randint(4, 10)
        sld.ellipse([px - ir, py - ir, px + ir, py + ir], fill=(245, 245, 250, 220))

    # Player 2 (Right) - Technicus dodging
    right_x = int(w * 0.72)
    tech_layer = draw_character(right_x, base_y, "Technician")
    # pose: shifted back/up (simulate dodge)
    tech_layer = tech_layer.transform(tech_layer.size, Image.AFFINE, (1, 0, -40, 0, 1, -30), resample=Image.BICUBIC)

    # UI: health bars, portraits, timer, super meter
    ui = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ud = ImageDraw.Draw(ui)
    # health bars
    hb_w = int(w * 0.28)
    hb_h = 28
    # left
    l_x = int(w * 0.05)
    ud.rounded_rectangle([l_x, 18, l_x + hb_w, 18 + hb_h], radius=12, fill=(40, 40, 48))
    ud.rectangle([l_x + 6, 22, l_x + 6 + int(hb_w * 0.92), 18 + hb_h - 6], fill=(250, 220, 80))
    ud.ellipse([l_x - 4, 12, l_x + 12, 36], fill=(220, 160, 110), outline=(0, 0, 0), width=3)  # portrait placeholder
    # right
    r_x = int(w * 0.67)
    ud.rounded_rectangle([r_x, 18, r_x + hb_w, 18 + hb_h], radius=12, fill=(40, 40, 48))
    ud.rectangle([r_x + 6, 22, r_x + 6 + int(hb_w * 0.58), 18 + hb_h - 6], fill=(80, 220, 120))
    ud.ellipse([r_x + hb_w + 4 - 16, 12, r_x + hb_w + 4 + 12, 36], fill=(220, 160, 110), outline=(0, 0, 0), width=3)
    # timer
    font_mid = load_font(42, bold=True)
    ud.text((w // 2 - 24, 12), "99", font=font_mid, fill=(220, 220, 240))
    # super meter (bottom)
    sm_w = int(w * 0.6)
    sm_x = int((w - sm_w) / 2)
    sm_y = int(h * 0.88)
    ud.rounded_rectangle([sm_x, sm_y, sm_x + sm_w, sm_y + 26], radius=13, fill=(30, 30, 36))
    ud.rectangle([sm_x + 6, sm_y + 6, sm_x + 6 + sm_w - 12, sm_y + 20], fill=(40, 40, 48))
    # filled glowing super
    filled = sm_w - 12
    for i in range(6):
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        glow = (255, 120, 40 - i * 12)
        ld.rectangle([sm_x + 6, sm_y + 6, sm_x + 6 + filled, sm_y + 20], fill=(255, 120, 40, 80))
        layer = layer.filter(ImageFilter.GaussianBlur(6))
        ui = Image.alpha_composite(ui, layer)
    ud.rectangle([sm_x + 6, sm_y + 6, sm_x + 6 + filled, sm_y + 20], fill=(255, 120, 40))

    # combine everything
    composed = Image.alpha_composite(img, tank_layer)
    composed = Image.alpha_composite(composed, sl)
    composed = Image.alpha_composite(composed, tech_layer)
    composed = Image.alpha_composite(composed, ui)

    # retro 90s palette/posterize + edge-thickening to mimic hand-drawn thick lines
    edge = composed.filter(ImageFilter.FIND_EDGES).convert("L")
    edge = edge.point(lambda p: 255 if p > 40 else 0)
    edge_rgb = Image.merge("RGBA", (edge, edge, edge, edge)).filter(ImageFilter.GaussianBlur(1))
    nub = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    nub.paste(composed, (0, 0))
    nub = Image.alpha_composite(nub, edge_rgb)

    nub.save(filename)
    print(f"Saved {filename}")


# ---------------------------------------------------------------------------
# Scene 3: Split-screen Game Menu & Character Concept Art
# ---------------------------------------------------------------------------

def draw_game_menu(filename: Path, size=(1600, 900)):
    w, h = size
    img = Image.new("RGBA", (w, h), (14, 12, 10, 255))
    draw = ImageDraw.Draw(img)

    # Background: dark industrial barbershop
    bg = radial_gradient((w, h), (20, 18, 16), (6, 6, 8), center=(int(w * 0.45), int(h * 0.25)))
    bdraw = ImageDraw.Draw(bg)
    # neon sign center-left
    neon_text(bg, (int(w * 0.06), int(h * 0.06)), "IT'S A CUT-THROAT BUSINESS", load_font(56, bold=True), (255, 30, 40), (255, 40, 60), glow_radius=20)
    img = Image.alpha_composite(img, bg)

    # Screen split visually
    mid = w // 2
    draw.line([(mid, 0), (mid, h)], fill=(18, 16, 16), width=6)

    # Left option: PRECISION CUT
    left_bg = Image.new("RGBA", (mid - 40, h - 160), (18, 18, 20, 200))
    ldraw = ImageDraw.Draw(left_bg)
    rounded_rect(ldraw, [20, 20, left_bg.width - 20, left_bg.height - 20], r=22, fill=(26, 26, 30))
    # icon: crossed golden scissor and clipper
    cx = 120
    cy = 220
    # scissor (stylized)
    ldraw.line([(cx - 40, cy - 10), (cx + 40, cy + 10)], fill=(220, 190, 60), width=10)
    ldraw.line([(cx - 40, cy + 10), (cx + 40, cy - 10)], fill=(220, 190, 60), width=10)
    # clipper
    ldraw.rectangle([cx - 10, cy + 30, cx + 40, cy + 70], fill=(210, 170, 60), outline=(0, 0, 0), width=5)
    # label
    font_title = load_font(48, bold=True)
    ldraw.text((40, left_bg.height - 120), "PRECISION CUT", font=font_title, fill=(220, 220, 230))

    img.paste(left_bg, (20, 140), left_bg)

    # Right option: STREET BRAWL
    right_bg = Image.new("RGBA", (mid - 40, h - 160), (18, 18, 20, 200))
    rdraw = ImageDraw.Draw(right_bg)
    rounded_rect(rdraw, [20, 20, right_bg.width - 20, right_bg.height - 20], r=22, fill=(26, 26, 30))
    # icon: flaming fist
    fx = 200
    fy = 220
    for i, col in enumerate([(255, 180, 60), (255, 120, 40), (255, 60, 30)]):
        rdraw.ellipse([fx - 60 - i * 8, fy - 40 - i * 6, fx + 60 + i * 8, fy + 40 + i * 6], fill=col + (90,))
    rdraw.rectangle([fx - 30, fy - 10, fx + 30, fy + 40], fill=(200, 60, 40), outline=(0, 0, 0), width=6)
    rdraw.text((40, right_bg.height - 120), "STREET BRAWL", font=font_title, fill=(220, 220, 230))

    img.paste(right_bg, (mid + 20, 140), right_bg)

    # Characters: four employees as Street Fighter-like character portraits
    # We'll place two on each side, stylized
    char_positions = [
        (int(mid * 0.4), int(h * 0.32)),  # A (Tank)
        (int(mid * 0.6), int(h * 0.32)),  # B (All-rounder)
        (int(mid * 0.4), int(h * 0.57)),  # C (Brawler)
        (int(mid * 0.6), int(h * 0.57)),  # D (Technicus)
    ]

    def draw_character_concept(draw_to: Image.Image, pos: Tuple[int, int], archetype: str, label: str):
        lx, ly = pos
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        # base silhouette
        if archetype == "Tank":
            color = (170, 70, 60)
        elif archetype == "All-rounder":
            color = (100, 120, 160)
        elif archetype == "Brawler":
            color = (120, 80, 70)
        else:
            color = (70, 140, 160)
        # big torso
        tx0 = lx - 80
        ty0 = ly - 100
        tx1 = lx + 80
        ty1 = ly + 40
        ld.rounded_rectangle([tx0, ty0, tx1, ty1], radius=22, fill=color)
        # head detail
        ld.ellipse([lx - 36, ty0 - 64, lx + 36, ty0 - 8], fill=(220, 200, 170), outline=(0, 0, 0), width=6)
        # thick black outline to emulate 90s style
        ld.rounded_rectangle([tx0, ty0, tx1, ty1], radius=22, outline=(0, 0, 0), width=8)
        ld.ellipse([lx - 36, ty0 - 64, lx + 36, ty0 - 8], outline=(0, 0, 0), width=6)
        # accessories
        if archetype == "Tank":
            # beard & tattoos
            ld.rectangle([lx - 18, ty0 - 32, lx + 18, ty0 - 12], fill=(70, 40, 30))
            # tattoo stripes
            ld.line([(tx0 + 12, ty0 + 10), (tx0 + 40, ty0 + 30)], fill=(40, 20, 30), width=6)
        elif archetype == "Technicus":
            ld.rectangle([lx - 28, ty0 - 46, lx - 6, ty0 - 28], fill=(255, 255, 255))
            ld.rectangle([lx + 6, ty0 - 46, lx + 28, ty0 - 28], fill=(255, 255, 255))
            ld.line([(lx - 6, ty0 - 26), (lx + 6, ty0 - 26)], fill=(70, 40, 30), width=4)
            # scissors in hand
            ld.line([(tx1 - 20, ty0 + 10), (tx1 + 30, ty0 - 30)], fill=(150, 150, 150), width=8)
        # label
        f = load_font(24, bold=True)
        ld.text((tx0 + 6, ty1 + 8), label, font=f, fill=(230, 230, 230))
        draw_to.alpha_composite(layer)

    draw_character_concept(img, char_positions[0], "Tank", "CHARACTER A\n(Tank)")
    draw_character_concept(img, char_positions[1], "All-rounder", "CHARACTER B\n(All-rounder)")
    draw_character_concept(img, char_positions[2], "Brawler", "CHARACTER C\n(Brawler)")
    draw_character_concept(img, char_positions[3], "Technicus", "CHARACTER D\n(Technicus)")

    # Title header
    font_header = load_font(64, bold=True)
    neon_text(img, (int(w * 0.06), int(h * 0.02)), "BARBER BRAWLAR: SELECT MODE", font_header, (255, 255, 255), (120, 200, 255), glow_radius=24)

    img.save(filename)
    print(f"Saved {filename}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Ensure compatibility with platforms missing ImageChops.multiply earlier usage
    try:
        from PIL import ImageChops  # noqa
    except Exception:
        pass

    draw_precision_cut(OUT / "precision_cut.png")
    draw_street_brawl(OUT / "street_brawl.png")
    draw_game_menu(OUT / "game_menu.png")

    print("All images generated.")
