import math
import random
import sys

import pygame


pygame.init()

WIDTH, HEIGHT = 1000, 700
CENTER = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Orbital Guard")
clock = pygame.time.Clock()

title_font = pygame.font.Font(None, 68)
label_font = pygame.font.Font(None, 30)
body_font = pygame.font.Font(None, 24)
mono_font = pygame.font.Font(None, 28)

BG = (8, 13, 28)
GRID = (18, 42, 68)
WHITE = (235, 245, 255)
CYAN = (96, 224, 255)
BLUE = (92, 120, 255)
MINT = (115, 255, 205)
ORANGE = (255, 170, 88)
RED = (255, 96, 124)
PANEL_FILL = (18, 26, 54, 170)


def clamp(value, low, high):
    return max(low, min(high, value))


def draw_glow_circle(surface, color, center, radius, width=2):
    for extra in (14, 8, 4):
        glow_surface = pygame.Surface((radius * 2 + extra * 2 + 4, radius * 2 + extra * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*color, 24), (glow_surface.get_width() // 2, glow_surface.get_height() // 2), radius + extra, width)
        surface.blit(glow_surface, (center[0] - glow_surface.get_width() // 2, center[1] - glow_surface.get_height() // 2))
    pygame.draw.circle(surface, color, center, radius, width)


def draw_panel(surface, rect, title, rows):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, PANEL_FILL, panel.get_rect(), border_radius=24)
    pygame.draw.rect(panel, (*CYAN, 70), panel.get_rect(), width=2, border_radius=24)
    surface.blit(panel, rect.topleft)

    title_surf = label_font.render(title, True, CYAN)
    surface.blit(title_surf, (rect.x + 18, rect.y + 14))
    for i, row in enumerate(rows):
        text = body_font.render(row, True, WHITE)
        surface.blit(text, (rect.x + 18, rect.y + 52 + i * 24))


def draw_background(surface, tick):
    surface.fill(BG)
    for x in range(0, WIDTH, 48):
        pygame.draw.line(surface, GRID, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 48):
        pygame.draw.line(surface, GRID, (0, y), (WIDTH, y), 1)

    for i in range(5):
        radius = 120 + i * 70 + int(8 * math.sin(tick * 0.01 + i))
        color = (20 + i * 10, 40 + i * 15, 70 + i * 18)
        pygame.draw.circle(surface, color, CENTER, radius, 1)

    sweep_angle = tick * 0.02
    end = CENTER + pygame.Vector2(math.cos(sweep_angle), math.sin(sweep_angle)) * 320
    pygame.draw.line(surface, (*CYAN, 60), CENTER, end, 2)


def reset_game():
    return {
        "angle": -math.pi / 2,
        "heat": 0.0,
        "shield": 100.0,
        "energy": 100.0,
        "score": 0,
        "combo": 0,
        "best_combo": 0,
        "projectiles": [],
        "enemies": [],
        "pulse": [],
        "spawn_timer": 0,
        "game_over": False,
    }


def spawn_enemy(state):
    angle = random.random() * math.tau
    radius = random.randint(380, 460)
    pos = CENTER + pygame.Vector2(math.cos(angle), math.sin(angle)) * radius
    velocity = (CENTER - pos).normalize() * random.uniform(1.4, 2.8)
    state["enemies"].append(
        {
            "pos": pygame.Vector2(pos),
            "vel": velocity,
            "radius": random.randint(18, 26),
            "hp": random.randint(1, 3),
            "accent": random.choice([CYAN, MINT, ORANGE, RED]),
        }
    )


state = reset_game()
tick = 0
running = True

while running:
    dt = clock.tick(FPS) / 1000.0
    tick += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if state["game_over"] and event.key == pygame.K_r:
                state = reset_game()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not state["game_over"]:
            if state["heat"] < 85 and state["energy"] >= 8:
                turret_pos = CENTER + pygame.Vector2(math.cos(state["angle"]), math.sin(state["angle"])) * 132
                velocity = pygame.Vector2(math.cos(state["angle"]), math.sin(state["angle"])) * 9.5
                state["projectiles"].append({"pos": pygame.Vector2(turret_pos), "vel": velocity, "life": 90})
                state["heat"] = clamp(state["heat"] + 11, 0, 100)
                state["energy"] = clamp(state["energy"] - 8, 0, 100)

    if not state["game_over"]:
        mouse = pygame.Vector2(pygame.mouse.get_pos())
        direction = mouse - CENTER
        if direction.length_squared() > 0:
            state["angle"] = math.atan2(direction.y, direction.x)

        state["heat"] = clamp(state["heat"] - 18 * dt, 0, 100)
        state["energy"] = clamp(state["energy"] + 14 * dt, 0, 100)

        state["spawn_timer"] += 1
        spawn_interval = max(18, 50 - state["score"] // 120)
        if state["spawn_timer"] >= spawn_interval:
            state["spawn_timer"] = 0
            spawn_enemy(state)

        for projectile in state["projectiles"][:]:
            projectile["pos"] += projectile["vel"]
            projectile["life"] -= 1
            if projectile["life"] <= 0:
                state["projectiles"].remove(projectile)

        core_radius = 80
        for enemy in state["enemies"][:]:
            enemy["pos"] += enemy["vel"]
            if enemy["pos"].distance_to(CENTER) <= core_radius:
                state["shield"] -= 22
                state["combo"] = 0
                state["pulse"].append({"radius": core_radius, "life": 24, "color": RED})
                state["enemies"].remove(enemy)
                if state["shield"] <= 0:
                    state["game_over"] = True
                continue

            hit = False
            for projectile in state["projectiles"][:]:
                if projectile["pos"].distance_to(enemy["pos"]) <= enemy["radius"] + 6:
                    if projectile in state["projectiles"]:
                        state["projectiles"].remove(projectile)
                    enemy["hp"] -= 1
                    state["pulse"].append({"radius": enemy["radius"] + 10, "life": 18, "color": enemy["accent"], "pos": enemy["pos"].copy()})
                    if enemy["hp"] <= 0:
                        if enemy in state["enemies"]:
                            state["enemies"].remove(enemy)
                        state["combo"] += 1
                        state["best_combo"] = max(state["best_combo"], state["combo"])
                        state["score"] += 25 + state["combo"] * 6
                    hit = True
                    break
            if not hit and enemy["pos"].distance_to(CENTER) < 160:
                enemy["vel"].scale_to_length(enemy["vel"].length() + 0.005)

        for ring in state["pulse"][:]:
            ring["radius"] += 6
            ring["life"] -= 1
            if ring["life"] <= 0:
                state["pulse"].remove(ring)

    draw_background(screen, tick)

    for ring in state["pulse"]:
        alpha = int(180 * ring["life"] / 24)
        pulse_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        center = ring.get("pos", CENTER)
        pygame.draw.circle(pulse_surface, (*ring["color"], alpha), center, int(ring["radius"]), 2)
        screen.blit(pulse_surface, (0, 0))

    draw_glow_circle(screen, BLUE, CENTER, 106, 2)
    draw_glow_circle(screen, CYAN, CENTER, 80, 3)
    pygame.draw.circle(screen, (18, 24, 60), CENTER, 76)
    core_text = label_font.render("CORE", True, WHITE)
    screen.blit(core_text, core_text.get_rect(center=(CENTER.x, CENTER.y - 12)))
    shield_text = mono_font.render(f"{int(max(0, state['shield']))}%", True, MINT if state["shield"] > 35 else RED)
    screen.blit(shield_text, shield_text.get_rect(center=(CENTER.x, CENTER.y + 18)))

    for enemy in state["enemies"]:
        draw_glow_circle(screen, enemy["accent"], enemy["pos"], enemy["radius"] + 4, 1)
        pygame.draw.circle(screen, (24, 34, 70), enemy["pos"], enemy["radius"])
        pygame.draw.circle(screen, enemy["accent"], enemy["pos"], enemy["radius"], 2)
        hp_width = enemy["radius"] * 2
        hp_rect = pygame.Rect(enemy["pos"].x - enemy["radius"], enemy["pos"].y + enemy["radius"] + 8, hp_width, 4)
        pygame.draw.rect(screen, (40, 46, 72), hp_rect, border_radius=2)
        pygame.draw.rect(screen, enemy["accent"], (hp_rect.x, hp_rect.y, hp_width * enemy["hp"] / 3, hp_rect.height), border_radius=2)

    for projectile in state["projectiles"]:
        pygame.draw.circle(screen, WHITE, projectile["pos"], 4)
        pygame.draw.circle(screen, CYAN, projectile["pos"], 8, 1)

    turret_pos = CENTER + pygame.Vector2(math.cos(state["angle"]), math.sin(state["angle"])) * 132
    barrel_end = CENTER + pygame.Vector2(math.cos(state["angle"]), math.sin(state["angle"])) * 196
    pygame.draw.line(screen, CYAN, CENTER, barrel_end, 8)
    pygame.draw.circle(screen, (24, 32, 68), turret_pos, 24)
    draw_glow_circle(screen, CYAN, turret_pos, 28, 2)

    title = title_font.render("ORBITAL GUARD", True, WHITE)
    screen.blit(title, (34, 28))
    subtitle = label_font.render("Aim with mouse. Left click fires. Protect the core.", True, CYAN)
    screen.blit(subtitle, (38, 92))

    draw_panel(
        screen,
        pygame.Rect(34, 132, 270, 150),
        "TACTICAL FEED",
        [
            f"Score      {state['score']:05d}",
            f"Combo      x{state['combo']}",
            f"Best       x{state['best_combo']}",
            f"Threats    {len(state['enemies']):02d}",
        ],
    )
    draw_panel(
        screen,
        pygame.Rect(34, 300, 270, 132),
        "SYSTEM LOAD",
        [
            f"Heat       {int(state['heat']):02d}%",
            f"Energy     {int(state['energy']):02d}%",
            f"Shield     {int(max(0, state['shield'])):02d}%",
        ],
    )

    heat_rect = pygame.Rect(40, 474, 258, 14)
    energy_rect = pygame.Rect(40, 522, 258, 14)
    pygame.draw.rect(screen, (40, 46, 72), heat_rect, border_radius=7)
    pygame.draw.rect(screen, (40, 46, 72), energy_rect, border_radius=7)
    pygame.draw.rect(screen, ORANGE, (heat_rect.x, heat_rect.y, heat_rect.width * state["heat"] / 100, heat_rect.height), border_radius=7)
    pygame.draw.rect(screen, MINT, (energy_rect.x, energy_rect.y, energy_rect.width * state["energy"] / 100, energy_rect.height), border_radius=7)
    screen.blit(body_font.render("Heat", True, WHITE), (40, 450))
    screen.blit(body_font.render("Energy", True, WHITE), (40, 498))

    hint = body_font.render("Press ESC to quit. Press R to restart after failure.", True, WHITE)
    screen.blit(hint, (34, HEIGHT - 42))

    if state["game_over"]:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 10, 24, 200))
        screen.blit(overlay, (0, 0))
        failed = title_font.render("CORE BREACH", True, WHITE)
        score = label_font.render(f"Final score {state['score']:05d}", True, CYAN)
        retry = label_font.render("Press R to restart or ESC to quit", True, WHITE)
        screen.blit(failed, failed.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 30)))
        screen.blit(score, score.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 28)))
        screen.blit(retry, retry.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 72)))

    pygame.display.flip()

pygame.quit()
sys.exit()
