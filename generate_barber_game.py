from __future__ import annotations
"""
generate_barber_game.py

Creates three stylized, cel-shaded arcade-style images for a "Viral Barber Game" concept:
 - gameplay1.png  -> The Precision Cut (first-person POV)
 - gameplay2.png  -> The Street Brawl (side-scrolling fighting screenshot)
 - menu.png       -> Split-screen game menu + character concept art

Dependencies: pillow, numpy
Install: pip install --upgrade pillow numpy

This script aims to produce art-like screenshots programmatically (stylized shapes, outlines, and effects)
"""

from dataclasses import dataclass
from math import sin, cos, pi
import os
from typing import Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import numpy as np

# Configuration
OUTPUT_DIR = "output"
WIDTH, HEIGHT = 1280, 720
FONT_PATH = None  # Use default PIL font fallback

# Utility types
Color = Tuple[int, int, int, int]


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        if FONT_PATH and os.path.exists(FONT_PATH):
            return ImageFont.truetype(FONT_PATH, size)
        # Try a common system font first
        try:
            return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
        except Exception:
            return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def shadowed_text(draw: ImageDraw.Draw, xy: Tuple[int, int], text: str, font: ImageFont.FreeTypeFont,
                  fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0)):
    # Draw text with an outline for arcade feel
    x, y = xy
    # Pillow's text supports stroke in newer versions
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


# Cel-outline helper: draw a thick black version behind shape
def draw_cel_ellipse(draw: ImageDraw.Draw, bbox, fill, outline_thickness=10):
    x0, y0, x1, y1 = bbox
    # draw outline by drawing multiple ellipses smaller
    draw.ellipse((x0 - outline_thickness, y0 - outline_thickness, x1 + outline_thickness, y1 + outline_thickness), fill=(0, 0, 0))
    draw.ellipse(bbox, fill=fill)


