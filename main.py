import sys
import math
import random
from dataclasses import dataclass
from typing import Tuple

import pygame

# Viral Barber Game - Prototype
# Two modes: PRECISION CUT (first-person barber arcade) and STREET BRAWL (2D fighter)
# Self-contained demo using Pygame only (no external assets).

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Viral Barber Game - Prototype")
CLOCK = pygame.time.Clock()

# Colors (vibrant + neon)
BLACK = (10, 10, 10)
WHITE = (245, 245, 245)
NEON_RED = (255, 42, 42)
ELECTRIC_BLUE = (66, 170, 255)
GOLD = (212, 175, 55)
WOOD = (95, 61, 35)
NEON_BG_ACCENT = (30, 30, 40)

FONT_BIG = pygame.font.SysFont("Arial", 56, bold=True)
FONT_MED = pygame.font.SysFont("Arial", 28, bold=True)
FONT_SMALL = pygame.font.SysFont("Arial", 18)

# Game States
STATE_MENU = "menu"
STATE_PRECISION = "precision"
STATE_BRAWL = "brawl"

# Utility

def draw_text_center(surf, text, font, color, pos):
    r = font.render(text, True, color)
    rect = r.get_rect(center=pos)
    surf.blit(r, rect)


def thick_outline_rect(surf, rect, color_fill, color_outline, thickness=4, radius=6):
    # draw outline then fill for pseudo-cel shading
    pygame.draw.rect(surf, color_outline, rect.inflate(thickness * 2, thickness * 2), border_radius=radius)
    pygame.draw.rect(surf, color_fill, rect, border_radius=radius)


@dataclass
class Spark:
    x: float
    y: float
    dx: float
    dy: float
    life: float

    def update(self, dt: float):
        self.x += self.dx * dt
        self.y += self.dy * dt
        self.life -= dt


