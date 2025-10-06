import pygame
import math
import sys
import random

# Initialize
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kawaii Kaleidoscope ✨")

# Color palettes
vivid_colors = [
    (255, 0, 0),      # Red
    (255, 165, 0),    # Orange
    (255, 255, 0),    # Yellow
    (0, 255, 0),      # Green
    (0, 255, 255),    # Cyan
    (0, 0, 255),      # Blue
    (255, 0, 255),    # Magenta
    (255, 255, 255),  # White
]

pastel_colors = [
    (255, 182, 193),  # Light Pink
    (255, 218, 185),  # Peach
    (255, 253, 208),  # Cream
    (200, 255, 200),  # Mint
    (173, 216, 230),  # Light Blue
    (221, 160, 221),  # Plum
    (255, 240, 245),  # Lavender Blush
    (255, 228, 225),  # Misty Rose
]

rainbow_colors = [
    (255, 0, 127),    # Pink
    (255, 0, 0),      # Red
    (255, 127, 0),    # Orange
    (255, 255, 0),    # Yellow
    (0, 255, 0),      # Green
    (0, 255, 255),    # Cyan
    (0, 0, 255),      # Blue
    (127, 0, 255),    # Purple
]

# Background colors
bg_colors = [
    (0, 0, 0),        # Black
    (255, 255, 255),  # White
    (250, 240, 255),  # Lavender
    (240, 255, 255),  # Azure
    (255, 250, 240),  # Floral White
]

# Settings
segments = 12  # Number of kaleidoscope segments
center_x, center_y = WIDTH // 2, HEIGHT // 2
current_color_index = 0
colors = pastel_colors  # Start with pastel colors
current_color = colors[current_color_index]
brush_size = 3
current_bg_index = 0
current_bg = bg_colors[current_bg_index]
rainbow_mode = False
rainbow_hue = 0
shape_mode = 0  # 0: circle, 1: star, 2: heart
sparkle_mode = False

# Drawing surface
drawing_surface = pygame.Surface((WIDTH, HEIGHT))
drawing_surface.fill(current_bg)

# Font
font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 18)

def rotate_point(x, y, cx, cy, angle):
    """Rotate a point around a center"""
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    
    # Move to origin
    temp_x = x - cx
    temp_y = y - cy
    
    # Rotate
    rotated_x = temp_x * cos_angle - temp_y * sin_angle
    rotated_y = temp_x * sin_angle + temp_y * cos_angle
    
    # Move back
    final_x = rotated_x + cx
    final_y = rotated_y + cy
    
    return int(final_x), int(final_y)

def mirror_point(x, y, cx, cy, angle):
    """Mirror a point across an axis"""
    # Axis direction vector
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    
    # Relative coordinates from center
    dx = x - cx
    dy = y - cy
    
    # Mirror reflection calculation
    cos_2angle = math.cos(2 * angle)
    sin_2angle = math.sin(2 * angle)
    
    mirrored_dx = dx * cos_2angle + dy * sin_2angle
    mirrored_dy = dx * sin_2angle - dy * cos_2angle
    
    return int(mirrored_dx + cx), int(mirrored_dy + cy)

