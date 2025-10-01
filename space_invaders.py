import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Game settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
ALIEN_SPEED = 1
ALIEN_DROP_SPEED = 40
ALIEN_BULLET_SPEED = 3

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 30)
        self.speed = PLAYER_SPEED

    def move_left(self):
        if self.rect.left > 0:
            self.rect.x -= self.speed

    def move_right(self):
        if self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def draw(self, screen):
        # Draw simple spaceship shape
        points = [
            (self.rect.centerx, self.rect.top),
            (self.rect.left, self.rect.bottom),
            (self.rect.centerx - 10, self.rect.bottom - 10),
            (self.rect.centerx + 10, self.rect.bottom - 10),
            (self.rect.right, self.rect.bottom)
        ]
        pygame.draw.polygon(screen, GREEN, points)

class Alien:
    def __init__(self, x, y, alien_type=0):
        self.rect = pygame.Rect(x, y, 30, 20)
        self.alien_type = alien_type
        self.direction = 1

    def update(self):
        self.rect.x += ALIEN_SPEED * self.direction

    def drop_down(self):
        self.rect.y += ALIEN_DROP_SPEED

    def draw(self, screen):
        color = WHITE if self.alien_type == 0 else YELLOW if self.alien_type == 1 else RED
        # Draw simple alien shape
        pygame.draw.rect(screen, color, self.rect)
        # Draw eyes
        pygame.draw.circle(screen, BLACK, (self.rect.left + 8, self.rect.centery), 3)
        pygame.draw.circle(screen, BLACK, (self.rect.right - 8, self.rect.centery), 3)

class Bullet:
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x, y, 3, 10)
        self.speed = speed

    def update(self):
        self.rect.y -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

class AlienBullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 3, 10)
        self.speed = ALIEN_BULLET_SPEED

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

