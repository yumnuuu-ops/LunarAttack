import pygame
import random
import sys
import math

pygame.init()
pygame.font.init()

# Screen configuration
SCREEN_W, SCREEN_H = 1000, 700
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("LunarAttack - Interactive Fading Effects Simulation")
clock = pygame.time.Clock()

# Typography
try:
    font_title = pygame.font.Font("PressStart2P-Regular.ttf", 20)
    font_body = pygame.font.Font("PressStart2P-Regular.ttf", 10)
    font_large = pygame.font.Font("PressStart2P-Regular.ttf", 14)
except Exception:
    font_title = pygame.font.SysFont("Consolas", 28, bold=True)
    font_body = pygame.font.SysFont("Consolas", 14)
    font_large = pygame.font.SysFont("Consolas", 18, bold=True)

# Color Palette
TEXT_COLOR = (220, 220, 240)
HIGHLIGHT_COLOR = (0, 190, 255) # Deep Space Azure

# Background Starfield Data
stars = []
for _ in range(80):
    stars.append({
        'x': random.randint(0, SCREEN_W),
        'y': random.randint(0, SCREEN_H),
        'size': random.choice([1, 2, 2.5]),
        'alpha': random.randint(100, 255),
        'twinkle_speed': random.uniform(0.02, 0.08),
        'time': random.uniform(0, 100)
    })

# Particles list
ghosts = []
glow_puffs = []

# Class definitions for fading ghosts
class FadeGhost:
    def __init__(self, x, y, image, fade_speed=12, shrink_rate=0.98, drift_vy=0.0):
        self.x = x
        self.y = y
        self.original_image = image
        self.alpha = 255
        self.fade_speed = fade_speed
        self.shrink_rate = shrink_rate
        self.drift_vy = drift_vy
        self.scale = 1.0

    def update(self):
        self.alpha -= self.fade_speed
        self.y += self.drift_vy
        self.scale *= self.shrink_rate

    def is_dead(self):
        return self.alpha <= 0

    def draw(self, surface):
        if self.alpha <= 0:
            return
        
        w, h = self.original_image.get_size()
        new_w = int(w * self.scale)
        new_h = int(h * self.scale)
        if new_w <= 0 or new_h <= 0:
            return
            
        scaled_img = pygame.transform.scale(self.original_image, (new_w, new_h))
        scaled_img.set_alpha(self.alpha)
        
        rect = scaled_img.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(scaled_img, rect.topleft)

# Auxiliary soft radial glow for the dissolve effect
class GlowPuff:
    def __init__(self, x, y, color, start_size, max_size, life, decay):
        self.x = x
        self.y = y
        self.color = color
        self.size = start_size
        self.max_size = max_size
        self.life = life
        self.age = 0
        self.decay = decay

    def update(self):
        self.age += self.decay
        progress = min(1.0, self.age / self.life)
        self.size = self.max_size * (0.2 + 0.8 * math.sin(progress * (math.pi / 2)))

    def is_dead(self):
        return self.age >= self.life

    def draw(self, surface):
        alpha = max(0, int(255 * (1 - (self.age / self.life))))
        if alpha <= 0:
            return
        
        size_int = max(2, int(self.size))
        temp_surface = pygame.Surface((size_int * 2, size_int * 2), pygame.SRCALPHA)
        
        # Soft radial gradient
        for r in range(size_int, 0, -2):
            ratio = r / size_int
            layer_alpha = int(alpha * (1.0 - ratio) * 0.35)
            if layer_alpha > 0:
                pygame.draw.circle(temp_surface, (self.color[0], self.color[1], self.color[2], layer_alpha), (size_int, size_int), r)
                
        surface.blit(temp_surface, (int(self.x) - size_int, int(self.y) - size_int))

# Custom Radial Gradient Drawing to simulate Nebula background (#000517)
def draw_nebula_background(surface):
    surface.fill((0, 5, 23)) # EXACT hex #000517
    
    # Soft space gas clouds
    glow_spots = [
        {"x": 120, "y": 140, "color": (12, 35, 95), "r": 260},
        {"x": 880, "y": 140, "color": (18, 40, 110), "r": 290},
        {"x": 500, "y": 500, "color": (8, 25, 75), "r": 360}
    ]
    for spot in glow_spots:
        cx, cy = spot["x"], spot["y"]
        color = spot["color"]
        max_r = spot["r"]
        for r in range(max_r, 0, -30):
            layer_alpha = int(10 * (1 - r / max_r))
            layer_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(layer_surf, (color[0], color[1], color[2], layer_alpha), (r, r), r)
            surface.blit(layer_surf, (cx - r, cy - r))