def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB"""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))

def draw_star(surface, x, y, size, color):
    """Draw a star"""
    points = []
    for i in range(5):
        angle = i * 4 * math.pi / 5 - math.pi / 2
        points.append((x + size * math.cos(angle), y + size * math.sin(angle)))
    if len(points) >= 3:
        pygame.draw.polygon(surface, color, points)

def draw_heart(surface, x, y, size, color):
    """Draw a heart"""
    # Simple heart approximation using circles and polygon
    for dx in range(-size, size + 1):
        for dy in range(-size, size + 1):
            # Heart equation
            x_norm = dx / size
            y_norm = dy / size
            if (x_norm**2 + y_norm**2 - 1)**3 - x_norm**2 * y_norm**3 < 0:
                px, py = x + dx, y - dy
                if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                    surface.set_at((int(px), int(py)), color)

def draw_shape(surface, x, y, size, color, mode):
    """Draw shape based on mode"""
    if mode == 0:  # Circle
        pygame.draw.circle(surface, color, (x, y), size)
    elif mode == 1:  # Star
        draw_star(surface, x, y, size, color)
    elif mode == 2:  # Heart
        draw_heart(surface, x, y, size, color)

def draw_kaleidoscope_point(surface, x, y, color, size):
    """Draw a point in kaleidoscope pattern"""
    angle_step = 2 * math.pi / segments
    
    for i in range(segments):
        angle = i * angle_step
        
        # Rotation
        rot_x, rot_y = rotate_point(x, y, center_x, center_y, angle)
        draw_shape(surface, rot_x, rot_y, size, color, shape_mode)
        
        # Mirror reflection
        mir_x, mir_y = mirror_point(x, y, center_x, center_y, angle)
        draw_shape(surface, mir_x, mir_y, size, color, shape_mode)
    
    # Add sparkles if enabled
    if sparkle_mode:
        for _ in range(3):
            sparkle_x = x + random.randint(-20, 20)
            sparkle_y = y + random.randint(-20, 20)
            sparkle_size = random.randint(1, 2)
            sparkle_color = (255, 255, 255) if current_bg_index == 0 else (255, 255, 0)
            
            for i in range(segments):
                angle = i * angle_step
                rot_x, rot_y = rotate_point(sparkle_x, sparkle_y, center_x, center_y, angle)
                pygame.draw.circle(surface, sparkle_color, (rot_x, rot_y), sparkle_size)
                mir_x, mir_y = mirror_point(sparkle_x, sparkle_y, center_x, center_y, angle)
                pygame.draw.circle(surface, sparkle_color, (mir_x, mir_y), sparkle_size)

def draw_line_kaleidoscope(surface, x1, y1, x2, y2, color, size):
    """Draw a line in kaleidoscope pattern"""
    angle_step = 2 * math.pi / segments
    
    # Calculate distance for shapes along the line
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    steps = max(int(dist / (size * 0.5)), 1)
    
    for step in range(steps + 1):
        t = step / steps if steps > 0 else 0
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        
        for i in range(segments):
            angle = i * angle_step
            
            # Rotation
            rot_x, rot_y = rotate_point(x, y, center_x, center_y, angle)
            draw_shape(surface, rot_x, rot_y, size, color, shape_mode)
            
            # Mirror reflection
            mir_x, mir_y = mirror_point(x, y, center_x, center_y, angle)
            draw_shape(surface, mir_x, mir_y, size, color, shape_mode)
        
        # Add sparkles if enabled
        if sparkle_mode and step % 3 == 0:
            for _ in range(2):
                sparkle_x = x + random.randint(-15, 15)
                sparkle_y = y + random.randint(-15, 15)
                sparkle_size = random.randint(1, 2)
                sparkle_color = (255, 255, 255) if current_bg_index == 0 else (255, 255, 0)
                
                for i in range(segments):
                    angle = i * angle_step
                    rot_x, rot_y = rotate_point(sparkle_x, sparkle_y, center_x, center_y, angle)
                    pygame.draw.circle(surface, sparkle_color, (rot_x, rot_y), sparkle_size)
                    mir_x, mir_y = mirror_point(sparkle_x, sparkle_y, center_x, center_y, angle)
                    pygame.draw.circle(surface, sparkle_color, (mir_x, mir_y), sparkle_size)

# Main loop
clock = pygame.time.Clock()
running = True
drawing = False
prev_pos = None

print("=== ✨ Kawaii Kaleidoscope ✨ ===")
print("Controls:")
print("- Mouse drag: Draw")
print("- Space: Change color")
print("- P: Toggle color palette (Pastel/Vivid/Rainbow)")
print("- R: Toggle rainbow mode")
print("- S: Change shape (Circle/Star/Heart)")
print("- K: Toggle sparkles ✨")
print("- B: Change background")
print("- C: Clear screen")
print("- 1-9: Set brush size")
print("- ESC: Exit")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                drawing = True
                prev_pos = event.pos
                draw_color = hsv_to_rgb(rainbow_hue, 1.0, 1.0) if rainbow_mode else current_color
                draw_kaleidoscope_point(drawing_surface, event.pos[0], event.pos[1], 
                                       draw_color, brush_size)
                if rainbow_mode:
                    rainbow_hue = (rainbow_hue + 5) % 360
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
                prev_pos = None
        
        elif event.type == pygame.MOUSEMOTION:
            if drawing and prev_pos:
                draw_color = hsv_to_rgb(rainbow_hue, 1.0, 1.0) if rainbow_mode else current_color
                draw_line_kaleidoscope(drawing_surface, prev_pos[0], prev_pos[1],
                                      event.pos[0], event.pos[1], 
                                      draw_color, brush_size)
                prev_pos = event.pos
                if rainbow_mode:
                    rainbow_hue = (rainbow_hue + 2) % 360
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Change color
                current_color_index = (current_color_index + 1) % len(colors)
                current_color = colors[current_color_index]
                print(f"Color changed: {current_color}")
            
            elif event.key == pygame.K_p:
                # Toggle palette
                if colors == pastel_colors:
                    colors = vivid_colors
                    print("Palette: Vivid")
                elif colors == vivid_colors:
                    colors = rainbow_colors
                    print("Palette: Rainbow")
                else:
                    colors = pastel_colors
                    print("Palette: Pastel")
                current_color_index = 0
                current_color = colors[current_color_index]
            
            elif event.key == pygame.K_r:
                # Toggle rainbow mode
                rainbow_mode = not rainbow_mode
                print(f"Rainbow mode: {'ON ✨' if rainbow_mode else 'OFF'}")
            
            elif event.key == pygame.K_s:
                # Change shape
                shape_mode = (shape_mode + 1) % 3
                shape_names = ["Circle ⭕", "Star ⭐", "Heart ♥"]
                print(f"Shape: {shape_names[shape_mode]}")
            
            elif event.key == pygame.K_k:
                # Toggle sparkles
                sparkle_mode = not sparkle_mode
                print(f"Sparkles: {'ON ✨' if sparkle_mode else 'OFF'}")
            
            elif event.key == pygame.K_b:
                # Change background
                current_bg_index = (current_bg_index + 1) % len(bg_colors)
                current_bg = bg_colors[current_bg_index]
                drawing_surface.fill(current_bg)
                bg_names = ["Black", "White", "Lavender", "Azure", "Floral"]
                print(f"Background: {bg_names[current_bg_index]}")
            
            elif event.key == pygame.K_c:
                # Clear screen
                drawing_surface.fill(current_bg)
                print("Screen cleared")
            
            elif event.key in [pygame.K_1, pygame.K_KP1]:
                brush_size = 1
                print(f"Brush size: {brush_size}")
            elif event.key in [pygame.K_2, pygame.K_KP2]:
                brush_size = 2
                print(f"Brush size: {brush_size}")
            elif event.key in [pygame.K_3, pygame.K_KP3]:
                brush_size = 3
                print(f"Brush size: {brush_size}")
            elif event.key in [pygame.K_4, pygame.K_KP4]:
                brush_size = 4
                print(f"Brush size: {brush_size}")
            elif event.key in [pygame.K_5, pygame.K_KP5]:
                brush_size = 5
                print(f"Brush size: {brush_size}")
            elif event.key in [pygame.K_6, pygame.K_KP6]:
                brush_size = 6
                print(f"Brush size: {brush_size}")
            elif event.key in [pygame.K_7, pygame.K_KP7]:
                brush_size = 7
                print(f"Brush size: {brush_size}")
            elif event.key in [pygame.K_8, pygame.K_KP8]:
                brush_size = 8
                print(f"Brush size: {brush_size}")
            elif event.key in [pygame.K_9, pygame.K_KP9]:
                brush_size = 9
                print(f"Brush size: {brush_size}")
            
            elif event.key == pygame.K_ESCAPE:
                running = False
    
    # Render screen
    screen.blit(drawing_surface, (0, 0))
    
    # Display UI info
    palette_name = "Pastel" if colors == pastel_colors else ("Vivid" if colors == vivid_colors else "Rainbow")
    shape_names = ["Circle", "Star", "Heart"]
    
    # Main info line
    info_text = f"✨ Kawaii Kaleidoscope ✨ | Brush: {brush_size} | Shape: {shape_names[shape_mode]}"
    text_surface = font.render(info_text, True, (255, 255, 255) if current_bg_index == 0 else (50, 50, 50))
    text_bg = pygame.Surface((text_surface.get_width() + 10, text_surface.get_height() + 10))
    text_bg.fill((0, 0, 0) if current_bg_index == 0 else (255, 255, 255))
    text_bg.set_alpha(180)
    screen.blit(text_bg, (5, 5))
    screen.blit(text_surface, (10, 10))
    
    # Status line
    status_parts = []
    status_parts.append(f"Palette: {palette_name}")
    if rainbow_mode:
        status_parts.append("Rainbow Mode ON")
    if sparkle_mode:
        status_parts.append("Sparkles ON")
    status_text = " | ".join(status_parts)
    
    status_surface = small_font.render(status_text, True, (255, 255, 255) if current_bg_index == 0 else (50, 50, 50))
    status_bg = pygame.Surface((status_surface.get_width() + 10, status_surface.get_height() + 10))
    status_bg.fill((0, 0, 0) if current_bg_index == 0 else (255, 255, 255))
    status_bg.set_alpha(180)
    screen.blit(status_bg, (5, 35))
    screen.blit(status_surface, (10, 40))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()