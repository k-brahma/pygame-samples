import math
import random
import sys

import pygame


pygame.init()

WIDTH, HEIGHT = 960, 640
LANE_COUNT = 4
ROAD_WIDTH = 520
ROAD_LEFT = (WIDTH - ROAD_WIDTH) // 2
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Drift")
clock = pygame.time.Clock()

ui_font = pygame.font.Font(None, 28)
title_font = pygame.font.Font(None, 72)
stat_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 22)

BG = (6, 10, 24)
ROAD = (18, 24, 38)
ROAD_EDGE = (0, 246, 255)
LANE = (90, 120, 170)
PANEL = (18, 24, 48, 200)
WHITE = (240, 247, 255)
PINK = (255, 70, 170)
CYAN = (0, 235, 255)
MINT = (103, 255, 194)
ORANGE = (255, 168, 72)
RED = (255, 80, 110)


def clamp(value, low, high):
    return max(low, min(high, value))


def lane_center(index):
    return ROAD_LEFT + index * LANE_WIDTH + LANE_WIDTH // 2


def draw_glow_rect(surface, rect, color, border_radius=18, glow=18, width=0):
    for i in range(glow, 0, -6):
        alpha = max(8, 70 - i * 2)
        glow_surface = pygame.Surface((rect.width + i * 2, rect.height + i * 2), pygame.SRCALPHA)
        glow_color = (*color, alpha)
        pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), width=width, border_radius=border_radius + i)
        surface.blit(glow_surface, (rect.x - i, rect.y - i))
    pygame.draw.rect(surface, color, rect, width=width, border_radius=border_radius)


def draw_panel(surface, rect, title, lines):
    panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, PANEL, panel_surface.get_rect(), border_radius=22)
    pygame.draw.rect(panel_surface, (*CYAN, 70), panel_surface.get_rect(), width=2, border_radius=22)
    surface.blit(panel_surface, rect.topleft)
    draw_glow_rect(surface, rect, (30, 170, 190), border_radius=22, glow=12, width=1)

    title_text = ui_font.render(title, True, CYAN)
    surface.blit(title_text, (rect.x + 18, rect.y + 14))
    for i, line in enumerate(lines):
        line_text = small_font.render(line, True, WHITE)
        surface.blit(line_text, (rect.x + 18, rect.y + 50 + i * 22))