def draw_stars(surface):
    for star in stars:
        star['time'] += star['twinkle_speed']
        twinkle = abs(math.sin(star['time']))
        alpha = int(star['alpha'] * (0.4 + 0.6 * twinkle))
        star_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, (200, 225, 255, int(alpha * 0.8)), (5, 5), star['size'])
        surface.blit(star_surf, (int(star['x']) - 5, int(star['y']) - 5))

# Generate the actual plane image to use for fading
def create_plane_image():
    surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    # Left & Right wings
    pygame.draw.polygon(surf, (40, 42, 50), [(30, 10), (10, 45), (22, 45)])
    pygame.draw.polygon(surf, (40, 42, 50), [(30, 10), (50, 45), (38, 45)])
    # Main fuselage
    pygame.draw.polygon(surf, (60, 62, 72), [(30, 2), (20, 42), (40, 42)])
    pygame.draw.polygon(surf, (30, 31, 38), [(30, 2), (24, 42), (36, 42)])
    # Glowing Orange cockpit center light
    pygame.draw.rect(surf, (255, 90, 0), pygame.Rect(28, 25, 4, 10), border_radius=1)
    # Glowing Orange wing borders
    pygame.draw.line(surf, (255, 70, 0), (10, 45), (15, 30), 2)
    pygame.draw.line(surf, (255, 70, 0), (50, 45), (45, 30), 2)
    # Engine nozzle at the back
    pygame.draw.rect(surf, (70, 75, 85), pygame.Rect(26, 42, 8, 4))
    return surf

# Draw user plane
def draw_user_plane(surface, x, y, plane_image):
    surface.blit(plane_image, (x - 30, y - 30))

# --- POOF / FADING VARIATIONS ---

# 1. Clean Fade & Shrink (Minimalist, disappears seamlessly)
def trigger_fade_shrink(x, y, plane_image):
    ghosts.append(FadeGhost(x, y, plane_image, fade_speed=10, shrink_rate=0.96, drift_vy=0.0))

# 2. Fade & Dissolve (Fades with a soft blue/cyan background nebula puff)
def trigger_fade_dissolve(x, y, plane_image):
    # Fades out the plane
    ghosts.append(FadeGhost(x, y, plane_image, fade_speed=12, shrink_rate=0.98, drift_vy=0.0))
    # Spawns soft glowing vapor matching background highlights
    glow_puffs.append(GlowPuff(x, y, (0, 180, 255), 10, 50, 1.0, 0.04))

# 3. Drifting Celestial Vapor (Drifts upwards like steam in space)
def trigger_drifting_fade(x, y, plane_image):
    # Fades and slowly drifts up
    ghosts.append(FadeGhost(x, y, plane_image, fade_speed=8, shrink_rate=0.97, drift_vy=-0.8))

# Main loop
running = True
target_dummies = [
    {"x": 250, "y": 300, "alive": True},
    {"x": 750, "y": 300, "alive": True}
]

plane_image = create_plane_image()

EFFECT_SHRINK, EFFECT_DISSOLVE, EFFECT_DRIFT = 1, 2, 3
current_effect = EFFECT_SHRINK