class PrecisionCutMode:
    def __init__(self):
        self.time_limit = 12.0  # seconds
        self.time_left = self.time_limit
        self.combo = 0
        self.combo_timer = 0.0
        self.sparks: list[Spark] = []
        self.perfect_text_timer = 0.0
        # fake head and fade target
        self.head_center = (WIDTH * 0.6, HEIGHT * 0.45)
        self.head_radius = 120
        self.fade_x = self.head_center[0] - 70
        self.clip_y = self.head_center[1]
        self.perfection_window = 8.0  # pixels

    def reset(self):
        self.time_left = self.time_limit
        self.combo = 0
        self.combo_timer = 0.0
        self.sparks.clear()
        self.perfect_text_timer = 0.0

    def update(self, dt: float, mouse_pos: Tuple[int, int], mouse_down: bool):
        self.time_left = max(0.0, self.time_left - dt)

        # Move clipper with mouse vertically, limit bounds
        mx, my = mouse_pos
        self.clip_y = max(100, min(HEIGHT - 80, my))

        # If clicking near the fade x position and within perfect window, register precision
        if mouse_down:
            dist = abs(mx - self.fade_x) + abs(self.clip_y - (self.head_center[1] + 10))
            if dist < 80:  # general hit area
                # precision depends on vertical alignment
                vert_err = abs(self.clip_y - (self.head_center[1] + 10))
                if vert_err <= self.perfection_window:
                    self.combo += 1
                    self.combo_timer = 1.2
                    self.perfect_text_timer = 0.9
                    # spawn sparks
                    for _ in range(12):
                        ang = random.uniform(-math.pi / 2, math.pi / 2)
                        speed = random.uniform(120, 350)
                        self.sparks.append(Spark(self.fade_x, self.clip_y, math.cos(ang) * speed, math.sin(ang) * speed, random.uniform(0.4, 0.9)))
                else:
                    # smaller sparks for imperfect
                    self.combo = 0
                    for _ in range(4):
                        ang = random.uniform(-math.pi / 2, math.pi / 2)
                        speed = random.uniform(40, 140)
                        self.sparks.append(Spark(self.fade_x, self.clip_y, math.cos(ang) * speed, math.sin(ang) * speed, random.uniform(0.2, 0.6)))

        # update sparks
        for sp in list(self.sparks):
            sp.update(dt)
            sp.dy += 300 * dt  # gravity-ish
            if sp.life <= 0:
                self.sparks.remove(sp)

        # timers
        if self.combo_timer > 0:
            self.combo_timer -= dt
        else:
            self.combo = 0
        if self.perfect_text_timer > 0:
            self.perfect_text_timer -= dt

    def draw(self, surf: pygame.Surface):
        surf.fill(NEON_BG_ACCENT)

        # background: blurred barbershop (simple rectangles with low alpha)
        for i in range(6):
            rx = 80 + i * 180
            ry = 80
            w = 140
            h = 380
            pygame.draw.rect(surf, (20, 20, 20), (rx, ry, w, h), border_radius=10)
            # mirror shine
            pygame.draw.rect(surf, (40, 40, 40), (rx + 8, ry + 10, w - 16, 40), border_radius=8)

        # head (side view with shading)
        cx, cy = self.head_center
        pygame.draw.circle(surf, (60, 50, 40), (int(cx), int(cy)), self.head_radius + 6)  # outline
        pygame.draw.circle(surf, (232, 200, 170), (int(cx), int(cy)), self.head_radius)
        # hair top
        pygame.draw.arc(surf, (30, 30, 30), (cx - 110, cy - 110, 220, 160), math.radians(200), math.radians(340), 48)

        # fade target line (where clipper should be)
        pygame.draw.line(surf, (80, 80, 80), (self.fade_x, cy - 100), (self.fade_x, cy + 100), 4)

        # draw clipper (player hand holding golden clipper) - first-person
        hand_x = self.fade_x - 60
        hand_y = self.clip_y + 60
        # hand glove
        pygame.draw.ellipse(surf, (220, 180, 150), (hand_x - 12, hand_y - 18, 44, 36))
        # clipper body
        clip_rect = pygame.Rect(self.fade_x - 12, self.clip_y - 40, 90, 30)
        pygame.draw.rect(surf, GOLD, clip_rect, border_radius=6)
        pygame.draw.rect(surf, (80, 60, 30), clip_rect.inflate(-6, -6), border_radius=4)
        # blade
        pygame.draw.rect(surf, (220, 220, 235), (self.fade_x + 70, self.clip_y - 36, 28, 38), border_radius=4)

        # electric sparks
        for sp in self.sparks:
            alpha = max(0, min(255, int(255 * (sp.life / 1.0))))
            col = (*ELECTRIC_BLUE[:3], alpha)
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(s, col, (3, 3), 3)
            surf.blit(s, (int(sp.x), int(sp.y)))

        # combo / PERFECT FADE text
        if self.perfect_text_timer > 0:
            # show big floating text
            scale = 1.0 + 0.25 * math.sin(self.perfect_text_timer * 12)
            txt = FONT_BIG.render("PERFECT FADE!", True, ELECTRIC_BLUE)
            txt_rect = txt.get_rect(center=(cx, cy - 180))
            surf.blit(txt, txt_rect)

        if self.combo > 1 and self.combo_timer > 0:
            draw_text_center(surf, f"COMBO x{self.combo}", FONT_MED, (255, 230, 120), (cx, cy - 120))

        # UI: Time Limit bar at top
        bar_w = WIDTH * 0.8
        bar_h = 20
        bx = (WIDTH - bar_w) / 2
        by = 18
        frac = self.time_left / self.time_limit
        # background
        pygame.draw.rect(surf, (60, 10, 10), (bx - 4, by - 4, bar_w + 8, bar_h + 8), border_radius=8)
        # fill
        fill_w = int(bar_w * frac)
        # blinking red when low
        blink = (self.time_left < 4.0) and (pygame.time.get_ticks() % 600 < 300)
        fill_col = (220, 30, 30) if blink else (255, 80, 80)
        pygame.draw.rect(surf, fill_col, (bx, by, fill_w, bar_h), border_radius=6)
        pygame.draw.rect(surf, (120, 120, 120), (bx + fill_w, by, bar_w - fill_w, bar_h), border_radius=6)
        draw_text_center(surf, f"Time: {int(self.time_left)}", FONT_SMALL, WHITE, (WIDTH / 2, by + bar_h / 2))

        # Vertical precision meter at right
        meter_h = 300
        mx = WIDTH - 70
        my_top = (HEIGHT - meter_h) / 2
        pygame.draw.rect(surf, (40, 40, 40), (mx - 22, my_top - 6, 44, meter_h + 12), border_radius=10)
        # indicator
        rel = (self.clip_y - 100) / (HEIGHT - 180)
        ind_y = my_top + rel * meter_h
        pygame.draw.rect(surf, ELECTRIC_BLUE, (mx - 12, ind_y - 6, 24, 12), border_radius=6)
        draw_text_center(surf, "PRECISION", FONT_SMALL, WHITE, (mx, my_top - 20))

        # hint text
        draw_text_center(surf, "Click/hold near the fade to perform precise cuts", FONT_SMALL, WHITE, (WIDTH / 2, HEIGHT - 30))