def draw_first_person_precision_cut(path: str):
    W, H = WIDTH, HEIGHT
    base = Image.new("RGBA", (W, H), (20, 20, 25, 255))
    draw = ImageDraw.Draw(base)

    # Background (barbershop with blur)
    bg = Image.new("RGBA", (W, H), (40, 40, 45, 255))
    bg_draw = ImageDraw.Draw(bg)
    # Draw simple mirror shapes and shelves
    for i in range(3):
        mx = 200 + i * 300
        my = 120
        mw, mh = 220, 300
        # mirror
        bg_draw.rectangle((mx, my, mx + mw, my + mh), fill=(60, 60, 70))
        # shelf
        bg_draw.rectangle((mx, my + mh + 10, mx + mw, my + mh + 30), fill=(80, 60, 40))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=12))
    base = Image.alpha_composite(base, bg)
    draw = ImageDraw.Draw(base)

    # Foreground: Hand holding a golden clipper (simplified shapes + outlines)
    # Hand
    hand_color = (255, 220, 180)
    glove_color = (230, 200, 170)
    # palm
    draw_cel_ellipse(draw, (W * 0.22, H * 0.55, W * 0.5, H * 0.82), fill=hand_color, outline_thickness=12)
    # fingers (simplified)
    for i in range(4):
        fx0 = W * (0.5 - i * 0.04)
        draw.rectangle((fx0, H * 0.62, fx0 + 24, H * 0.75), fill=hand_color)
        # finger outline
        draw.rectangle((fx0 - 4, H * 0.62 - 4, fx0 + 24 + 4, H * 0.75 + 4), fill=(0, 0, 0))
        draw.rectangle((fx0, H * 0.62, fx0 + 24, H * 0.75), fill=hand_color)

    # Golden clipper body
    clip_x0, clip_y0 = int(W * 0.45), int(H * 0.48)
    clip_x1, clip_y1 = int(W * 0.75), int(H * 0.64)
    # outline
    draw.rectangle((clip_x0 - 8, clip_y0 - 8, clip_x1 + 8, clip_y1 + 8), fill=(0, 0, 0))
    # gold gradient (simple)
    gold_top = (255, 215, 90)
    gold_bottom = (200, 150, 60)
    for i in range(clip_y1 - clip_y0):
        t = i / max(1, (clip_y1 - clip_y0))
        r = int(gold_top[0] * (1 - t) + gold_bottom[0] * t)
        g = int(gold_top[1] * (1 - t) + gold_bottom[1] * t)
        b = int(gold_top[2] * (1 - t) + gold_bottom[2] * t)
        draw.line((clip_x0, clip_y0 + i, clip_x1, clip_y0 + i), fill=(r, g, b))
    # blade
    blade_box = (clip_x1 - 24, clip_y0 + 6, clip_x1 + 8, clip_y1 - 6)
    draw.rectangle(blade_box, fill=(220, 230, 255))
    draw.rectangle((blade_box[0] - 3, blade_box[1] - 3, blade_box[2] + 3, blade_box[3] + 3), outline=(0, 0, 0))

    # Electric sparks (electric blue) using particle noise
    sparks = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sp_draw = ImageDraw.Draw(sparks)
    rng = np.random.default_rng(42)
    center_x = clip_x1 - 6
    center_y = int((clip_y0 + clip_y1) / 2)
    for _ in range(140):
        angle = rng.random() * 2 * pi
        radius = rng.random() ** 0.5 * 140
        x = int(center_x + cos(angle) * radius)
        y = int(center_y + sin(angle) * radius * 0.6)
        size = int(rng.integers(1, 6))
        brightness = int(180 + rng.integers(0, 75))
        col = (30, 170, 255, brightness)
        sp_draw.ellipse((x - size, y - size, x + size, y + size), fill=col)
    sparks = sparks.filter(ImageFilter.GaussianBlur(radius=1))
    base = Image.alpha_composite(base, sparks)
    draw = ImageDraw.Draw(base)

    # Combo-hit effects (floating text near clipper)
    font_big = load_font(56)
    text = "COMBO +3"
    draw.text((center_x + 40, center_y - 60), text, font=font_big, fill=(255, 240, 130), stroke_width=3, stroke_fill=(0, 0, 0))

    # Floating central arcade text: 'PERFECT FADE!'
    font_perfect = load_font(84)
    shadowed_text(draw, (W * 0.25, H * 0.14), "PERFECT FADE!", font_perfect, fill=(255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))

    # Time Limit bar top (blinking red)
    bar_w = int(W * 0.6)
    bar_h = 26
    bar_x = int((W - bar_w) / 2)
    bar_y = 20
    draw.rectangle((bar_x - 4, bar_y - 4, bar_x + bar_w + 4, bar_y + bar_h + 4), fill=(0, 0, 0))
    # simulate blinking by drawing stripes
    for i in range(5):
        if i % 2 == 0:
            draw.rectangle((bar_x + i * (bar_w // 5), bar_y, bar_x + (i + 1) * (bar_w // 5) - 2, bar_y + bar_h), fill=(220, 40, 50))
    # text inside the bar
    font_small = load_font(22)
    draw.text((bar_x + 8, bar_y + 2), "Time Limit", font=font_small, fill=(255, 255, 255))

    # Vertical precision meter at right
    meter_w = 36
    meter_h = int(H * 0.52)
    meter_x = W - 72
    meter_y = int(H * 0.2)
    # outer
    draw.rectangle((meter_x - 4, meter_y - 4, meter_x + meter_w + 4, meter_y + meter_h + 4), fill=(0, 0, 0))
    # gradient meter fill (green -> yellow -> red)
    for i in range(meter_h):
        t = i / max(1, meter_h)
        if t > 0.7:
            col = (220, 80, 60)
        elif t > 0.4:
            col = (240, 200, 60)
        else:
            col = (60, 200, 140)
        draw.line((meter_x, meter_y + meter_h - i, meter_x + meter_w, meter_y + meter_h - i), fill=col)
    # marker
    marker_y = meter_y + int(meter_h * 0.35)
    draw.rectangle((meter_x - 6, marker_y - 4, meter_x + meter_w + 6, marker_y + 4), fill=(255, 255, 255))

    # Depth overlay vignette
    vignette = Image.new("L", (W, H), 0)
    vn_draw = ImageDraw.Draw(vignette)
    for i in range(max(W, H) // 2):
        alpha = int(255 * (1 - (i / (max(W, H) / 2))))
        vn_draw.ellipse((-i, -i, W + i, H + i), outline=alpha)
    base.putalpha(255)
    base = Image.composite(base, Image.new("RGBA", base.size, (0, 0, 0, 255)), vignette)

    base.save(path)
    print(f"Saved {path}")


# Helper to draw a cartoon fighter character blocky
@dataclass
class FighterSpec:
    x: int
    y: int
    scale: float
    color: Tuple[int, int, int]
    head_color: Tuple[int, int, int]
    face_features: str  # small descriptor to tweak
    direction: int = 1  # 1 right-facing, -1 left-facing


def draw_fighter(img: Image.Image, spec: FighterSpec):
    draw = ImageDraw.Draw(img)
    s = spec.scale
    x = spec.x
    y = spec.y
    # torso
    torso_w = int(90 * s)
    torso_h = int(120 * s)
    torso_box = (x - torso_w // 2, y - torso_h, x + torso_w // 2, y)
    draw.rectangle((torso_box[0] - 8, torso_box[1] - 8, torso_box[2] + 8, torso_box[3] + 8), fill=(0, 0, 0))
    draw.rectangle(torso_box, fill=spec.color)
    # head
    head_r = int(36 * s)
    hx = x + spec.direction * int(18 * s)
    hy = y - torso_h - head_r + 10
    draw.ellipse((hx - head_r - 6, hy - head_r - 6, hx + head_r + 6, hy + head_r + 6), fill=(0, 0, 0))
    draw.ellipse((hx - head_r, hy - head_r, hx + head_r, hy + head_r), fill=spec.head_color)
    # simple face: eyes
    eye_offset_x = int(12 * s) * spec.direction
    draw.ellipse((hx - 8 + eye_offset_x, hy - 6, hx - 2 + eye_offset_x, hy), fill=(0, 0, 0))
    draw.ellipse((hx + 2 + eye_offset_x, hy - 6, hx + 8 + eye_offset_x, hy), fill=(0, 0, 0))
    # mouth or mustache
    if "mustache" in spec.face_features:
        draw.line((hx - 10, hy + 10, hx + 10, hy + 10), fill=(60, 40, 20), width=max(2, int(3 * s)))
    # arms
    arm_l = [(torso_box[0], y - torso_h + 20), (torso_box[0] - int(40 * s), y - int(10 * s)), (torso_box[0], y - int(10 * s))]
    arm_r = [(torso_box[2], y - torso_h + 20), (torso_box[2] + int(40 * s) * spec.direction, y - int(10 * s)), (torso_box[2], y - int(10 * s))]
    draw.polygon(arm_l, fill=spec.head_color)
    draw.polygon(arm_r, fill=spec.head_color)
    # hands: add scissors or fists depending on feature
    if "scissors" in spec.face_features:
        # draw simple scissors in right hand
        hx_hand = arm_r[1][0]
        hy_hand = arm_r[1][1]
        draw.line((hx_hand, hy_hand, hx_hand + 30 * spec.direction, hy_hand - 10), fill=(180, 180, 200), width=6)
        draw.ellipse((hx_hand + 30 * spec.direction - 8, hy_hand - 16, hx_hand + 30 * spec.direction + 8, hy_hand), fill=(200, 200, 200))
    if "fist" in spec.face_features:
        fhx = arm_l[1][0]
        fhy = arm_l[1][1]
        draw.ellipse((fhx - 12, fhy - 12, fhx + 12, fhy + 12), fill=(60, 40, 20))


def draw_street_brawl(path: str):
    W, H = WIDTH, HEIGHT
    img = Image.new("RGBA", (W, H), (8, 8, 12, 255))
    draw = ImageDraw.Draw(img)

    # Background dark barbershop with neon sign
    floor_y = int(H * 0.7)
    draw.rectangle((0, floor_y, W, H), fill=(30, 20, 14))
    # chairs silhouette
    for i in range(3):
        cx = 160 + i * 320
        draw.rectangle((cx - 60, floor_y - 120, cx + 60, floor_y - 40), fill=(20, 20, 20))
        draw.ellipse((cx - 70, floor_y - 40, cx + 70, floor_y - 10), fill=(14, 10, 8))
    # neon sign
    neon_text = "IT'S A CUT-THROAT BUSINESS"
    font_neon = load_font(28)
    nx = int(W * 0.15)
    ny = int(H * 0.12)
    # neon glow layers
    for glow in range(8, 0, -2):
        draw.text((nx, ny), neon_text, font=font_neon, fill=(255, 50, 50, max(20, 255 - glow * 20)))
    draw.text((nx, ny), neon_text, font=font_neon, fill=(255, 120, 120))

    # Fighters
    left_spec = FighterSpec(x=int(W * 0.28), y=floor_y - 20, scale=1.05, color=(150, 40, 30), head_color=(240, 200, 160), face_features="fist beard", direction=1)
    right_spec = FighterSpec(x=int(W * 0.72), y=floor_y - 20, scale=1.0, color=(40, 90, 140), head_color=(240, 220, 180), face_features="mustache scissors", direction=-1)
    draw_fighter(img, left_spec)
    draw_fighter(img, right_spec)

    # Action effects: left super move - glowing fist + shaving foam shockwave
    # glowing fist
    gf_center = (left_spec.x + 30, left_spec.y - 70)
    gf = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gf_draw = ImageDraw.Draw(gf)
    for r in range(60, 8, -6):
        alpha = int(40 + (60 - r) * 3)
        col = (255, 240, 160, max(0, alpha))
        gf_draw.ellipse((gf_center[0] - r, gf_center[1] - r, gf_center[0] + r, gf_center[1] + r), outline=col)
    # shockwave of foam (white swirls)
    for i in range(6):
        rx = 120 + i * 40
        gf_draw.arc((gf_center[0] - rx, gf_center[1] - rx, gf_center[0] + rx, gf_center[1] + rx), start=220, end=320, fill=(230, 240, 250, 200), width=8)
    gf = gf.filter(ImageFilter.GaussianBlur(radius=2))
    img = Image.alpha_composite(img, gf)
    draw = ImageDraw.Draw(img)

    # Right player dodge pose highlight (motion lines)
    for i in range(5):
        draw.line((right_spec.x + 20, right_spec.y - 120 - i * 6, right_spec.x + 80, right_spec.y - 60 - i * 6), fill=(200, 220, 255, 180), width=3)

    # UI: health bars
    bar_w = 420
    bar_h = 22
    p1_x = 60
    p2_x = W - 60 - bar_w
    ui_y = 18
    # P1
    draw.rectangle((p1_x - 6, ui_y - 6, p1_x + bar_w + 6, ui_y + bar_h + 6), fill=(0, 0, 0))
    draw.rectangle((p1_x, ui_y, p1_x + int(bar_w * 0.72), ui_y + bar_h), fill=(240, 220, 60))
    # portrait simple
    draw.ellipse((p1_x - 56, ui_y - 10, p1_x - 8, ui_y + 34), fill=(200, 180, 140))
    # P2
    draw.rectangle((p2_x - 6, ui_y - 6, p2_x + bar_w + 6, ui_y + bar_h + 6), fill=(0, 0, 0))
    draw.rectangle((p2_x + (bar_w - int(bar_w * 0.46)), ui_y, p2_x + bar_w, ui_y + bar_h), fill=(80, 240, 140))
    draw.ellipse((p2_x + bar_w + 8, ui_y - 10, p2_x + bar_w + 56, ui_y + 34), fill=(220, 200, 160))

    # Timer in center
    font_timer = load_font(36)
    shadowed_text(draw, ((W - 40) // 2, ui_y - 4), "99", font_timer, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))

    # Super meter at bottom center
    sm_w = 500
    sm_h = 18
    sm_x = (W - sm_w) // 2
    sm_y = H - 50
    draw.rectangle((sm_x - 6, sm_y - 6, sm_x + sm_w + 6, sm_y + sm_h + 6), fill=(0, 0, 0))
    # full glowing
    for i in range(8):
        alpha = max(0, 220 - i * 24)
        draw.rectangle((sm_x + i * 6, sm_y, sm_x + sm_w - i * 6, sm_y + sm_h), fill=(40 + i * 20, 160 + i * 10, 255, alpha))
    # label
    font_small = load_font(20)
    draw.text((sm_x + sm_w + 12, sm_y - 2), "SUPER", font=font_small, fill=(255, 255, 255))

    # Overall retro halftone/scanline effect
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(0, H, 3):
        od.line((0, y, W, y), fill=(0, 0, 0, 20))
    img = Image.alpha_composite(img, overlay)

    img.save(path)
    print(f"Saved {path}")


def draw_menu(path: str):
    W, H = WIDTH, HEIGHT
    img = Image.new("RGBA", (W, H), (18, 18, 20, 255))
    draw = ImageDraw.Draw(img)

    # Split layout
    mid = W // 2
    # left panel (Precision Cut)
    left_box = (0, 0, mid, H)
    right_box = (mid, 0, W, H)
    draw.rectangle(left_box, fill=(40, 45, 50))
    draw.rectangle(right_box, fill=(28, 26, 28))

    # Icons and titles
    font_title = load_font(42)
    # Left icon: crossed golden scissor and clipper
    lx = mid // 2
    ly = int(H * 0.2)
    # icons background circle
    draw.ellipse((lx - 90, ly - 90, lx + 90, ly + 90), fill=(60, 60, 70))
    # scissor (simple)
    draw.line((lx - 30, ly - 10, lx + 30, ly + 10), fill=(255, 215, 80), width=10)
    draw.ellipse((lx - 44, ly - 26, lx - 20, ly - 2), fill=(255, 215, 80))
    draw.ellipse((lx + 20, ly + 2, lx + 44, ly + 26), fill=(255, 215, 80))
    # clipper (gold bar)
    draw.rectangle((lx - 10, ly - 60, lx + 60, ly - 30), fill=(220, 170, 70))
    # label
    shadowed_text(draw, (lx - 120, ly + 110), "PRECISION CUT", font_title, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))

    # Right icon: flaming fist
    rx = mid + (mid // 2)
    ry = int(H * 0.2)
    draw.ellipse((rx - 90, ry - 90, rx + 90, ry + 90), fill=(50, 30, 30))
    # fist
    draw.rectangle((rx - 30, ry - 20, rx + 30, ry + 20), fill=(180, 50, 40))
    # flame effect
    for i in range(5):
        draw.polygon([(rx + 20 - i * 8, ry - 60 + i * 12), (rx + 50 - i * 10, ry - 20 + i * 6), (rx + 10 - i * 6, ry - 10 + i * 8)], fill=(255, 80 + i * 20, 30))
    shadowed_text(draw, (rx - 100, ry + 110), "STREET BRAWL", font_title, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))

    # Character concept portraits - 4 staff on bottom center
    portraits_y = int(H * 0.54)
    spacing = 120
    start_x = mid - 1.5 * spacing
    specs = [
        ("The Tank", (200, 140, 100)),
        ("The All-rounder", (160, 160, 220)),
        ("The Brawler", (200, 120, 120)),
        ("The Technicus", (140, 200, 150)),
    ]
    font_name = load_font(20)
    for i, (name, col) in enumerate(specs):
        cx = int(start_x + i * spacing)
        cy = portraits_y
        # portrait card background
        draw.rectangle((cx - 56, cy - 86, cx + 56, cy + 86), fill=(20, 20, 20))
        # head circle with outline
        draw.ellipse((cx - 40, cy - 70, cx + 40, cy - 10), fill=col)
        draw.rectangle((cx - 34, cy - 15, cx + 34, cy + 48), fill=(60, 60, 60))
        shadowed_text(draw, (cx - 40, cy + 52), name, font_name, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))

    # Menu selection hints
    font_hint = load_font(18)
    draw.text((60, H - 40), "Press [Enter] to select", font=font_hint, fill=(200, 200, 200))
    draw.text((W - 260, H - 40), "Use ← → to switch", font=font_hint, fill=(200, 200, 200))

    # Center title top
    big_title = load_font(56)
    shadowed_text(draw, (W * 0.25 - 50, 24), "BARBER BRAWL ARCADE", big_title, fill=(255, 230, 200), stroke_width=6, stroke_fill=(30, 10, 10))

    img.save(path)
    print(f"Saved {path}")


def main():
    ensure_output_dir()
    draw_first_person_precision_cut(os.path.join(OUTPUT_DIR, "gameplay1.png"))
    draw_street_brawl(os.path.join(OUTPUT_DIR, "gameplay2.png"))
    draw_menu(os.path.join(OUTPUT_DIR, "menu.png"))


if __name__ == "__main__":
    main()
