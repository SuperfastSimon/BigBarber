from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import math
import random
import os

# Barber Arcade Mockup Generator
# Generates 3 images (Precision Cut screenshot, Street Brawl screenshot, Split-screen Menu)
# Requires: pillow
# Usage: python barber_arcade_mockups.py
# Outputs PNG files in the current directory.

CANVAS_W = 1920
CANVAS_H = 1080

# Utility: load a reasonably arcade-ish font if available, otherwise use default
def load_font(size):
    candidates = [
        "/usr/share/fonts/truetype/arcadeclassic/ArcadeClassic.ttf",
        "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf",
        "/Library/Fonts/Arial.ttf",
        "C:\\Windows\\Fonts\\Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

# Draw thick-outlined text by rendering multiple offsets
def draw_stroked_text(draw, position, text, font, fill, stroke_fill, stroke_width):
    x, y = position
    # Draw stroke by drawing text shifted in a grid
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx * dx + dy * dy <= stroke_width * stroke_width:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_fill)
    draw.text(position, text, font=font, fill=fill)

# Glow: create blurred colored blob
def draw_glow(base, center, radius, color, intensity=1.0):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    x, y = center
    # Draw multiple concentric circles to get smoother blur
    for r in range(radius, 0, -int(radius / 6) or -1):
        alpha = int(255 * (r / radius) * 0.18 * intensity)
        ld.ellipse((x - r, y - r, x + r, y + r), fill=(color[0], color[1], color[2], alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(radius / 2))
    base.alpha_composite(layer)

# Simple cel-shaded outline for polygon
def draw_cell_polygon(draw, xy, fill, outline_width=6, outline=(0,0,0)):
    # Draw main polygon
    draw.polygon(xy, fill=fill)
    # Draw thicker outline by drawing scaled strokes around polygon edges
    # We approximate by stroking lines between vertices
    n = len(xy)
    for i in range(n):
        x1, y1 = xy[i]
        x2, y2 = xy[(i + 1) % n]
        draw.line((x1, y1, x2, y2), fill=outline, width=outline_width)

# Save helper
def save(img, name):
    img.save(name)
    print(f"Saved: {name}")

# Background: dreamy blurred barbershop
def draw_barbershop_background(size, neon_text=None):
    w, h = size
    bg = Image.new("RGBA", size, (30, 30, 30, 255))
    draw = ImageDraw.Draw(bg)
    # Wood floor gradient
    for i in range(h):
        t = i / h
        r = int(20 + 40 * t)
        g = int(12 + 20 * t)
        b = int(10 + 20 * t)
        draw.line((0, i, w, i), fill=(r, g, b))
    # Put blurry shelf shapes to represent products & mirrors
    shelf = Image.new("RGBA", size, (0,0,0,0))
    sd = ImageDraw.Draw(shelf)
    # mirrors: rectangles with highlight
    for i, x in enumerate([w*0.2, w*0.5, w*0.8]):
        rx = int(x - 160)
        ry = int(h * 0.15)
        rw = 320
        rh = 260
        sd.rectangle((rx, ry, rx + rw, ry + rh), fill=(60, 80, 100, 180), outline=(20,20,20,200))
        # products: small colored rectangles
        for j in range(5):
            px = rx + 20 + j * 55
            py = ry + rh + 18
            sd.rectangle((px, py, px + 30, py + 60), fill=(random.randint(80,230), random.randint(60,200), random.randint(60,230), 255))
    shelf = shelf.filter(ImageFilter.GaussianBlur(22))
    bg.alpha_composite(shelf)
    # Neon sign
    if neon_text:
        neon = Image.new("RGBA", size, (0,0,0,0))
        nd = ImageDraw.Draw(neon)
        font = load_font(56)
        text = neon_text
        tw, th = nd.textsize(text, font=font)
        nd.text((w - tw - 80, h * 0.1), text, font=font, fill=(255, 40, 40, 255))
        neon = neon.filter(ImageFilter.GaussianBlur(4))
        bg.alpha_composite(neon)
    # Final blur to create depth
    bg = bg.filter(ImageFilter.GaussianBlur(2))
    return bg

# Create precision cut screenshot
def create_precision_cut():
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (10, 10, 10, 255))
    bg = draw_barbershop_background((CANVAS_W, CANVAS_H), neon_text="IT'S A CUT-THROAT BUSINESS")
    img.alpha_composite(bg)
    draw = ImageDraw.Draw(img)

    # Foreground: customer head (side), simple cel-shaded sphere-ish
    cx, cy = int(CANVAS_W * 0.45), int(CANVAS_H * 0.55)
    head_r = 200
    # base head
    draw.ellipse((cx - head_r, cy - head_r, cx + head_r, cy + head_r), fill=(220, 190, 160))
    # hair area (top) to show fade
    draw.pieslice((cx - head_r, cy - head_r, cx + head_r, cy + head_r), -140, -40, fill=(18, 18, 18))
    # cel-shade highlight
    draw.ellipse((cx - 60, cy - 120, cx + 40, cy - 60), fill=(255, 230, 180))
    # outline
    draw.ellipse((cx - head_r, cy - head_r, cx + head_r, cy + head_r), outline=(0,0,0), width=8)

    # Player hand holding golden clippers (first-person POV) - stylized polygon
    hand_x = int(CANVAS_W * 0.65)
    hand_y = int(CANVAS_H * 0.6)
    # glove
    draw.polygon([(hand_x - 60, hand_y + 10), (hand_x + 40, hand_y + 0), (hand_x + 20, hand_y + 80), (hand_x - 80, hand_y + 70)], fill=(245, 210, 175))
    draw.line([(hand_x - 60, hand_y + 10), (hand_x + 40, hand_y)], fill=(0,0,0), width=6)
    # golden clippers body
    clip_x = hand_x + 40
    clip_y = hand_y - 20
    body = [(clip_x, clip_y), (clip_x + 160, clip_y - 20), (clip_x + 160, clip_y + 30), (clip_x, clip_y + 40)]
    draw_cell_polygon(draw, body, fill=(220, 180, 40), outline_width=8, outline=(20,10,0))
    # blades
    blade = [(clip_x + 160, clip_y - 10), (clip_x + 210, clip_y - 20), (clip_x + 215, clip_y + 10), (clip_x + 160, clip_y + 20)]
    draw_cell_polygon(draw, blade, fill=(200, 220, 255), outline_width=6, outline=(0,0,0))

    # Electric sparks (electric blue) near blades
    sparks_layer = Image.new("RGBA", img.size, (0,0,0,0))
    sd = ImageDraw.Draw(sparks_layer)
    for i in range(28):
        angle = random.uniform(-1.2, -0.3)
        length = random.uniform(30, 140)
        sx = clip_x + 200 + random.randint(-20, 40)
        sy = clip_y + random.randint(-10, 20)
        ex = int(sx + math.cos(angle) * length)
        ey = int(sy + math.sin(angle) * length)
        sd.line((sx, sy, ex, ey), fill=(80, 230, 255, 255), width=random.randint(2,5))
        # small sparks
        for t in range(3):
            px = ex + random.randint(-10, 10)
            py = ey + random.randint(-10, 10)
            sd.ellipse((px-3, py-3, px+3, py+3), fill=(180, 255, 255, 220))
    sparks_layer = sparks_layer.filter(ImageFilter.GaussianBlur(1))
    img.alpha_composite(sparks_layer)

    # Combo hit effect text floating from clippers
    font_big = load_font(120)
    combo_text = "PERFECT FADE!"
    tw, th = draw.textsize(combo_text, font=font_big)
    # big arcade text in center slightly above
    center_x = CANVAS_W // 2
    center_y = CANVAS_H // 2 - 80
    # draw stroked
    draw_stroked_text(draw, (center_x - tw // 2, center_y - th // 2), combo_text, font_big, fill=(255, 240, 80), stroke_fill=(0, 0, 0), stroke_width=6)

    # UI Top: Time Limit bar that is blinking red
    bar_w = int(CANVAS_W * 0.6)
    bar_h = 24
    bx = (CANVAS_W - bar_w) // 2
    by = 40
    # animated blink simulated by stripes
    for i in range(20):
        stripe_x = bx + int((i / 20) * bar_w)
        color = (255, 40, 40) if i % 2 == 0 else (190, 20, 20)
        draw.rectangle((stripe_x, by, stripe_x + int(bar_w/20), by + bar_h), fill=color)
    draw.rectangle((bx, by, bx + bar_w, by + bar_h), outline=(0,0,0), width=4)
    draw.text((bx + 8, by - 2), "TIME LIMIT", font=load_font(20), fill=(255,255,255))

    # Right side vertical precision meter
    meter_h = 380
    mx = CANVAS_W - 140
    my = CANVAS_H // 2 - meter_h // 2
    draw.rectangle((mx, my, mx + 36, my + meter_h), fill=(30, 30, 30))
    # meter levels with gradient and marker
    for i in range(10):
        y0 = my + int((i / 10) * meter_h)
        y1 = my + int(((i + 1) / 10) * meter_h) - 2
        col = (20, 220 - i*16, 140 + i*8)
        draw.rectangle((mx + 4, y0, mx + 32, y1), fill=col)
    # marker showing precision (e.g., near perfect)
    marker_y = my + int(meter_h * 0.18)
    draw.polygon([(mx - 10, marker_y), (mx + 46, marker_y - 12), (mx + 46, marker_y + 12)], fill=(255, 240, 80))
    draw.line((mx - 14, marker_y, mx + 52, marker_y), fill=(0,0,0), width=3)
    draw.text((mx - 10, my + meter_h + 10), "PRECISION", font=load_font(18), fill=(255,255,255))

    # Depth of field blur around background to emphasize foreground: apply vignette
    vignette = Image.new('L', img.size, 0)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse((-CANVAS_W*0.1, -CANVAS_H*0.15, CANVAS_W*1.1, CANVAS_H*1.15), fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(120))
    img.putalpha(vignette)
    # Convert back to RGB with black background
    final = Image.new('RGB', img.size, (10, 10, 10))
    final.paste(img, mask=img.split()[3])
    save(final, 'precision_cut.png')

# Create street brawl screenshot
def create_street_brawl():
    img = Image.new('RGB', (CANVAS_W, CANVAS_H), (6, 6, 6))
    draw = ImageDraw.Draw(img)

    # background: darker shop interior with neon sign
    bg = draw_barbershop_background((CANVAS_W, CANVAS_H), neon_text="IT'S A CUT-THROAT BUSINESS")
    img.paste(bg, (0,0), bg)

    # ground/platform
    draw.rectangle((0, CANVAS_H - 160, CANVAS_W, CANVAS_H), fill=(40, 24, 18))
    # midline to suggest arena
    mid_y = CANVAS_H - 200
    draw.line((0, mid_y, CANVAS_W, mid_y), fill=(80, 50, 45), width=6)

    # Left character (Tank) - stylized sprite
    tx = int(CANVAS_W * 0.25)
    ty = mid_y - 10
    # body
    draw.rectangle((tx - 60, ty - 120, tx + 60, ty + 20), fill=(200, 140, 110))
    # tattoos & beard
    draw.ellipse((tx - 55, ty - 140, tx + 55, ty - 80), fill=(56, 32, 24))
    draw.rectangle((tx - 20, ty - 100, tx + 20, ty - 50), fill=(40, 40, 40))
    # arms - left arm throwing super move (glowing fist)
    draw.rectangle((tx + 60, ty - 90, tx + 150, ty - 40), fill=(200, 140, 110))
    draw.ellipse((tx + 140, ty - 120, tx + 200, ty - 60), fill=(255, 200, 160))
    draw.line((tx + 160, ty - 80, tx + 420, ty - 100), fill=(255, 255, 255), width=4)
    # glowing fist
    draw.ellipse((tx + 360, ty - 140, tx + 420, ty - 80), fill=(255, 110, 40))
    draw_glow(img, (tx + 390, ty - 110), 70, (255, 140, 50), intensity=1.2)
    # foam shockwave
    sw_center = (tx + 420, ty - 60)
    for r in range(3):
        radius = 80 + r * 40
        bbox = [sw_center[0] - radius, sw_center[1] - radius, sw_center[0] + radius, sw_center[1] + radius]
        draw.arc(bbox, start=200 - r*10, end=400 + r*10, fill=(255, 245, 220), width=18 - r*5)
    # foam particles
    for i in range(40):
        px = sw_center[0] + random.randint(-220, 220)
        py = sw_center[1] + random.randint(-80, 120)
        r = random.randint(3, 9)
        draw.ellipse((px-r, py-r, px+r, py+r), fill=(245, 250, 255))

    # Right character (Technician) - dodging
    rx = int(CANVAS_W * 0.72)
    ry = mid_y - 10
    draw.rectangle((rx - 50, ry - 120, rx + 50, ry + 20), fill=(160, 180, 200))
    # head with glasses & mustache
    draw.ellipse((rx - 36, ry - 160, rx + 36, ry - 100), fill=(240, 210, 180))
    draw.rectangle((rx - 28, ry - 145, rx + 28, ry - 130), fill=(25, 25, 25))  # glasses band
    draw.line((rx - 18, ry - 120, rx + 18, ry - 120), fill=(60, 40, 30), width=6)  # moustache
    # scissors in hand, quick pose
    sc_x1 = rx - 90
    sc_y1 = ry - 90
    draw.line((sc_x1, sc_y1, sc_x1 - 40, sc_y1 - 100), fill=(200,200,255), width=6)
    draw.ellipse((sc_x1 - 46, sc_y1 - 106, sc_x1 - 34, sc_y1 - 94), outline=(30,30,30), width=6)

    # Dramatic lighting: electric blue rim light around technician
    draw_glow(img, (rx, ry - 80), 90, (60, 160, 255), intensity=0.9)

    # UI: top health bars and portraits
    # Left health
    pw = 420
    ph = 34
    left_x = 120
    top_y = 40
    draw.rectangle((left_x - 6, top_y - 6, left_x + pw + 6, top_y + ph + 6), fill=(10,10,10))
    draw.rectangle((left_x, top_y, left_x + pw, top_y + ph), fill=(240, 220, 60))
    # Right health
    right_x = CANVAS_W - 120 - pw
    draw.rectangle((right_x - 6, top_y - 6, right_x + pw + 6, top_y + ph + 6), fill=(10,10,10))
    draw.rectangle((right_x, top_y, right_x + pw, top_y + ph), fill=(60, 220, 120))
    # portraits (simple circles)
    draw.ellipse((left_x - 80, top_y - 6, left_x - 8, top_y + ph + 6), fill=(200, 150, 120))
    draw.ellipse((right_x + pw + 8, top_y - 6, right_x + pw + 80, top_y + ph + 6), fill=(160, 180, 200))

    # Timer center
    timer_font = load_font(64)
    timer_text = "99"
    tw, th = draw.textsize(timer_text, font=timer_font)
    draw_stroked_text(draw, (CANVAS_W//2 - tw//2, top_y - 6), timer_text, timer_font, fill=(255,255,255), stroke_fill=(0,0,0), stroke_width=4)

    # Super meter bottom (full and glowing)
    sm_w = 600
    sm_h = 28
    sm_x = (CANVAS_W - sm_w) // 2
    sm_y = CANVAS_H - 80
    draw.rectangle((sm_x - 6, sm_y - 6, sm_x + sm_w + 6, sm_y + sm_h + 6), fill=(10,10,10))
    # meter fill
    for i in range(60):
        x0 = sm_x + int(i * (sm_w/60))
        x1 = sm_x + int((i+1) * (sm_w/60)) - 2
        color = (255, 80 + int(175 * (i/60)), 60) if i > 40 else (30, 130, 255)
        draw.rectangle((x0, sm_y, x1, sm_y + sm_h), fill=color)
    draw_glow(img, (sm_x + sm_w//2, sm_y + sm_h//2), 60, (255, 180, 60), intensity=0.8)
    draw.text((sm_x - 60, sm_y - 2), "SUPER", font=load_font(22), fill=(255,255,255))

    # Retro CRT/scanline effect to sell 90s arcade
    scan = Image.new('RGBA', img.size, (0,0,0,0))
    sd = ImageDraw.Draw(scan)
    for y in range(0, CANVAS_H, 3):
        sd.line((0, y, CANVAS_W, y), fill=(0,0,0,20))
    img = Image.alpha_composite(img.convert('RGBA'), scan)
    final = img.convert('RGB')
    save(final, 'street_brawl.png')

# Create split-screen menu and character concept art
def create_menu_and_concepts():
    img = Image.new('RGB', (CANVAS_W, CANVAS_H), (12,12,12))
    draw = ImageDraw.Draw(img)

    # Background: industrial barbershop with neon sign center
    bg = draw_barbershop_background((CANVAS_W, CANVAS_H), neon_text="IT'S A CUT-THROAT BUSINESS")
    img.paste(bg, (0,0), bg)

    # Split down the middle
    mid = CANVAS_W // 2
    # Left panel (Precision Cut)
    draw.rectangle((0, 0, mid, CANVAS_H), fill=(18, 18, 30, 200))
    draw.rectangle((mid, 0, CANVAS_W, CANVAS_H), fill=(12, 12, 12, 180))

    # Icons and titles
    icon_font = load_font(42)
    title_font = load_font(68)
    # Left icon: crossed golden scissors and clippers
    lx = mid // 2
    ly = 220
    # scissor
    draw.line((lx - 90, ly - 10, lx - 30, ly + 40), fill=(240,220,80), width=12)
    draw.ellipse((lx - 112, ly - 36, lx - 88, ly - 12), outline=(20,20,20), width=6)
    # clipper
    draw.rectangle((lx + 5, ly - 20, lx + 110, ly + 10), fill=(220,180,40))
    draw.text((lx - 180, ly + 80), "PRECISION CUT", font=title_font, fill=(240,240,240))

    # Right icon: flaming fist
    rx = mid + (mid // 2)
    ry = 220
    # fist
    draw.rectangle((rx - 36, ry - 10, rx + 36, ry + 50), fill=(240, 140, 100))
    # flames stylized
    for i in range(6):
        fx = rx + random.randint(-40, 40)
        fy = ry - 80 - i * 16
        draw.polygon([(fx, fy), (fx + 24, fy + 40), (fx - 24, fy + 40)], fill=(255, 80 + i*20, 40))
    draw.text((mid + 60, ry + 80), "STREET BRAWL", font=title_font, fill=(240,240,240))

    # Four character portraits in center bottom row
    roster_y = CANVAS_H - 380
    spacing = CANVAS_W // 5
    names = ["THE TANK", "THE ALL-ROUNDER", "THE BRAWLER", "THE TECHNICIAN"]
    for i in range(4):
        cx = spacing * (i + 1)
        cy = roster_y
        # portrait circle
        draw.ellipse((cx - 90, cy - 120, cx + 90, cy + 60), fill=(40 + i*40, 40 + i*20, 70 + i*30))
        # stylized details for each
        if i == 0:  # Tank
            draw.line((cx - 30, cy - 40, cx + 30, cy - 40), fill=(0,0,0), width=8)
            draw.text((cx - 60, cy + 20), names[i], font=load_font(22), fill=(255,255,255))
        if i == 1:  # All-rounder
            draw.line((cx - 20, cy - 60, cx + 20, cy - 60), fill=(0,0,0), width=6)
            draw.text((cx - 90, cy + 20), names[i], font=load_font(22), fill=(255,255,255))
        if i == 2:  # Brawler
            draw.line((cx - 40, cy - 30, cx + 40, cy - 30), fill=(0,0,0), width=8)
            draw.text((cx - 80, cy + 20), names[i], font=load_font(22), fill=(255,255,255))
        if i == 3:  # Technician
            draw.line((cx - 30, cy - 50, cx + 30, cy - 50), fill=(0,0,0), width=5)
            # add glasses
            draw.rectangle((cx - 30, cy - 60, cx - 6, cy - 46), fill=(20,20,20))
            draw.rectangle((cx + 6, cy - 60, cx + 30, cy - 46), fill=(20,20,20))
            draw.text((cx - 110, cy + 20), names[i], font=load_font(22), fill=(255,255,255))

    # Ready-to-Fight poses silhouettes above portraits
    # We'll draw 4 big silhouette-like poses top-middle
    poses_y = 420
    for i in range(4):
        px = spacing * (i + 1)
        py = poses_y
        # big black outline body
        draw.polygon([(px - 60, py + 100), (px - 30, py - 10), (px + 30, py - 10), (px + 60, py + 100)], fill=(20,20,20))
        # arms variances
        if i == 0:
            draw.polygon([(px - 120, py + 40), (px - 60, py + 20), (px - 40, py + 60), (px - 120, py + 90)], fill=(20,20,20))
        if i == 1:
            draw.polygon([(px - 80, py + 40), (px - 20, py - 20), (px + 20, py - 20), (px + 80, py + 40)], fill=(20,20,20))
        if i == 2:
            draw.polygon([(px - 70, py + 30), (px - 10, py + 30), (px - 10, py + 100), (px - 70, py + 100)], fill=(20,20,20))
        if i == 3:
            draw.polygon([(px + 60, py - 10), (px + 120, py - 60), (px + 140, py - 20), (px + 80, py + 30)], fill=(20,20,20))

    # Lower UI: option boxes for menu selection
    draw.rectangle((mid//2 - 200, CANVAS_H - 140, mid//2 + 200, CANVAS_H - 40), outline=(255,255,255), width=4, fill=(30,30,40))
    draw_stroked_text(draw, (mid//2 - 140, CANVAS_H - 130), "PRECISION CUT", load_font(28), fill=(255,240,80), stroke_fill=(0,0,0), stroke_width=2)
    draw.rectangle((mid + mid//2 - 200, CANVAS_H - 140, mid + mid//2 + 200, CANVAS_H - 40), outline=(255,255,255), width=4, fill=(30,30,40))
    draw_stroked_text(draw, (mid + mid//2 - 120, CANVAS_H - 130), "STREET BRAWL", load_font(28), fill=(255,120,120), stroke_fill=(0,0,0), stroke_width=2)

    save(img, 'split_menu_concepts.png')

if __name__ == '__main__':
    print('Generating mockups...')
    create_precision_cut()
    create_street_brawl()
    create_menu_and_concepts()
    print('Done. Generated: precision_cut.png, street_brawl.png, split_menu_concepts.png')
