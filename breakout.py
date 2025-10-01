import pygame
import sys

# 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ブロック崩し")

# 色定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# パドル
paddle_width, paddle_height = 100, 15
paddle_x = WIDTH // 2 - paddle_width // 2
paddle_y = HEIGHT - 40
paddle_speed = 8

# ボール
ball_size = 10
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_dx = 4
ball_dy = -4

# ブロック
block_width, block_height = 75, 25
blocks = []
colors = [RED, ORANGE, YELLOW, GREEN, BLUE]

for row in range(5):
    for col in range(10):
        block_x = col * (block_width + 5) + 35
        block_y = row * (block_height + 5) + 50
        blocks.append(pygame.Rect(block_x, block_y, block_width, block_height))

# ゲーム変数
score = 0
lives = 3
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# ゲームループ
running = True
game_over = False
win = False

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over and not win:
        # パドル操作
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle_x > 0:
            paddle_x -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle_x < WIDTH - paddle_width:
            paddle_x += paddle_speed

        # ボール移動
        ball_x += ball_dx
        ball_y += ball_dy

        # 壁との衝突
        if ball_x <= 0 or ball_x >= WIDTH - ball_size:
            ball_dx = -ball_dx
        if ball_y <= 0:
            ball_dy = -ball_dy

        # パドルとの衝突
        paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
        ball_rect = pygame.Rect(ball_x, ball_y, ball_size, ball_size)

        if ball_rect.colliderect(paddle_rect) and ball_dy > 0:
            ball_dy = -ball_dy
            # パドルのどこに当たったかで角度を変える
            hit_pos = (ball_x - paddle_x) / paddle_width
            ball_dx = (hit_pos - 0.5) * 10

        # ブロックとの衝突
        for block in blocks[:]:
            if ball_rect.colliderect(block):
                blocks.remove(block)
                ball_dy = -ball_dy
                score += 10
                break

        # ボールが下に落ちた
        if ball_y > HEIGHT:
            lives -= 1
            if lives > 0:
                ball_x = WIDTH // 2
                ball_y = HEIGHT // 2
                ball_dx = 4
                ball_dy = -4
            else:
                game_over = True

        # 全ブロック破壊
        if len(blocks) == 0:
            win = True

    # 描画
    screen.fill(BLACK)

    # ブロック描画
    for i, block in enumerate(blocks):
        color = colors[i // 10 % len(colors)]
        pygame.draw.rect(screen, color, block)

    # パドル描画
    pygame.draw.rect(screen, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))

    # ボール描画
    pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_size)

    # スコアとライフ表示
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WIDTH - 150, 10))

    # ゲームオーバー/クリア表示
    if game_over:
        game_over_text = font.render("GAME OVER - Press ESC to quit", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 250, HEIGHT // 2))
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            running = False

    if win:
        win_text = font.render("YOU WIN! - Press ESC to quit", True, GREEN)
        screen.blit(win_text, (WIDTH // 2 - 220, HEIGHT // 2))
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            running = False

    pygame.display.flip()

pygame.quit()
sys.exit()