class Bunker:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 60
        self.rect = pygame.Rect(x, y, self.width, self.height)
        # Create a 2D array representing bunker pixels (1 = intact, 0 = destroyed)
        self.pixels = [[1 for _ in range(self.width)] for _ in range(self.height)]
        self.create_bunker_shape()

    def create_bunker_shape(self):
        # Create bunker shape (dome-like structure)
        for y in range(self.height):
            for x in range(self.width):
                # Create dome shape
                if y < 20:
                    # Top part - rounded
                    center_x = self.width // 2
                    dist_from_center = abs(x - center_x)
                    if dist_from_center > 40 - y:
                        self.pixels[y][x] = 0
                elif y > 40:
                    # Bottom part - entrance
                    if 25 < x < 55:
                        self.pixels[y][x] = 0

    def take_damage(self, impact_rect, is_from_above=True):
        # Create damage around impact point
        damage_radius = 8
        impact_x = impact_rect.centerx - self.x
        impact_y = impact_rect.centery - self.y

        for dy in range(-damage_radius, damage_radius + 1):
            for dx in range(-damage_radius, damage_radius + 1):
                px = impact_x + dx
                py = impact_y + dy
                if 0 <= px < self.width and 0 <= py < self.height:
                    # Circular damage pattern
                    if dx*dx + dy*dy <= damage_radius*damage_radius:
                        self.pixels[py][px] = 0

    def check_collision(self, rect):
        # Check if rect collides with any intact part of bunker
        if not self.rect.colliderect(rect):
            return False

        # Check pixel-level collision
        rel_x = rect.centerx - self.x
        rel_y = rect.centery - self.y

        if 0 <= rel_x < self.width and 0 <= rel_y < self.height:
            return self.pixels[rel_y][rel_x] == 1
        return False

    def draw(self, screen):
        # Draw bunker pixels
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x] == 1:
                    pygame.draw.rect(screen, GREEN,
                                   (self.x + x, self.y + y, 1, 1))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 60)
        self.bullets = []
        self.alien_bullets = []
        self.aliens = []
        self.bunkers = []
        self.create_alien_fleet()
        self.create_bunkers()
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_won = False
        self.alien_direction = 1
        self.last_alien_shot = 0

    def create_alien_fleet(self):
        # Create grid of aliens
        for row in range(5):
            for col in range(11):
                x = 75 + col * 50
                y = 50 + row * 40
                alien_type = 0 if row < 2 else 1 if row < 4 else 2
                self.aliens.append(Alien(x, y, alien_type))

    def create_bunkers(self):
        # Create 4 bunkers evenly spaced
        bunker_count = 4
        bunker_spacing = SCREEN_WIDTH // (bunker_count + 1)
        for i in range(bunker_count):
            x = bunker_spacing * (i + 1) - 40  # Center bunkers
            y = SCREEN_HEIGHT - 180
            self.bunkers.append(Bunker(x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over and not self.game_won:
                    if len(self.bullets) < 3:  # Limit bullets on screen
                        bullet = Bullet(self.player.rect.centerx, self.player.rect.top, BULLET_SPEED)
                        self.bullets.append(bullet)
                elif event.key == pygame.K_r and (self.game_over or self.game_won):
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True

    def update(self):
        if self.game_over or self.game_won:
            return

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move_left()
        if keys[pygame.K_RIGHT]:
            self.player.move_right()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)

        # Update alien bullets
        for bullet in self.alien_bullets[:]:
            bullet.update()
            if bullet.rect.top > SCREEN_HEIGHT:
                self.alien_bullets.remove(bullet)

        # Check if aliens should drop down
        should_drop = False
        for alien in self.aliens:
            if alien.rect.left <= 0 or alien.rect.right >= SCREEN_WIDTH:
                should_drop = True
                break

        if should_drop:
            self.alien_direction *= -1
            for alien in self.aliens:
                alien.direction = self.alien_direction
                alien.drop_down()

        # Update aliens
        for alien in self.aliens:
            alien.update()

        # Alien shooting
        current_time = pygame.time.get_ticks()
        if current_time - self.last_alien_shot > random.randint(500, 2000):
            if self.aliens:
                shooting_alien = random.choice(self.aliens)
                bullet = AlienBullet(shooting_alien.rect.centerx, shooting_alien.rect.bottom)
                self.alien_bullets.append(bullet)
                self.last_alien_shot = current_time

        # Check collisions - player bullets with bunkers
        for bullet in self.bullets[:]:
            for bunker in self.bunkers:
                if bunker.check_collision(bullet.rect):
                    bunker.take_damage(bullet.rect, is_from_above=True)
                    self.bullets.remove(bullet)
                    break

        # Check collisions - alien bullets with bunkers
        for bullet in self.alien_bullets[:]:
            for bunker in self.bunkers:
                if bunker.check_collision(bullet.rect):
                    bunker.take_damage(bullet.rect, is_from_above=False)
                    self.alien_bullets.remove(bullet)
                    break

        # Check collisions - player bullets hitting aliens
        for bullet in self.bullets[:]:
            for alien in self.aliens[:]:
                if bullet.rect.colliderect(alien.rect):
                    self.bullets.remove(bullet)
                    self.aliens.remove(alien)
                    # Score based on alien type
                    if alien.alien_type == 0:
                        self.score += 10
                    elif alien.alien_type == 1:
                        self.score += 20
                    else:
                        self.score += 30
                    break

        # Check collisions - alien bullets hitting player
        for bullet in self.alien_bullets[:]:
            if bullet.rect.colliderect(self.player.rect):
                self.alien_bullets.remove(bullet)
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True

        # Check collisions - aliens with bunkers (destroy bunker parts)
        for alien in self.aliens:
            for bunker in self.bunkers:
                if bunker.rect.colliderect(alien.rect):
                    bunker.take_damage(alien.rect, is_from_above=False)

        # Check if aliens reached player
        for alien in self.aliens:
            if alien.rect.bottom >= self.player.rect.top:
                self.game_over = True
                break

        # Check win condition
        if not self.aliens:
            self.game_won = True

    def draw(self):
        self.screen.fill(BLACK)

        if not self.game_over and not self.game_won:
            # Draw game objects
            self.player.draw(self.screen)

            for bullet in self.bullets:
                bullet.draw(self.screen)

            for bullet in self.alien_bullets:
                bullet.draw(self.screen)

            for alien in self.aliens:
                alien.draw(self.screen)

            for bunker in self.bunkers:
                bunker.draw(self.screen)

            # Draw score and lives
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))

        elif self.game_over:
            # Game over screen
            game_over_text = self.font.render("GAME OVER", True, RED)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)

            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))

            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)

        elif self.game_won:
            # Victory screen
            win_text = self.font.render("YOU WIN!", True, GREEN)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)

            text_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))

            self.screen.blit(win_text, text_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()