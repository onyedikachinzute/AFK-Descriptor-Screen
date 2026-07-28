#!/usr/bin/env python3
"""
Quantum Singularity Matrix v4.0 – Ultimate Autonomous Geometric Engine
Nebula backdrop, bloom-glow particles, comet streaks, screen-shake shockwaves,
gravity-reactive drifting shapes, and a redesigned holo-UI deck.
"""

import sys
import time
import math
import random
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog

try:
    import pygame
except ImportError:
    print("Pygame is required. Install with: pip install pygame")
    sys.exit(1)

# ─── Configuration ──────────────────────────────────────────────
DEFAULT_MESSAGE = "Stepped into another dimension..."
STAR_COUNT = 260
TEXT_PARTICLE_COUNT = 950
SHAPE_COUNT = 10
NEBULA_BLOB_COUNT = 6
COMET_INTERVAL = (3.0, 7.0)
FPS = 60

SHAPE_TYPES = ["triangle", "square", "hexagon", "diamond", "star5"]


def hsv(hue, s, v, a=255):
    """a is in 0-255 (like normal RGBA) for consistency with the rest of the file."""
    c = pygame.Color(0, 0, 0)
    a_pct = max(0, min(100, a / 2.55))
    try:
        c.hsva = (int(hue) % 360, max(0, min(100, s)), max(0, min(100, v)), a_pct)
    except ValueError:
        c = pygame.Color(255, 255, 255, max(0, min(255, int(a))))
    return c


def glow_blit(dest_surface, draw_fn, size, pos, passes=((1.0, 60), (0.55, 110), (0.3, 160))):
    """Cheap bloom: draw shape at several soft alpha layers, biggest first."""
    for scale, alpha in passes:
        s = max(2, int(size * (1 + scale)))
        layer = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
        draw_fn(layer, s, s, int(size * (1 + scale * 0.4)), alpha)
        dest_surface.blit(layer, (pos[0] - s, pos[1] - s), special_flags=pygame.BLEND_RGB_ADD)


# ─── Drifting Nebula Cloud ───────────────────────────────────────
class NebulaBlob:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.radius = random.uniform(h * 0.25, h * 0.55)
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-3, 3)
        self.hue_offset = random.uniform(0, 360)
        self.phase = random.uniform(0, math.tau)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.phase += dt * 0.15
        if self.x < -self.radius: self.x = self.w + self.radius
        if self.x > self.w + self.radius: self.x = -self.radius
        if self.y < -self.radius: self.y = self.h + self.radius
        if self.y > self.h + self.radius: self.y = -self.radius

    def draw(self, surface, global_hue):
        pulse = 0.85 + 0.15 * math.sin(self.phase)
        r = int(self.radius * pulse)
        layer = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        hue = (global_hue * 0.4 + self.hue_offset) % 360
        for i, frac in enumerate((1.0, 0.7, 0.45, 0.2)):
            rr = int(r * frac)
            alpha = int(16 + i * 6)
            c = hsv(hue + i * 12, 70, 35, alpha)
            pygame.draw.circle(layer, c, (r, r), rr)
        surface.blit(layer, (self.x - r, self.y - r), special_flags=pygame.BLEND_RGB_ADD)


# ─── Streaking Comet ─────────────────────────────────────────────
class Comet:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset()

    def reset(self):
        edge = random.choice(["top", "left", "right"])
        if edge == "top":
            self.x, self.y = random.uniform(0, self.w), -30
            angle = random.uniform(math.pi * 0.25, math.pi * 0.45)
        elif edge == "left":
            self.x, self.y = -30, random.uniform(0, self.h * 0.5)
            angle = random.uniform(math.pi * 0.1, math.pi * 0.3)
        else:
            self.x, self.y = self.w + 30, random.uniform(0, self.h * 0.5)
            angle = math.pi - random.uniform(math.pi * 0.1, math.pi * 0.3)
        speed = random.uniform(650, 950)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.trail = []
        self.life = 1.6
        self.hue = random.uniform(0, 360)
        self.dead = False

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.trail.append((self.x, self.y))
        if len(self.trail) > 16:
            self.trail.pop(0)
        self.life -= dt
        if self.life <= 0 or self.x > self.w + 60 or self.y > self.h + 60:
            self.dead = True

    def draw(self, surface):
        n = len(self.trail)
        for i, (tx, ty) in enumerate(self.trail):
            frac = i / max(1, n - 1)
            alpha = int(180 * frac)
            radius = max(1, int(4 * frac))
            c = hsv(self.hue, 40, 100, alpha)
            pygame.draw.circle(surface, c, (int(tx), int(ty)), radius)
        pygame.draw.circle(surface, hsv(self.hue, 20, 100, 255), (int(self.x), int(self.y)), 3)