def draw_background(surface, tick, stars):
    surface.fill(BG)
    gradient = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(HEIGHT):
        alpha = int(110 * (y / HEIGHT))
        pygame.draw.line(gradient, (255, 0, 125, alpha), (0, y), (WIDTH, y))
    surface.blit(gradient, (0, 0))

    for star in stars:
        star["y"] += star["speed"]
        if star["y"] > HEIGHT:
            star["y"] = 0
            star["x"] = random.randint(0, WIDTH)
        pygame.draw.circle(surface, (200, 230, 255), (int(star["x"]), int(star["y"])), star["size"])

    horizon_y = 140
    pygame.draw.rect(surface, (10, 18, 32), (0, horizon_y, WIDTH, HEIGHT - horizon_y))
    for i in range(13):
        x = i * 80 + (tick * 0.2) % 40
        height = 70 + int(30 * math.sin(i * 1.7))
        rect = pygame.Rect(x, horizon_y - height, 46, height)
        pygame.draw.rect(surface, (20, 26, 46), rect, border_radius=8)
        pygame.draw.rect(surface, (255, 0, 135), rect, width=1, border_radius=8)
        for row in range(5):
            for col in range(2):
                wx = rect.x + 8 + col * 16
                wy = rect.y + 10 + row * 12
                pygame.draw.rect(surface, (255, 210, 90), (wx, wy, 8, 5), border_radius=2)

    road_rect = pygame.Rect(ROAD_LEFT, 80, ROAD_WIDTH, HEIGHT - 80)
    pygame.draw.rect(surface, ROAD, road_rect, border_radius=32)
    draw_glow_rect(surface, road_rect, ROAD_EDGE, border_radius=32, glow=20, width=2)

    for lane in range(1, LANE_COUNT):
        x = ROAD_LEFT + lane * LANE_WIDTH
        for y in range(-40, HEIGHT, 70):
            offset = (tick * 11 + y) % 70
            pygame.draw.line(surface, LANE, (x, y + offset), (x, y + offset + 34), 3)

    for y in range(0, HEIGHT, 4):
        alpha = 12 if (y + tick // 2) % 12 == 0 else 0
        if alpha:
            pygame.draw.line(surface, (255, 255, 255, alpha), (0, y), (WIDTH, y))


def draw_car(surface, x, y, color, accent):
    body = pygame.Rect(0, 0, 68, 118)
    body.center = (x, y)
    glow = body.inflate(22, 22)
    draw_glow_rect(surface, glow, accent, border_radius=26, glow=14, width=1)
    pygame.draw.rect(surface, color, body, border_radius=18)
    pygame.draw.rect(surface, (240, 245, 255), body, width=2, border_radius=18)
    windshield = pygame.Rect(body.x + 10, body.y + 18, body.width - 20, 28)
    pygame.draw.rect(surface, (170, 240, 255), windshield, border_radius=10)
    stripe = pygame.Rect(body.x + body.width // 2 - 6, body.y + 50, 12, 38)
    pygame.draw.rect(surface, accent, stripe, border_radius=6)
    for wx in (body.x + 10, body.right - 18):
        pygame.draw.rect(surface, (20, 20, 28), (wx, body.y + 18, 8, 24), border_radius=4)
        pygame.draw.rect(surface, (20, 20, 28), (wx, body.bottom - 42, 8, 24), border_radius=4)


def reset_game():
    return {
        "lane": 1,
        "x": lane_center(1),
        "speed": 1.0,
        "boost": 100,
        "score": 0,
        "best_combo": 0,
        "combo": 0,
        "shield": 100,
        "cooldown": 0,
        "game_over": False,
        "traffic": [],
        "shards": [],
    }


def spawn_traffic(state):
    lane = random.randrange(LANE_COUNT)
    if any(car["lane"] == lane and car["y"] < 180 for car in state["traffic"]):
        return
    state["traffic"].append(
        {
            "lane": lane,
            "x": lane_center(lane),
            "y": -140,
            "speed": random.uniform(7.0, 10.5) * state["speed"],
            "color": random.choice([(255, 120, 90), (255, 210, 80), (120, 255, 210)]),
        }
    )


def spawn_shard(state):
    lane = random.randrange(LANE_COUNT)
    if any(item["lane"] == lane and item["y"] < 220 for item in state["shards"]):
        return
    state["shards"].append({"lane": lane, "x": lane_center(lane), "y": -60, "pulse": random.random() * math.pi * 2})


stars = [
    {"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "speed": random.uniform(0.6, 2.0), "size": random.randint(1, 2)}
    for _ in range(90)
]

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

    keys = pygame.key.get_pressed()
    if not state["game_over"]:
        if keys[pygame.K_LEFT]:
            state["lane"] = max(0, state["lane"] - 1)
        if keys[pygame.K_RIGHT]:
            state["lane"] = min(LANE_COUNT - 1, state["lane"] + 1)

        target_x = lane_center(state["lane"])
        state["x"] += (target_x - state["x"]) * min(1, 12 * dt)

        boost_active = keys[pygame.K_SPACE] and state["boost"] > 0
        speed_target = 1.65 if boost_active else 1.0
        state["speed"] += (speed_target - state["speed"]) * min(1, 5 * dt)
        state["boost"] = clamp(state["boost"] - (33 if boost_active else -18) * dt, 0, 100)
        state["score"] += int(36 * state["speed"])

        if tick % max(16, int(42 / state["speed"])) == 0:
            spawn_traffic(state)
        if tick % 55 == 0:
            spawn_shard(state)

        player_rect = pygame.Rect(0, 0, 68, 118)
        player_rect.center = (int(state["x"]), HEIGHT - 130)

        for car in state["traffic"][:]:
            car["y"] += car["speed"] * state["speed"]
            car_rect = pygame.Rect(0, 0, 68, 118)
            car_rect.center = (int(car["x"]), int(car["y"]))
            if car_rect.colliderect(player_rect) and state["cooldown"] <= 0:
                state["shield"] -= 34
                state["combo"] = 0
                state["cooldown"] = 60
                if state["shield"] <= 0:
                    state["game_over"] = True
            if car["y"] > HEIGHT + 120:
                state["traffic"].remove(car)
                state["combo"] += 1
                state["best_combo"] = max(state["best_combo"], state["combo"])
                state["score"] += 25 + state["combo"] * 5

        for shard in state["shards"][:]:
            shard["y"] += 7.0 * state["speed"]
            shard["pulse"] += 0.12
            shard_rect = pygame.Rect(0, 0, 34, 34)
            shard_rect.center = (int(shard["x"]), int(shard["y"]))
            if shard_rect.colliderect(player_rect):
                state["boost"] = clamp(state["boost"] + 28, 0, 100)
                state["score"] += 80
                state["shards"].remove(shard)
            elif shard["y"] > HEIGHT + 60:
                state["shards"].remove(shard)

        state["cooldown"] = max(0, state["cooldown"] - 1)

    draw_background(screen, tick, stars)

    for shard in state["shards"]:
        size = 14 + int(5 * math.sin(shard["pulse"]))
        points = [
            (shard["x"], shard["y"] - size),
            (shard["x"] + size * 0.7, shard["y"]),
            (shard["x"], shard["y"] + size),
            (shard["x"] - size * 0.7, shard["y"]),
        ]
        shard_rect = pygame.Rect(int(shard["x"] - 20), int(shard["y"] - 20), 40, 40)
        draw_glow_rect(screen, shard_rect, MINT, border_radius=14, glow=12, width=1)
        pygame.draw.polygon(screen, MINT, points)

    for car in state["traffic"]:
        draw_car(screen, int(car["x"]), int(car["y"]), (35, 44, 66), car["color"])

    if not state["game_over"]:
        for i in range(6):
            flame = pygame.Rect(0, 0, 10, 28 + i * 2)
            flame.center = (int(state["x"]) + random.randint(-10, 10), HEIGHT - 76 + i * 6)
            pygame.draw.ellipse(screen, (255, 130 + i * 15, 40, 100), flame)
    player_color = (55, 65, 98) if state["cooldown"] % 8 < 4 else (120, 80, 100)
    draw_car(screen, int(state["x"]), HEIGHT - 130, player_color, PINK)

    title = title_font.render("NEON DRIFT", True, WHITE)
    screen.blit(title, (36, 28))
    subtitle = ui_font.render("Dodge traffic, collect shards, hold SPACE for boost", True, CYAN)
    screen.blit(subtitle, (40, 92))

    draw_panel(
        screen,
        pygame.Rect(36, 132, 240, 124),
        "STATUS",
        [
            f"Score   {state['score']:06d}",
            f"Combo   x{state['combo']}",
            f"Best    x{state['best_combo']}",
        ],
    )
    draw_panel(
        screen,
        pygame.Rect(36, 276, 240, 132),
        "SYSTEM",
        [
            f"Shield  {max(0, state['shield'])}%",
            f"Boost   {int(state['boost'])}%",
            f"Speed   {state['speed']:.2f}x",
        ],
    )

    shield_rect = pygame.Rect(48, 452, 216, 14)
    boost_rect = pygame.Rect(48, 506, 216, 14)
    pygame.draw.rect(screen, (40, 46, 72), shield_rect, border_radius=7)
    pygame.draw.rect(screen, (40, 46, 72), boost_rect, border_radius=7)
    pygame.draw.rect(screen, RED, (shield_rect.x, shield_rect.y, int(shield_rect.width * max(0, state["shield"]) / 100), shield_rect.height), border_radius=7)
    pygame.draw.rect(screen, CYAN, (boost_rect.x, boost_rect.y, int(boost_rect.width * state["boost"] / 100), boost_rect.height), border_radius=7)
    screen.blit(small_font.render("Shield", True, WHITE), (48, 430))
    screen.blit(small_font.render("Boost", True, WHITE), (48, 484))

    if state["game_over"]:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 18, 190))
        screen.blit(overlay, (0, 0))
        game_over = title_font.render("SIGNAL LOST", True, WHITE)
        info = stat_font.render(f"Score {state['score']:06d}", True, CYAN)
        retry = ui_font.render("Press R to restart or ESC to quit", True, WHITE)
        screen.blit(game_over, game_over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        screen.blit(info, info.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
        screen.blit(retry, retry.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 72)))

    pygame.display.flip()

pygame.quit()
sys.exit()
