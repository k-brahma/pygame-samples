import pygame
import sys
import random

# 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("落下物キャッチゲーム")

# 色定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (255, 0, 255)

# プレイヤー
player_width, player_height = 60, 60
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_speed = 7

# 落下物
falling_items = []
item_size = 30
item_speed = 3
spawn_timer = 0
spawn_interval = 60  # フレーム数

# アイテムの種類
ITEM_TYPES = [
    {'color': YELLOW, 'points': 10},  # 良いアイテム
    {'color': GREEN, 'points': 20},   # より良いアイテム
    {'color': RED, 'points': -10},    # 悪いアイテム
]

# ゲーム変数
score = 0
lives = 3
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
game_over = False
level = 1

# ゲームループ
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_ESCAPE:
                running = False

    if not game_over:
        # プレイヤー操作
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_speed

        # 落下物生成
        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            item_type = random.choice(ITEM_TYPES)
            item_x = random.randint(0, WIDTH - item_size)
            falling_items.append({
                'x': item_x,
                'y': -item_size,
                'type': item_type
            })

        # レベルアップ（スコアに応じて難易度上昇）
        level = score // 100 + 1
        current_speed = item_speed + (level - 1) * 0.5
        spawn_interval = max(30, 60 - (level - 1) * 5)

        # 落下物移動
        for item in falling_items[:]:
            item['y'] += current_speed

            # プレイヤーとの衝突チェック
            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            item_rect = pygame.Rect(item['x'], item['y'], item_size, item_size)

            if player_rect.colliderect(item_rect):
                points = item['type']['points']
                score += points
                if points < 0:  # 悪いアイテムを取った
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                falling_items.remove(item)
            # 画面外に出た
            elif item['y'] > HEIGHT:
                falling_items.remove(item)

    # 描画
    screen.fill(BLACK)

    # プレイヤー描画
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_width, player_height))
    # プレイヤーの目を描画
    eye_size = 8
    pygame.draw.circle(screen, WHITE, (player_x + 15, player_y + 20), eye_size)
    pygame.draw.circle(screen, WHITE, (player_x + 45, player_y + 20), eye_size)
    pygame.draw.circle(screen, BLACK, (player_x + 15, player_y + 20), eye_size // 2)
    pygame.draw.circle(screen, BLACK, (player_x + 45, player_y + 20), eye_size // 2)

    # 落下物描画
    for item in falling_items:
        if item['type']['color'] == RED:
            # 悪いアイテムは三角形
            points = [
                (item['x'] + item_size // 2, item['y']),
                (item['x'], item['y'] + item_size),
                (item['x'] + item_size, item['y'] + item_size)
            ]
            pygame.draw.polygon(screen, item['type']['color'], points)
        else:
            # 良いアイテムは円
            pygame.draw.circle(screen, item['type']['color'],
                             (item['x'] + item_size // 2, item['y'] + item_size // 2),
                             item_size // 2)

    # UI表示
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))
    screen.blit(level_text, (WIDTH - 150, 10))

    # ゲームオーバー表示
    if game_over:
        game_over_text = font.render("GAME OVER!", True, RED)
        final_score_text = font.render(f"Final Score: {score}", True, WHITE)
        restart_text = font.render("Press ESC to quit", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 60))
        screen.blit(final_score_text, (WIDTH // 2 - 130, HEIGHT // 2 - 10))
        screen.blit(restart_text, (WIDTH // 2 - 130, HEIGHT // 2 + 40))

    pygame.display.flip()

pygame.quit()
sys.exit()