# ─── Drifting Space Anomaly (Shapes) ────────────────────────────
class SpaceAnomaly:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.trail = []
        self.reset()
        self.x = random.choice([-50, self.w + 50])
        self.y = random.uniform(0, self.h)

    def reset(self):
        if random.random() > 0.5:
            self.x = -40 if random.random() > 0.5 else self.w + 40
            self.y = random.uniform(0, self.h)
        else:
            self.x = random.uniform(0, self.w)
            self.y = -40 if random.random() > 0.5 else self.h + 40

        self.shape_type = random.choice(SHAPE_TYPES)
        self.size = random.uniform(18, 42)
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-1.5, 1.5)
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-1.2, 1.2)
        self.color_offset = random.uniform(0, 360)
        self.trail.clear()

    def update(self, center_pos, dt):
        cx, cy = center_pos
        dx = cx - self.x
        dy = cy - self.y
        dist = math.hypot(dx, dy)

        if dist < 450:
            gravity_force = (450 - dist) * 0.012
            if dist > 0:
                self.vx += (dx / dist) * gravity_force
                self.vy += (dy / dist) * gravity_force
                self.rot_speed += (self.vx * 0.1)

        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.angle += self.rot_speed * dt * 60

        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

        if dist < 20 or self.x < -100 or self.x > self.w + 100 or self.y < -100 or self.y > self.h + 100:
            self.reset()

    def _points(self, cx, cy, size, rad):
        pts = []
        if self.shape_type == "square":
            for i in range(4):
                a = rad + i * (math.pi / 2)
                pts.append((cx + math.cos(a) * size, cy + math.sin(a) * size))
        elif self.shape_type == "triangle":
            for i in range(3):
                a = rad + i * (2 * math.pi / 3)
                pts.append((cx + math.cos(a) * size, cy + math.sin(a) * size))
        elif self.shape_type == "hexagon":
            for i in range(6):
                a = rad + i * (math.pi / 3)
                pts.append((cx + math.cos(a) * size, cy + math.sin(a) * size))
        elif self.shape_type == "diamond":
            for i, mult in enumerate([1.4, 0.6, 1.4, 0.6]):
                a = rad + i * (math.pi / 2)
                pts.append((cx + math.cos(a) * size * mult, cy + math.sin(a) * size * mult))
        elif self.shape_type == "star5":
            for i in range(10):
                a = rad + i * (math.pi / 5)
                r = size if i % 2 == 0 else size * 0.45
                pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        return pts

    def draw(self, surface, global_hue):
        hue = (global_hue + self.color_offset) % 360
        rad = math.radians(self.angle)

        # faint motion trail
        for i, (tx, ty) in enumerate(self.trail):
            frac = i / max(1, len(self.trail) - 1)
            trail_pts = self._points(tx, ty, self.size * 0.6, rad)
            if len(trail_pts) >= 3:
                c = hsv(hue, 80, 60, int(50 * frac))
                pygame.draw.polygon(surface, c, trail_pts, 1)

        points = self._points(self.x, self.y, self.size, rad)
        if len(points) >= 3:
            # outer glow pass
            glow_c = hsv(hue, 80, 90, 35)
            pygame.draw.polygon(surface, glow_c, points, 6)
            core_c = hsv(hue, 70, 100, 255)
            pygame.draw.polygon(surface, core_c, points, 2)


