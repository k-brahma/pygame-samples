import pygame
import sys
import random

# 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("フラッピーバード")

# 色定義
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
BROWN = (139, 69, 19)

# 鳥
bird_x = 80
bird_y = HEIGHT // 2
bird_radius = 15
bird_velocity = 0
gravity = 0.5
jump_strength = -9

# パイプ
pipes = []
pipe_width = 60
pipe_gap = 150
pipe_speed = 3
spawn_timer = 0
spawn_interval = 90

def create_pipe():
    gap_y = random.randint(150, HEIGHT - 150 - pipe_gap)
    return {
        'x': WIDTH,
        'gap_y': gap_y,
        'passed': False
    }

# 初期パイプ
pipes.append(create_pipe())

# ゲーム変数
score = 0
high_score = 0
clock = pygame.time.Clock()
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 24)
game_over = False
game_started = False

# ゲームループ
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_started:
                    game_started = True
                if not game_over:
                    bird_velocity = jump_strength
                else:
                    # リスタート
                    bird_y = HEIGHT // 2
                    bird_velocity = 0
                    pipes = [create_pipe()]
                    score = 0
                    game_over = False
                    game_started = False
            if event.key == pygame.K_ESCAPE and game_over:
                running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not game_started:
                game_started = True
            if not game_over:
                bird_velocity = jump_strength

    if game_started and not game_over:
        # 鳥の物理演算
        bird_velocity += gravity
        bird_y += bird_velocity

        # 地面・天井との衝突
        if bird_y - bird_radius <= 0 or bird_y + bird_radius >= HEIGHT:
            game_over = True
            high_score = max(high_score, score)

        # パイプ生成
        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            pipes.append(create_pipe())

        # パイプ移動
        for pipe in pipes[:]:
            pipe['x'] -= pipe_speed

            # スコア加算
            if not pipe['passed'] and pipe['x'] + pipe_width < bird_x:
                pipe['passed'] = True
                score += 1

            # 画面外のパイプ削除
            if pipe['x'] < -pipe_width:
                pipes.remove(pipe)

            # 衝突判定
            bird_rect = pygame.Rect(bird_x - bird_radius, bird_y - bird_radius,
                                   bird_radius * 2, bird_radius * 2)

            # 上のパイプ
            top_pipe_rect = pygame.Rect(pipe['x'], 0, pipe_width, pipe['gap_y'])
            # 下のパイプ
            bottom_pipe_rect = pygame.Rect(pipe['x'], pipe['gap_y'] + pipe_gap,
                                          pipe_width, HEIGHT - (pipe['gap_y'] + pipe_gap))

            if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect):
                game_over = True
                high_score = max(high_score, score)

    # 描画
    screen.fill(SKY_BLUE)

    # パイプ描画
    for pipe in pipes:
        # 上のパイプ
        pygame.draw.rect(screen, GREEN, (pipe['x'], 0, pipe_width, pipe['gap_y']))
        pygame.draw.rect(screen, DARK_GREEN, (pipe['x'], 0, pipe_width, pipe['gap_y']), 3)
        # パイプの端
        pygame.draw.rect(screen, DARK_GREEN,
                        (pipe['x'] - 5, pipe['gap_y'] - 20, pipe_width + 10, 20))

        # 下のパイプ
        pygame.draw.rect(screen, GREEN,
                        (pipe['x'], pipe['gap_y'] + pipe_gap, pipe_width,
                         HEIGHT - (pipe['gap_y'] + pipe_gap)))
        pygame.draw.rect(screen, DARK_GREEN,
                        (pipe['x'], pipe['gap_y'] + pipe_gap, pipe_width,
                         HEIGHT - (pipe['gap_y'] + pipe_gap)), 3)
        # パイプの端
        pygame.draw.rect(screen, DARK_GREEN,
                        (pipe['x'] - 5, pipe['gap_y'] + pipe_gap, pipe_width + 10, 20))

    # 地面
    pygame.draw.rect(screen, BROWN, (0, HEIGHT - 50, WIDTH, 50))

    # 鳥描画
    pygame.draw.circle(screen, YELLOW, (bird_x, int(bird_y)), bird_radius)
    # 目
    eye_x = bird_x + 5
    eye_y = int(bird_y) - 3
    pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 5)
    pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 2)
    # くちばし
    beak_points = [
        (bird_x + bird_radius, int(bird_y)),
        (bird_x + bird_radius + 8, int(bird_y) - 3),
        (bird_x + bird_radius + 8, int(bird_y) + 3)
    ]
    pygame.draw.polygon(screen, (255, 165, 0), beak_points)

    # スコア表示
    score_text = font.render(str(score), True, WHITE)
    score_shadow = font.render(str(score), True, BLACK)
    screen.blit(score_shadow, (WIDTH // 2 - 15 + 2, 52))
    screen.blit(score_text, (WIDTH // 2 - 15, 50))

    # スタート画面
    if not game_started:
        start_text = small_font.render("Press SPACE or Click to Start", True, WHITE)
        start_shadow = small_font.render("Press SPACE or Click to Start", True, BLACK)
        screen.blit(start_shadow, (WIDTH // 2 - 135 + 2, HEIGHT // 2 + 2))
        screen.blit(start_text, (WIDTH // 2 - 135, HEIGHT // 2))

    # ゲームオーバー表示
    if game_over:
        game_over_text = font.render("GAME OVER", True, WHITE)
        game_over_shadow = font.render("GAME OVER", True, BLACK)
        screen.blit(game_over_shadow, (WIDTH // 2 - 110 + 2, HEIGHT // 2 - 50 + 2))
        screen.blit(game_over_text, (WIDTH // 2 - 110, HEIGHT // 2 - 50))

        final_score_text = small_font.render(f"Score: {score}", True, WHITE)
        screen.blit(final_score_text, (WIDTH // 2 - 50, HEIGHT // 2))

        high_score_text = small_font.render(f"High Score: {high_score}", True, WHITE)
        screen.blit(high_score_text, (WIDTH // 2 - 70, HEIGHT // 2 + 30))

        restart_text = small_font.render("SPACE: Restart | ESC: Quit", True, WHITE)
        screen.blit(restart_text, (WIDTH // 2 - 120, HEIGHT // 2 + 70))

    pygame.display.flip()

pygame.quit()
sys.exit()