while running:
    # Handle events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r: # Reset planes
                for dummy in target_dummies:
                    dummy["alive"] = True
            elif event.key == pygame.K_1:
                current_effect = EFFECT_SHRINK
            elif event.key == pygame.K_2:
                current_effect = EFFECT_DISSOLVE
            elif event.key == pygame.K_3:
                current_effect = EFFECT_DRIFT
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                mx, my = event.pos
                hit_anything = False
                for dummy in target_dummies:
                    if dummy["alive"] and math.hypot(mx - dummy["x"], my - dummy["y"]) < 40:
                        if current_effect == EFFECT_SHRINK:
                            trigger_fade_shrink(dummy["x"], dummy["y"], plane_image)
                        elif current_effect == EFFECT_DISSOLVE:
                            trigger_fade_dissolve(dummy["x"], dummy["y"], plane_image)
                        elif current_effect == EFFECT_DRIFT:
                            trigger_drifting_fade(dummy["x"], dummy["y"], plane_image)
                        dummy["alive"] = False
                        hit_anything = True
                
                if not hit_anything:
                    # Explode/Fade at click position directly
                    if current_effect == EFFECT_SHRINK:
                        trigger_fade_shrink(mx, my, plane_image)
                    elif current_effect == EFFECT_DISSOLVE:
                        trigger_fade_dissolve(mx, my, plane_image)
                    elif current_effect == EFFECT_DRIFT:
                        trigger_drifting_fade(mx, my, plane_image)

    # 1. Update Game State
    for g in ghosts[:]:
        g.update()
        if g.is_dead():
            ghosts.remove(g)
            
    for p in glow_puffs[:]:
        p.update()
        if p.is_dead():
            glow_puffs.remove(p)

    # 2. Rendering
    # Background Nebula Layer & Twinkling Stars
    draw_nebula_background(screen)
    draw_stars(screen)

    # Draw User Planes
    for dummy in target_dummies:
        if dummy["alive"]:
            draw_user_plane(screen, dummy["x"], dummy["y"], plane_image)
            # Draw selection indicator
            pygame.draw.circle(screen, (0, 190, 255, 100), (dummy["x"], dummy["y"]), 35, 1)

    # Render active glow effects first (draw under plane ghosts)
    for p in glow_puffs:
        p.draw(screen)

    # Render active fading ghosts on top
    for g in ghosts:
        g.draw(screen)

    # --- Modern Premium Overlay UI ---
    # Header bar
    header_rect = pygame.Rect(0, 0, SCREEN_W, 60)
    pygame.Surface.fill(screen, (8, 9, 20), header_rect)
    pygame.draw.line(screen, HIGHLIGHT_COLOR, (0, 60), (SCREEN_W, 60), 2)
    
    title_text = font_title.render("SMOOTH ARCADE FADING EFFECTS SIMULATOR", True, TEXT_COLOR)
    screen.blit(title_text, (20, 20))
    
    # Instructions Box
    panel_rect = pygame.Rect(20, SCREEN_H - 170, 960, 130)
    panel_surf = pygame.Surface((960, 130), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (8, 10, 24, 210), pygame.Rect(0, 0, 960, 130), border_radius=6)
    pygame.draw.rect(panel_surf, HIGHLIGHT_COLOR, pygame.Rect(0, 0, 960, 130), 1, border_radius=6)
    screen.blit(panel_surf, (20, SCREEN_H - 170))
    
    inst1 = font_large.render("SMOOTH DISSOLVING & FADING GHOST EFFECTS:", True, HIGHLIGHT_COLOR)
    
    c1 = HIGHLIGHT_COLOR if current_effect == EFFECT_SHRINK else TEXT_COLOR
    c2 = HIGHLIGHT_COLOR if current_effect == EFFECT_DISSOLVE else TEXT_COLOR
    c3 = HIGHLIGHT_COLOR if current_effect == EFFECT_DRIFT else TEXT_COLOR
    
    opt1 = font_large.render("[1] Clean Fade & Shrink (Fades and scales down into nothing)", True, c1)
    opt2 = font_large.render("[2] Fade & Dissolve (Fades out with a soft background nebula glow)", True, c2)
    opt3 = font_large.render("[3] Drifting Celestial Vapor (Fades while drifting slowly upwards)", True, c3)
    
    inst4 = font_body.render("CLICK PLANES TO BLOW THEM UP | PRESS [R] TO RESPAWN FIGHTERS | PRESS [ESC] TO EXIT", True, (150, 155, 170))
    
    screen.blit(inst1, (40, SCREEN_H - 155))
    screen.blit(opt1, (40, SCREEN_H - 130))
    screen.blit(opt2, (40, SCREEN_H - 110))
    screen.blit(opt3, (40, SCREEN_H - 90))
    screen.blit(inst4, (40, SCREEN_H - 65))
    
    # Active particles count
    p_count = font_body.render(f"ACTIVE FADING GHOSTS: {len(ghosts)}", True, (100, 105, 128))
    screen.blit(p_count, (20, SCREEN_H - 195))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