class BrawlMode:
    def __init__(self):
        self.timer = 99
        self.left_hp = 100
        self.right_hp = 100
        self.super_full = True
        self.super_active = False
        self.super_timer = 0.0
        # positions
        self.left_pos = [220, HEIGHT - 220]
        self.right_pos = [WIDTH - 220, HEIGHT - 220]
        self.left_vel = [0, 0]
        self.right_vel = [0, 0]
        self.particles: list[Tuple[float, float, float, float, float]] = []  # x,y,dx,dy,life

    def reset(self):
        self.timer = 99
        self.left_hp = 100
        self.right_hp = 100
        self.super_full = True
        self.super_active = False
        self.super_timer = 0.0
        self.particles.clear()

    def update(self, dt: float, inputs: dict):
        # timer
        self.timer = max(0, self.timer - dt)

        # simple left player controls: A/D to move, W to jump
        if inputs.get("left_move"):
            self.left_pos[0] += -180 * dt
        if inputs.get("right_move"):
            self.left_pos[0] += 180 * dt
        # right player is AI-controlled simplistically
        # clamp positions
        self.left_pos[0] = max(120, min(WIDTH / 2 - 60, self.left_pos[0]))
        self.right_pos[0] = max(WIDTH / 2 + 60, min(WIDTH - 120, self.right_pos[0]))

        # Super move trigger
        if inputs.get("super") and self.super_full and not self.super_active:
            self.super_active = True
            self.super_timer = 0.7
            self.super_full = False
            # spawn fist particle effect
            for i in range(30):
                ang = random.uniform(-0.3, 0.3)
                spd = random.uniform(400, 700)
                self.particles.append([self.left_pos[0] + 60, self.left_pos[1] - 60, math.cos(ang) * spd, math.sin(ang) * spd, random.uniform(0.3, 0.9)])

        # update super
        if self.super_active:
            self.super_timer -= dt
            if self.super_timer <= 0:
                self.super_active = False
                # apply damage and foam shockwave to right
                self.right_hp = max(0, self.right_hp - 28)
                # spawn foam shockwave
                for i in range(40):
                    ang = random.uniform(-0.7, 0.7)
                    spd = random.uniform(100, 320)
                    self.particles.append([self.right_pos[0] - 40, self.right_pos[1] - 40, math.cos(ang) * spd, math.sin(ang) * spd, random.uniform(0.4, 1.1)])

        # update particles
        for p in list(self.particles):
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[4] -= dt
            p[3] += 300 * dt  # gravity
            if p[4] <= 0:
                self.particles.remove(p)

        # simple AI: when super occurs, attempt dodge
        if self.super_active and random.random() < 0.015:
            self.right_pos[0] += 100 * dt

    def draw(self, surf: pygame.Surface):
        surf.fill((18, 18, 18))

        # background: dark barbershop with neon sign
        pygame.draw.rect(surf, (22, 22, 22), (0, 0, WIDTH, HEIGHT))
        # neon sign
        sign_txt = FONT_MED.render("IT'S A CUT-THROAT BUSINESS", True, NEON_RED)
        sign_rect = sign_txt.get_rect(center=(WIDTH / 2, 80))
        # glow
        for i in range(6):
            alpha = max(0, 60 - i * 8)
            gsurf = pygame.Surface((sign_rect.width + 40, sign_rect.height + 20), pygame.SRCALPHA)
            gsurf.fill((*NEON_RED, alpha))
            surf.blit(gsurf, (sign_rect.x - 20 - i * 2, sign_rect.y - 10 - i * 2))
        surf.blit(sign_txt, sign_rect)

        # chairs silhouettes
        for i, x in enumerate(range(80, WIDTH, 220)):
            if 0 < x < WIDTH - 120:
                pygame.draw.rect(surf, (35, 25, 20), (x, HEIGHT - 200, 140, 80), border_radius=8)

        # draw fighters (hand-drawn sprite style with thick outlines)
        # Left: The Tank
        lx, ly = self.left_pos
        pygame.draw.rect(surf, (80, 35, 30), (lx - 48, ly - 100, 96, 120), border_radius=12)  # body
        pygame.draw.circle(surf, (220, 180, 160), (int(lx), int(ly - 120)), 30)  # head
        # beard/tattoos
        pygame.draw.circle(surf, (60, 30, 20), (int(lx), int(ly - 112)), 14)
        pygame.draw.rect(surf, (20, 20, 20), (lx - 40, ly + 10, 80, 8))

        # Right: The Technicus
        rx, ry = self.right_pos
        pygame.draw.rect(surf, (60, 70, 120), (rx - 42, ry - 100, 84, 110), border_radius=10)  # body
        pygame.draw.circle(surf, (240, 220, 200), (int(rx), int(ry - 120)), 26)  # head
        pygame.draw.rect(surf, (40, 40, 40), (rx + 18, ry - 60, 12, 4))  # glasses hint
        # shears in hand
        pygame.draw.polygon(surf, (200, 200, 220), [(rx + 36, ry - 40), (rx + 58, ry - 28), (rx + 34, ry - 16)])

        # draw particles (sparks & foam)
        for p in self.particles:
            life = p[4]
            size = max(2, int(8 * life))
            col = (255, 255, 255) if self.super_active else (200, 230, 255)
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*col, int(200 * max(0.2, life / 1.0))), (size, size), size)
            surf.blit(s, (p[0] - size, p[1] - size))

        # if super active, draw glowing fist animation
        if self.super_active:
            # draw a glowing fist near left moving right
            t = (0.7 - self.super_timer) / 0.7
            fx = self.left_pos[0] + 60 + 480 * t
            fy = self.left_pos[1] - 60
            pygame.draw.circle(surf, (255, 160, 40), (int(fx), int(fy)), int(48 * (1.0 + 0.2 * math.sin(t * 8))))
            draw_text_center(surf, "SUPER!", FONT_MED, (255, 220, 120), (fx, fy - 80))

        # UI: health bars
        # Left health
        pygame.draw.rect(surf, (30, 30, 30), (60, 30, 420, 28), border_radius=14)
        lw = int(400 * (self.left_hp / 100))
        pygame.draw.rect(surf, (255, 220, 70), (70, 36, lw, 18), border_radius=10)
        # portrait
        pygame.draw.circle(surf, (220, 180, 160), (40, 44), 24)
        draw_text_center(surf, "TANK", FONT_SMALL, WHITE, (40, 80))

        # Right health
        pygame.draw.rect(surf, (30, 30, 30), (WIDTH - 480, 30, 420, 28), border_radius=14)
        rw = int(400 * (self.right_hp / 100))
        pygame.draw.rect(surf, (120, 255, 120), (WIDTH - 410, 36, rw, 18), border_radius=10)
        pygame.draw.circle(surf, (240, 220, 200), (WIDTH - 40, 44), 24)
        draw_text_center(surf, "TECHNICIAN", FONT_SMALL, WHITE, (WIDTH - 40, 80))

        # Timer at center top
        draw_text_center(surf, str(int(self.timer)), FONT_BIG, WHITE, (WIDTH / 2, 50))

        # Super meter at bottom
        sm_w = 400
        sx = (WIDTH - sm_w) / 2
        sy = HEIGHT - 60
        pygame.draw.rect(surf, (30, 30, 30), (sx - 6, sy - 6, sm_w + 12, 32), border_radius=8)
        color = (255, 100, 200) if self.super_full else (80, 80, 80)
        pygame.draw.rect(surf, color, (sx, sy, sm_w, 20), border_radius=8)
        draw_text_center(surf, "SUPER METER", FONT_SMALL, WHITE, (WIDTH / 2, sy + 10))

        # instructions
        draw_text_center(surf, "Press SPACE to unleash the Tank's Super Move", FONT_SMALL, WHITE, (WIDTH / 2, HEIGHT - 20))


