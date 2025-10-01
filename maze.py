import pygame
import sys
import random

# 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("迷路脱出ゲーム")

# 色定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (100, 150, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

# グリッド設定
GRID_SIZE = 40
COLS = WIDTH // GRID_SIZE
ROWS = HEIGHT // GRID_SIZE

# 迷路生成（簡易版）
def generate_maze():
    # 0: 通路, 1: 壁
    maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]

    # ランダムウォークで迷路生成
    def carve_path(x, y):
        maze[y][x] = 0
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0
                carve_path(nx, ny)

    carve_path(1, 1)

    # スタートとゴールを確保
    maze[1][1] = 0
    maze[ROWS - 2][COLS - 2] = 0

    # スタートとゴール周辺を確保
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if 0 <= 1 + dy < ROWS and 0 <= 1 + dx < COLS:
                maze[1 + dy][1 + dx] = 0
            if 0 <= ROWS - 2 + dy < ROWS and 0 <= COLS - 2 + dx < COLS:
                maze[ROWS - 2 + dy][COLS - 2 + dx] = 0

    return maze

maze = generate_maze()

# プレイヤー
player_x, player_y = 1, 1
player_speed = GRID_SIZE

# ゴール
goal_x, goal_y = COLS - 2, ROWS - 2

# ゲーム変数
clock = pygame.time.Clock()
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 24)
game_clear = False
move_cooldown = 0

# タイマー
start_ticks = pygame.time.get_ticks()

# ゲームループ
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_clear and event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r:
                # リスタート
                maze = generate_maze()
                player_x, player_y = 1, 1
                game_clear = False
                start_ticks = pygame.time.get_ticks()

    if not game_clear:
        move_cooldown -= 1

        # プレイヤー移動（グリッドベース）
        if move_cooldown <= 0:
            keys = pygame.key.get_pressed()
            new_x, new_y = player_x, player_y

            if keys[pygame.K_UP]:
                new_y -= 1
                move_cooldown = 8
            elif keys[pygame.K_DOWN]:
                new_y += 1
                move_cooldown = 8
            elif keys[pygame.K_LEFT]:
                new_x -= 1
                move_cooldown = 8
            elif keys[pygame.K_RIGHT]:
                new_x += 1
                move_cooldown = 8

            # 壁チェック
            if 0 <= new_x < COLS and 0 <= new_y < ROWS:
                if maze[new_y][new_x] == 0:
                    player_x, player_y = new_x, new_y

        # ゴール判定
        if player_x == goal_x and player_y == goal_y:
            game_clear = True

    # 経過時間計算
    if not game_clear:
        elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000

    # 描画
    screen.fill(BLACK)

    # 迷路描画
    for row in range(ROWS):
        for col in range(COLS):
            x = col * GRID_SIZE
            y = row * GRID_SIZE

            if maze[row][col] == 1:
                # 壁
                pygame.draw.rect(screen, GRAY, (x, y, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, WHITE, (x, y, GRID_SIZE, GRID_SIZE), 1)
            else:
                # 通路
                pygame.draw.rect(screen, BLACK, (x, y, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, (30, 30, 30), (x, y, GRID_SIZE, GRID_SIZE), 1)

    # ゴール描画（光る効果）
    glow_size = GRID_SIZE - 10 + int(5 * abs(pygame.time.get_ticks() % 1000 - 500) / 250)
    goal_center_x = goal_x * GRID_SIZE + GRID_SIZE // 2
    goal_center_y = goal_y * GRID_SIZE + GRID_SIZE // 2
    pygame.draw.circle(screen, YELLOW, (goal_center_x, goal_center_y), glow_size // 2)
    pygame.draw.circle(screen, GREEN, (goal_center_x, goal_center_y), GRID_SIZE // 3)

    # プレイヤー描画
    player_center_x = player_x * GRID_SIZE + GRID_SIZE // 2
    player_center_y = player_y * GRID_SIZE + GRID_SIZE // 2
    pygame.draw.circle(screen, BLUE, (player_center_x, player_center_y), GRID_SIZE // 3)
    # 目
    pygame.draw.circle(screen, WHITE, (player_center_x - 5, player_center_y - 3), 3)
    pygame.draw.circle(screen, WHITE, (player_center_x + 5, player_center_y - 3), 3)

    # UI表示
    if not game_clear:
        time_text = small_font.render(f"Time: {elapsed_time}s", True, WHITE)
        screen.blit(time_text, (10, 10))

    help_text = small_font.render("Arrow keys: Move | R: Restart", True, WHITE)
    screen.blit(help_text, (10, HEIGHT - 25))

    # ゴール表示
    goal_hint = small_font.render("Reach the yellow goal!", True, YELLOW)
    screen.blit(goal_hint, (WIDTH - 200, 10))

    # ゲームクリア表示
    if game_clear:
        clear_text = font.render("GOAL!", True, GREEN)
        time_result = font.render(f"Time: {elapsed_time}s", True, WHITE)
        restart_text = small_font.render("Press R to restart | ESC to quit", True, WHITE)
        screen.blit(clear_text, (WIDTH // 2 - 80, HEIGHT // 2 - 60))
        screen.blit(time_result, (WIDTH // 2 - 100, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - 150, HEIGHT // 2 + 60))

    pygame.display.flip()

pygame.quit()
sys.exit()