# ─── Kinetic Text Node ──────────────────────────────────────────
class QuantumParticle:
    def __init__(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y
        self.x = target_x + random.uniform(-260, 260)
        self.y = target_y + random.uniform(-260, 260)
        self.vx = 0.0
        self.vy = 0.0
        self.base_size = random.uniform(1.6, 3.6)
        self.color_phase = random.uniform(0, 360)
        self.twinkle_phase = random.uniform(0, math.tau)

    def update(self, force_pos, force_radius, force_strength, dt):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist_to_home = math.hypot(dx, dy)

        spring = 0.14
        damping = 0.82

        self.vx += dx * spring
        self.vy += dy * spring

        if dist_to_home < 60 and dist_to_home > 1:
            self.vx += (-dy / dist_to_home) * 0.6
            self.vy += (dx / dist_to_home) * 0.6

        fx, fy = force_pos
        fdx = self.x - fx
        fdy = self.y - fy
        f_dist = math.hypot(fdx, fdy)

        if f_dist < force_radius:
            power = (force_radius - f_dist) * force_strength
            if f_dist > 0:
                self.vx += (fdx / f_dist) * power
                self.vy += (fdy / f_dist) * power

        self.vx *= damping
        self.vy *= damping
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.color_phase = (self.color_phase + dt * 60) % 360
        self.twinkle_phase += dt * 3.0

    def draw(self, surface, global_hue):
        hue = (global_hue + self.color_phase) % 360
        twinkle = 0.75 + 0.25 * math.sin(self.twinkle_phase)
        size = max(1, int(self.base_size * twinkle))
        color = hsv(hue, 95, 100, 255)
        # tiny halo for a soft glow feel without per-particle surfaces (perf)
        halo = hsv(hue, 90, 100, 70)
        pygame.draw.circle(surface, halo, (int(self.x), int(self.y)), size + 2)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), size)


# ─── 3D Starfield Vector ────────────────────────────────────────
class WarpStar:
    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.reset(initial=True)

    def reset(self, initial=False):
        self.x = random.uniform(-self.w / 2, self.w / 2)
        self.y = random.uniform(-self.h / 2, self.h / 2)
        self.z = random.uniform(1.0, 1000.0) if initial else 1000.0
        self.prev_z = self.z
        self.speed = random.uniform(18, 38)

    def update(self, dt):
        self.prev_z = self.z
        self.z -= self.speed * dt * 60
        if self.z <= 5.0:
            self.reset()

    def draw(self, surface, global_hue):
        focal_length = 400.0
        z_safe = max(1.0, self.z)
        pz_safe = max(1.0, self.prev_z)

        px = int((self.x * focal_length) / z_safe) + self.w // 2
        py = int((self.y * focal_length) / z_safe) + self.h // 2
        ppx = int((self.x * focal_length) / pz_safe) + self.w // 2
        ppy = int((self.y * focal_length) / pz_safe) + self.h // 2

        if 0 <= px < self.w and 0 <= py < self.h:
            brightness_pct = 1.0 - (z_safe / 1000.0)
            brightness_val = int(max(0, min(100, brightness_pct * 100)))

            hue = (global_hue + 180) % 360
            color = hsv(hue, 45, brightness_val, 255)
            thickness = max(1, int(4 * brightness_pct))
            pygame.draw.line(surface, color, (px, py), (ppx, ppy), thickness)