class Game:
    def __init__(self):
        self.state = STATE_MENU
        self.precision = PrecisionCutMode()
        self.brawl = BrawlMode()
        self.running = True
        self.menu_selected = 0  # 0 left PRECISION, 1 right BRAWL

    def run(self):
        while self.running:
            dt = CLOCK.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        mouse_down = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == STATE_MENU:
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.menu_selected = min(1, self.menu_selected + 1)
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.menu_selected = max(0, self.menu_selected - 1)
                    if event.key == pygame.K_RETURN:
                        if self.menu_selected == 0:
                            self.state = STATE_PRECISION
                            self.precision.reset()
                        else:
                            self.state = STATE_BRAWL
                            self.brawl.reset()
                else:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_MENU
                    if self.state == STATE_BRAWL:
                        if event.key == pygame.K_SPACE:
                            # trigger super
                            self.brawl.update(0, {"super": True})
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
        # store mouse_down in self for update
        self._mouse_down = pygame.mouse.get_pressed()[0] or mouse_down

    def update(self, dt: float):
        if self.state == STATE_MENU:
            pass
        elif self.state == STATE_PRECISION:
            self.precision.update(dt, pygame.mouse.get_pos(), self._mouse_down)
        elif self.state == STATE_BRAWL:
            # simple inputs: left/right arrows move left fighter
            keys = pygame.key.get_pressed()
            inputs = {
                "left_move": keys[pygame.K_a] or keys[pygame.K_LEFT],
                "right_move": keys[pygame.K_d] or keys[pygame.K_RIGHT],
                "super": False,
            }
            # check for super key (space pressed) - we detect via events in handle_events, but allow here too
            if keys[pygame.K_SPACE]:
                inputs["super"] = True
            self.brawl.update(dt, inputs)

    def draw_menu(self, surf: pygame.Surface):
        surf.fill((25, 20, 20))

        # split screen composition
        mid = WIDTH // 2
        # left panel (PRECISION CUT)
        left_rect = pygame.Rect(40, 80, mid - 120, HEIGHT - 160)
        right_rect = pygame.Rect(mid + 40, 80, mid - 120, HEIGHT - 160)

        thick_outline_rect(surf, left_rect, (30, 30, 35), (20, 20, 20), thickness=6)
        thick_outline_rect(surf, right_rect, (30, 30, 35), (20, 20, 20), thickness=6)

        # icons
        # left icon: crossed golden scissors and clipper
        # draw scissors
        sc_cx = left_rect.x + 120
        sc_cy = left_rect.y + 140
        pygame.draw.circle(surf, GOLD, (sc_cx - 10, sc_cy - 4), 20)
        pygame.draw.circle(surf, GOLD, (sc_cx + 10, sc_cy + 4), 20)
        pygame.draw.line(surf, (40, 40, 40), (sc_cx - 30, sc_cy - 30), (sc_cx + 30, sc_cy + 30), 8)
        # clipper icon
        pygame.draw.rect(surf, GOLD, (sc_cx + 40, sc_cy - 18, 64, 24), border_radius=6)

        draw_text_center(surf, "PRECISION CUT", FONT_MED, ELECTRIC_BLUE, (left_rect.centerx, left_rect.y + 40))
        draw_text_center(surf, "Focus. Calm. Craft.", FONT_SMALL, (200, 200, 200), (left_rect.centerx, left_rect.y + 84))

        # right icon: flaming fist
        ff_cx = right_rect.x + 120
        ff_cy = right_rect.y + 140
        # flame base
        pygame.draw.polygon(surf, (255, 140, 40), [(ff_cx - 30, ff_cy + 30), (ff_cx, ff_cy - 40), (ff_cx + 30, ff_cy + 30)])
        pygame.draw.circle(surf, (220, 40, 40), (ff_cx, ff_cy), 28)

        draw_text_center(surf, "STREET BRAWL", FONT_MED, NEON_RED, (right_rect.centerx, right_rect.y + 40))
        draw_text_center(surf, "Loud. Fast. Chaotic.", FONT_SMALL, (200, 200, 200), (right_rect.centerx, right_rect.y + 84))

        # draw four characters vertically centered between the panels
        chars_x = WIDTH / 2
        base_y = HEIGHT / 2
        spacing = 110

        # Character A (The Tank)
        self.draw_character_icon(surf, (chars_x - 260, base_y - spacing * 1.5), "The Tank", (200, 140, 120))
        # Character B (The All-rounder)
        self.draw_character_icon(surf, (chars_x - 80, base_y - spacing * 0.5), "All-rounder", (140, 160, 200))
        # Character C (The Brawler)
        self.draw_character_icon(surf, (chars_x + 100, base_y - spacing * 0.5), "Brawler", (180, 130, 90))
        # Character D (The Technicus)
        self.draw_character_icon(surf, (chars_x + 260, base_y - spacing * 1.5), "Technicus", (190, 190, 220))

        # selection highlight
        if self.menu_selected == 0:
            pygame.draw.rect(surf, ELECTRIC_BLUE, (left_rect.x + 6, left_rect.y + 6, left_rect.width - 12, left_rect.height - 12), 4, border_radius=12)
        else:
            pygame.draw.rect(surf, NEON_RED, (right_rect.x + 6, right_rect.y + 6, right_rect.width - 12, right_rect.height - 12), 4, border_radius=12)

        # UI hints
        draw_text_center(surf, "Use ← → or A D to choose, ENTER to start", FONT_SMALL, WHITE, (WIDTH / 2, HEIGHT - 36))

    def draw_character_icon(self, surf: pygame.Surface, pos: Tuple[int, int], name: str, color: Tuple[int, int, int]):
        x, y = int(pos[0]), int(pos[1])
        # thick outlined head + body (Arcade sprite feel)
        pygame.draw.circle(surf, (14, 14, 14), (x, y - 18), 46)  # outline
        pygame.draw.circle(surf, color, (x, y - 18), 42)
        pygame.draw.rect(surf, (24, 24, 24), (x - 36, y + 20, 72, 28), border_radius=8)
        draw_text_center(surf, name, FONT_SMALL, WHITE, (x, y + 72))

    def draw(self):
        if self.state == STATE_MENU:
            self.draw_menu(SCREEN)
        elif self.state == STATE_PRECISION:
            self.precision.draw(SCREEN)
        elif self.state == STATE_BRAWL:
            self.brawl.draw(SCREEN)


if __name__ == "__main__":
    game = Game()
    game.run()
