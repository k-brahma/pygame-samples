import pygame
import sys
import random

# 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("シューティングゲーム")

# 色定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)

# プレイヤー
player_width, player_height = 40, 50
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 20
player_speed = 6

# 弾丸
bullets = []
bullet_width, bullet_height = 5, 15
bullet_speed = 10
shoot_cooldown = 0

# 敵
enemies = []
enemy_width, enemy_height = 40, 40
enemy_speed = 2
spawn_timer = 0
spawn_interval = 60

# ゲーム変数
score = 0
lives = 3
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
game_over = False
level = 1

# 星（背景）
stars = []
for _ in range(50):
    stars.append({
        'x': random.randint(0, WIDTH),
        'y': random.randint(0, HEIGHT),
        'speed': random.uniform(1, 3)
    })

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
        if keys[pygame.K_UP] and player_y > HEIGHT // 2:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < HEIGHT - player_height:
            player_y += player_speed

        # 射撃
        shoot_cooldown -= 1
        if keys[pygame.K_SPACE] and shoot_cooldown <= 0:
            bullets.append({
                'x': player_x + player_width // 2 - bullet_width // 2,
                'y': player_y
            })
            shoot_cooldown = 15

        # レベルアップ
        level = score // 200 + 1
        current_enemy_speed = enemy_speed + (level - 1) * 0.3
        spawn_interval = max(30, 60 - (level - 1) * 5)

        # 敵生成
        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            enemy_x = random.randint(0, WIDTH - enemy_width)
            enemies.append({
                'x': enemy_x,
                'y': -enemy_height,
                'speed': current_enemy_speed + random.uniform(-0.5, 0.5)
            })

        # 弾丸移動
        for bullet in bullets[:]:
            bullet['y'] -= bullet_speed
            if bullet['y'] < 0:
                bullets.remove(bullet)

        # 敵移動
        for enemy in enemies[:]:
            enemy['y'] += enemy['speed']

            # プレイヤーとの衝突
            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            enemy_rect = pygame.Rect(enemy['x'], enemy['y'], enemy_width, enemy_height)

            if player_rect.colliderect(enemy_rect):
                lives -= 1
                enemies.remove(enemy)
                if lives <= 0:
                    game_over = True
            # 画面外に出た
            elif enemy['y'] > HEIGHT:
                enemies.remove(enemy)

        # 弾丸と敵の衝突チェック
        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(bullet['x'], bullet['y'], bullet_width, bullet_height)
            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy['x'], enemy['y'], enemy_width, enemy_height)
                if bullet_rect.colliderect(enemy_rect):
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if enemy in enemies:
                        enemies.remove(enemy)
                    score += 10
                    break

        # 星の移動
        for star in stars:
            star['y'] += star['speed']
            if star['y'] > HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, WIDTH)

    # 描画
    screen.fill(BLACK)

    # 星描画
    for star in stars:
        pygame.draw.circle(screen, WHITE, (int(star['x']), int(star['y'])), 1)

    # プレイヤー描画（宇宙船風）
    pygame.draw.polygon(screen, BLUE, [
        (player_x + player_width // 2, player_y),
        (player_x, player_y + player_height),
        (player_x + player_width // 2, player_y + player_height - 10),
        (player_x + player_width, player_y + player_height)
    ])
    # エンジン炎
    if not game_over:
        flame_y = player_y + player_height + random.randint(0, 5)
        pygame.draw.polygon(screen, ORANGE, [
            (player_x + player_width // 2 - 5, player_y + player_height),
            (player_x + player_width // 2, flame_y),
            (player_x + player_width // 2 + 5, player_y + player_height)
        ])

    # 弾丸描画
    for bullet in bullets:
        pygame.draw.rect(screen, YELLOW, (bullet['x'], bullet['y'], bullet_width, bullet_height))

    # 敵描画
    for enemy in enemies:
        pygame.draw.rect(screen, RED, (enemy['x'], enemy['y'], enemy_width, enemy_height))
        # 敵の目
        pygame.draw.circle(screen, YELLOW, (int(enemy['x'] + 12), int(enemy['y'] + 15)), 5)
        pygame.draw.circle(screen, YELLOW, (int(enemy['x'] + 28), int(enemy['y'] + 15)), 5)

    # UI表示
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))
    screen.blit(level_text, (WIDTH - 150, 10))

    # 操作説明
    help_text = small_font.render("Arrow keys: Move | Space: Shoot", True, WHITE)
    screen.blit(help_text, (WIDTH // 2 - 150, HEIGHT - 25))

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
