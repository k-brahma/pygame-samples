import pygame
import sys
import random

# 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("スネークゲーム")

# 色定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 200, 0)

# スネーク
snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
direction = (1, 0)  # 右方向
next_direction = (1, 0)

# 餌
def spawn_food():
    while True:
        food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if food not in snake:
            return food

food = spawn_food()

# ゲーム変数
score = 0
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
game_over = False

# ゲームループ
running = True
frame_count = 0

while running:
    clock.tick(15)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_UP and direction != (0, 1):
                    next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    next_direction = (1, 0)
            if game_over and event.key == pygame.K_ESCAPE:
                running = False

    if not game_over:
        direction = next_direction

        # 新しい頭の位置
        head_x, head_y = snake[0]
        new_head = (head_x + direction[0], head_y + direction[1])

        # 壁との衝突チェック
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            game_over = True

        # 自分自身との衝突チェック
        if new_head in snake:
            game_over = True

        if not game_over:
            snake.insert(0, new_head)

            # 餌を食べたかチェック
            if new_head == food:
                score += 10
                food = spawn_food()
            else:
                snake.pop()

    # 描画
    screen.fill(BLACK)

    # グリッド線を描画（オプション）
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (30, 30, 30), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (30, 30, 30), (0, y), (WIDTH, y))

    # スネーク描画
    for i, segment in enumerate(snake):
        color = GREEN if i == 0 else DARK_GREEN
        pygame.draw.rect(screen, color,
                        (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE,
                         GRID_SIZE - 2, GRID_SIZE - 2))

    # 餌描画
    pygame.draw.rect(screen, RED,
                    (food[0] * GRID_SIZE, food[1] * GRID_SIZE,
                     GRID_SIZE - 2, GRID_SIZE - 2))

    # スコア表示
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # ゲームオーバー表示
    if game_over:
        game_over_text = font.render("GAME OVER!", True, RED)
        restart_text = font.render("Press ESC to quit", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))
        screen.blit(restart_text, (WIDTH // 2 - 130, HEIGHT // 2 + 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