# ─── Master Application Matrix ──────────────────────────────────
class CosmicAFKApp:
    def __init__(self, message):
        self.message = message
        self.start_time = time.time()
        self.clock = pygame.time.Clock()
        self.running = True
        self.global_hue = 0.0

        self.last_mouse_pos = (0, 0)
        self.mouse_idle_time = 0.0

        self.drone_x = 0.0
        self.drone_y = 0.0
        self.drone_time = random.uniform(0, 500)

        self.shockwave_pos = (0, 0)
        self.shockwave_radius = 0.0
        self.shockwave_active = False
        self.next_distortion_timer = random.uniform(4.0, 8.0)

        self.shake_time = 0.0
        self.shake_mag = 0.0

        self.comets = []
        self.next_comet_timer = random.uniform(*COMET_INTERVAL)

        pygame.init()
        info = pygame.display.Info()
        self.w = info.current_w
        self.h = info.current_h
        self.screen = pygame.display.set_mode((self.w, self.h), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.mouse.set_visible(False)

        # render everything onto a fixed offscreen canvas so screen-shake
        # can just re-blit it with an offset
        self.canvas = pygame.Surface((self.w, self.h))

        font_size = int(self.h * 0.30)
        try:
            self.font_main = pygame.font.Font(None, font_size)
            self.font_sub = pygame.font.Font(None, int(self.h * 0.045))
            self.font_small = pygame.font.Font(None, int(self.h * 0.028))
        except Exception:
            self.font_main = pygame.font.SysFont("impact", font_size)
            self.font_sub = pygame.font.SysFont("segoeui", int(self.h * 0.045))
            self.font_small = pygame.font.SysFont("segoeui", int(self.h * 0.028))

        self.warp_center = (self.w // 2, self.h // 2 - int(self.h * 0.08))

        self.nebulae = [NebulaBlob(self.w, self.h) for _ in range(NEBULA_BLOB_COUNT)]
        self.stars = [WarpStar(self.w, self.h) for _ in range(STAR_COUNT)]
        self.anomalies = [SpaceAnomaly(self.w, self.h) for _ in range(SHAPE_COUNT)]
        self.text_particles = []
        self.bake_text_morph_targets()

    def bake_text_morph_targets(self):
        temp_surface = self.font_main.render("AFK", True, (255, 255, 255))
        ts_w, ts_h = temp_surface.get_size()

        offset_x = (self.w - ts_w) // 2
        offset_y = (self.h - ts_h) // 2 - int(self.h * 0.08)

        valid_pixels = []
        for x in range(0, ts_w, 2):
            for y in range(0, ts_h, 2):
                if temp_surface.get_at((x, y)).r > 128:
                    valid_pixels.append((x + offset_x, y + offset_y))

        if not valid_pixels:
            valid_pixels = [(self.w // 2, self.h // 2)]

        random.shuffle(valid_pixels)
        for i in range(TEXT_PARTICLE_COUNT):
            target = valid_pixels[i % len(valid_pixels)]
            tx = target[0] + random.uniform(-1.0, 1.0)
            ty = target[1] + random.uniform(-1.0, 1.0)
            self.text_particles.append(QuantumParticle(tx, ty))

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            if dt > 0.1:
                dt = 0.1
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self, dt):
        self.global_hue = (self.global_hue + dt * 35) % 360
        current_mouse = pygame.mouse.get_pos()

        if current_mouse != self.last_mouse_pos:
            self.mouse_idle_time = 0.0
            self.last_mouse_pos = current_mouse
            active_force_pos = current_mouse
            active_radius = 160
            active_strength = 0.6
        else:
            self.mouse_idle_time += dt
            self.drone_time += dt * 0.8
            self.drone_x = self.w // 2 + math.sin(self.drone_time * 1.5) * (self.w * 0.35) + math.cos(self.drone_time * 0.7) * (self.w * 0.1)
            self.drone_y = self.warp_center[1] + math.cos(self.drone_time * 1.2) * (self.h * 0.25) + math.sin(self.drone_time * 2.1) * (self.h * 0.05)

            active_force_pos = (self.drone_x, self.drone_y)
            active_radius = 180
            active_strength = 0.45

        # Shockwave Engine Clock
        self.next_distortion_timer -= dt
        if self.next_distortion_timer <= 0:
            self.shockwave_active = True
            self.shockwave_pos = (active_force_pos[0] + random.uniform(-50, 50), active_force_pos[1] + random.uniform(-50, 50))
            self.shockwave_radius = 10.0
            self.next_distortion_timer = random.uniform(5.0, 9.0)
            self.shake_time = 0.35
            self.shake_mag = 9.0

        if self.shockwave_active:
            self.shockwave_radius += dt * 1100.0
            if self.shockwave_radius > max(self.w, self.h):
                self.shockwave_active = False

        if self.shake_time > 0:
            self.shake_time -= dt

        # Comet spawner
        self.next_comet_timer -= dt
        if self.next_comet_timer <= 0:
            self.comets.append(Comet(self.w, self.h))
            self.next_comet_timer = random.uniform(*COMET_INTERVAL)
        for c in self.comets:
            c.update(dt)
        self.comets = [c for c in self.comets if not c.dead]

        # Component Updates
        for nb in self.nebulae:
            nb.update(dt)

        for star in self.stars:
            star.update(dt)

        for anomaly in self.anomalies:
            anomaly.update(self.warp_center, dt)

        for tp in self.text_particles:
            if self.shockwave_active:
                sdx = tp.x - self.shockwave_pos[0]
                sdy = tp.y - self.shockwave_pos[1]
                s_dist = math.hypot(sdx, sdy)
                if abs(s_dist - self.shockwave_radius) < 60:
                    tp.update(self.shockwave_pos, self.shockwave_radius + 40, 1.8, dt)
                    continue
            tp.update(active_force_pos, active_radius, active_strength, dt)

    def draw(self):
        surf = self.canvas
        surf.fill((3, 2, 7))

        # Nebula backdrop (soft additive blobs)
        for nb in self.nebulae:
            nb.draw(surf, self.global_hue)

        # Background Singularity Glow
        core_radius = int(self.h * 0.50)
        core_surf = pygame.Surface((core_radius * 2, core_radius * 2), pygame.SRCALPHA)
        t = time.time()
        pulse = math.sin(t * 2.0) * 0.05 + 0.95

        for r in range(core_radius, 30, -15):
            alpha_pct = (1.0 - (r / core_radius)) ** 3
            alpha_val = int(max(0, min(110, alpha_pct * 110 * pulse)))
            hue_offset = (self.global_hue + r * 0.1) % 360
            c = hsv(hue_offset, 90, 15, alpha_val)
            pygame.draw.circle(core_surf, c, (core_radius, core_radius), r)

        surf.blit(core_surf, core_surf.get_rect(center=self.warp_center), special_flags=pygame.BLEND_RGB_ADD)

        # Layers: Stars -> Comets -> Floating Kinetic Shapes -> Text Particles
        for star in self.stars:
            star.draw(surf, self.global_hue)

        for c in self.comets:
            c.draw(surf)

        for anomaly in self.anomalies:
            anomaly.draw(surf, self.global_hue)

        for tp in self.text_particles:
            tp.draw(surf, self.global_hue)

        # Blast Ring rendering
        if self.shockwave_active and self.shockwave_radius > 0:
            sw_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            sw_alpha = int(max(0, min(150, (1.0 - (self.shockwave_radius / max(self.w, self.h))) * 150)))
            sw_color = hsv((self.global_hue + 120) % 360, 85, 100, sw_alpha)
            pygame.draw.circle(sw_surf, sw_color, (int(self.shockwave_pos[0]), int(self.shockwave_pos[1])), int(self.shockwave_radius), max(1, int(6 * (sw_alpha / 150))))
            # secondary inner ring for depth
            inner_r = max(0, self.shockwave_radius - 40)
            sw_color2 = hsv((self.global_hue + 160) % 360, 70, 100, int(sw_alpha * 0.5))
            pygame.draw.circle(sw_surf, sw_color2, (int(self.shockwave_pos[0]), int(self.shockwave_pos[1])), int(inner_r), 2)
            surf.blit(sw_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        # Bottom UI Deck Overlay
        elapsed = int(time.time() - self.start_time)
        timer_str = f"{elapsed // 3600:02d}:{(elapsed % 3600) // 60:02d}:{elapsed % 60:02d}"
        time_str = datetime.now().strftime("%H:%M:%S")
        clean_msg = self.message[:65].upper()

        accent = hsv(self.global_hue, 70, 100, 255)

        msg_surf = self.font_sub.render(clean_msg, True, (240, 245, 255))
        meta_surf = self.font_small.render(
            f"MATRIX TIME {timer_str}   •   THREADS ACTIVE   •   WALL CLOCK {time_str}", True, (130, 150, 185)
        )
        label_surf = self.font_small.render("◆ AWAY FROM KEYBOARD ◆", True, accent)

        y_anchor = self.h - int(self.h * 0.15)
        label_rect = label_surf.get_rect(center=(self.w // 2, y_anchor - int(self.h * 0.05)))
        msg_rect = msg_surf.get_rect(center=(self.w // 2, y_anchor))
        meta_rect = meta_surf.get_rect(center=(self.w // 2, y_anchor + int(self.h * 0.045)))

        pill_w = max(msg_rect.w, meta_rect.w, label_rect.w) + 110
        pill_h = int(self.h * 0.155)
        pill_center = (self.w // 2, y_anchor + int(self.h * 0.005))
        pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        pygame.draw.rect(pill, (6, 9, 20, 190), pill.get_rect(), border_radius=16)
        border_pulse = 90 + int(60 * (0.5 + 0.5 * math.sin(t * 3.0)))
        pygame.draw.rect(pill, (accent.r, accent.g, accent.b, border_pulse), pill.get_rect(), width=2, border_radius=16)

        # thin animated scanline sweeping the pill
        scan_x = int((math.sin(t * 0.6) * 0.5 + 0.5) * pill_w)
        scan = pygame.Surface((3, pill_h), pygame.SRCALPHA)
        scan.fill((accent.r, accent.g, accent.b, 60))
        pill.blit(scan, (scan_x, 0), special_flags=pygame.BLEND_RGB_ADD)

        surf.blit(pill, pill.get_rect(center=pill_center))
        surf.blit(label_surf, label_rect)
        surf.blit(msg_surf, msg_rect)
        surf.blit(meta_surf, meta_rect)

        # small corner brackets for a HUD feel
        self._draw_hud_corners(surf, accent)

        # Vignette
        self._draw_vignette(surf)

        # Screen shake: blit canvas onto real screen with offset
        if self.shake_time > 0:
            falloff = self.shake_time / 0.35
            ox = random.uniform(-1, 1) * self.shake_mag * falloff
            oy = random.uniform(-1, 1) * self.shake_mag * falloff
            self.screen.fill((0, 0, 0))
            self.screen.blit(surf, (ox, oy))
        else:
            self.screen.blit(surf, (0, 0))

    def _draw_hud_corners(self, surf, accent):
        m = int(self.h * 0.03)
        ln = int(self.h * 0.035)
        c = (accent.r, accent.g, accent.b, 140)
        corners = [
            ((m, m), (1, 1)),
            ((self.w - m, m), (-1, 1)),
            ((m, self.h - m), (1, -1)),
            ((self.w - m, self.h - m), (-1, -1)),
        ]
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        for (x, y), (dx, dy) in corners:
            pygame.draw.line(overlay, c, (x, y), (x + dx * ln, y), 2)
            pygame.draw.line(overlay, c, (x, y), (x, y + dy * ln), 2)
        surf.blit(overlay, (0, 0))

    def _draw_vignette(self, surf):
        if not hasattr(self, "_vignette_cache"):
            vig = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            max_dist = math.hypot(self.w / 2, self.h / 2)
            step = 6
            for i in range(0, max(self.w, self.h) // step + 1):
                r = self.w  # placeholder, real work done via radial rects below
                break
            # simple radial gradient using concentric rounded rects is expensive;
            # approximate with a few large soft ellipses at the corners instead.
            for cx, cy in [(0, 0), (self.w, 0), (0, self.h), (self.w, self.h)]:
                grad = pygame.Surface((int(self.w * 0.7), int(self.h * 0.7)), pygame.SRCALPHA)
                pygame.draw.ellipse(grad, (0, 0, 0, 90), grad.get_rect())
                vig.blit(grad, grad.get_rect(center=(cx, cy)))
            self._vignette_cache = vig
        surf.blit(self._vignette_cache, (0, 0), special_flags=pygame.BLEND_RGB_SUB)


# ─── Native Prompt Entry Window ───────────────────────────────────
def get_message_from_user():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    message = simpledialog.askstring(
        "COSMIC AFK ENGINE v4.0",
        "ENTER INTERSTATION MESSAGE FLAG:",
        initialvalue=DEFAULT_MESSAGE,
        parent=root
    )
    root.destroy()
    if message is None:
        sys.exit(0)
    return message.strip() or DEFAULT_MESSAGE


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else get_message_from_user()
    app = CosmicAFKApp(msg)
    try:
        app.run()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
