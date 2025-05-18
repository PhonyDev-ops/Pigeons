import pygame
import math
import random
import time

pygame.init()

# Screen setup
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stone vs Birds")

# Colors and clock
SKY = (135, 206, 235)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
clock = pygame.time.Clock()
FPS = 60

# Physics constants
GRAVITY = 9.8

# Load sprites
boy_img = pygame.image.load("boy.png")
boy_img = pygame.transform.scale(boy_img, (100, 100))

# Load birb animation frames (resize to match bird_img size)
birb_frames = [
    pygame.transform.scale(pygame.image.load('assets/brib_f1.png').convert_alpha(), (50, 40)),
    pygame.transform.scale(pygame.image.load('assets/brib_f2.png').convert_alpha(), (50, 40)),
    pygame.transform.scale(pygame.image.load('assets/brib_f3.png').convert_alpha(), (50, 40)),
    pygame.transform.scale(pygame.image.load('assets/brib_f4.png').convert_alpha(), (50, 40)),
    pygame.transform.scale(pygame.image.load('assets/brib_f5.png').convert_alpha(), (50, 40)),
    pygame.transform.scale(pygame.image.load('assets/brib_f6.png').convert_alpha(), (50, 40)),
    pygame.transform.scale(pygame.image.load('assets/brib_f7.png').convert_alpha(), (50, 40)),
    pygame.transform.scale(pygame.image.load('assets/brib_f8.png').convert_alpha(), (50, 40)),
]

# Load zombieboy animation frames
zombieboy_frames = [
    pygame.image.load('assets/zombieboy1.png').convert_alpha(),
    pygame.image.load('assets/zombieboy2.png').convert_alpha(),
    pygame.image.load('assets/zombieboy3.png').convert_alpha(),
    pygame.image.load('assets/zombieboy4.png').convert_alpha(),
    pygame.image.load('assets/zombieboy5.png').convert_alpha(),
]
zombieboy_frame_index = 0
zombieboy_animating = False
zombieboy_anim_timer = 0
zombieboy_anim_speed = 0.07  # seconds per frame

# Font
font = pygame.font.SysFont('VCR OSD Mono', 36)

# Boy setup
boy_pos = (100, HEIGHT - 120)
stone_radius = 8

# Game variables
angle = 45
velocity = 50
stones = []
birds = []
score = 0
stone_count = 50  # Limited stone count

# Bird class
class Bird:
    def __init__(self):
        self.x = WIDTH
        self.y = random.randint(100, 300)
        self.speed = random.uniform(2, 8)
        self.radius = 20
        self.frame_index = 0
        self.last_anim_time = time.time()
        self.image = birb_frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def move(self):
        self.x -= self.speed
        self.rect.x = int(self.x)
        # Animate birb
        now = time.time()
        if now - self.last_anim_time > 0.08:
            self.frame_index = (self.frame_index + 1) % len(birb_frames)
            self.image = birb_frames[self.frame_index]
            self.last_anim_time = now

    def draw(self):
        screen.blit(self.image, self.rect)

# Projectile class
class Stone:
    def __init__(self, angle, velocity):
        self.x = boy_pos[0] + 75
        self.y = boy_pos[1] + 40
        self.angle = math.radians(angle)
        self.velocity = velocity
        self.time = 0

    def update(self):
        t = self.time
        self.x = boy_pos[0] + 75 + self.velocity * math.cos(self.angle) * t
        self.y = boy_pos[1] + 40 - (self.velocity * math.sin(self.angle) * t - 0.5 * GRAVITY * t ** 2)
        self.time += 0.1

    def draw(self):
        pygame.draw.circle(screen, BROWN, (int(self.x), int(self.y)), stone_radius)

    def is_off_screen(self):
        return self.x > WIDTH or self.y > HEIGHT or self.y < 0

def check_collision(stone, bird):
    dx = stone.x - (bird.x + 25)
    dy = stone.y - (bird.y + 20)
    distance = math.hypot(dx, dy)
    return distance < (stone_radius + bird.radius)

# Main game loop
running = True
bird_spawn_timer = 0

while running:
    screen.fill(SKY)
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        angle = min(angle + 1, 90)
    if keys[pygame.K_DOWN]:
        angle = max(angle - 1, 1)
    if keys[pygame.K_RIGHT]:
        velocity = min(velocity + 1, 150)
    if keys[pygame.K_LEFT]:
        velocity = max(velocity - 1, 10)
    if keys[pygame.K_SPACE]:
        if stone_count > 0 and (len(stones) == 0 or stones[-1].time > 0.5):
            stones.append(Stone(angle, velocity))
            stone_count -= 1
            zombieboy_animating = True
            zombieboy_frame_index = 0
            zombieboy_anim_timer = time.time()

    # Bird logic
    bird_spawn_timer += 1
    if bird_spawn_timer > 90:
        birds.append(Bird())
        bird_spawn_timer = 0

    for bird in birds[:]:
        bird.move()
        bird.draw()
        if bird.x < -50:
            birds.remove(bird)

    # Stone logic
    for stone in stones[:]:
        stone.update()
        stone.draw()
        if stone.is_off_screen():
            stones.remove(stone)
            continue

        for bird in birds[:]:
            if check_collision(stone, bird):
                birds.remove(bird)
                if stone in stones:
                    stones.remove(stone)
                score += 100
                break

    # Draw the ground
    ground_height = 40
    pygame.draw.rect(screen, (80, 200, 80), (0, HEIGHT - ground_height, WIDTH, ground_height))

    # Zombieboy animation logic
    if zombieboy_animating:
        now = time.time()
        if zombieboy_frame_index < len(zombieboy_frames) - 1:
            if now - zombieboy_anim_timer > zombieboy_anim_speed:
                zombieboy_frame_index += 1
                zombieboy_anim_timer = now
        else:
            zombieboy_animating = False
            zombieboy_frame_index = 0
    zombieboy_img = zombieboy_frames[zombieboy_frame_index]
    zombieboy_img = pygame.transform.scale(zombieboy_img, (100, 100))
    screen.blit(zombieboy_img, boy_pos)

    # Draw trajectory tracer (gradient line, semi-transparent)
    tracer_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    tracer_points = []
    tracer_x = boy_pos[0] + 75
    tracer_y = boy_pos[1] + 40
    tracer_angle = math.radians(angle)
    tracer_velocity = velocity
    t = 0
    max_t = 0

    # Collect points for the tracer
    while True:
        x = tracer_x + tracer_velocity * math.cos(tracer_angle) * t
        y = tracer_y - (tracer_velocity * math.sin(tracer_angle) * t - 0.5 * GRAVITY * t ** 2)
        if x > WIDTH or y > HEIGHT or y < 0:
            break
        tracer_points.append((int(x), int(y)))
        t += 0.05
        max_t = t

    # Draw a gradient line along the tracer points
    for i in range(1, len(tracer_points)):
        alpha = max(0, 180 - int(180 * (i / len(tracer_points))))
        color = (100, 100, 100, alpha)
        pygame.draw.line(tracer_surface, color, tracer_points[i-1], tracer_points[i], 4)
    screen.blit(tracer_surface, (0, 0))

    # UI stuff
    info_text = f"Angle: {angle}°  Velocity: {velocity}  Score: {score}  Stones: {stone_count}"
    shadow = font.render(info_text, True, (0, 0, 0))
    screen.blit(shadow, (14, 14))
    info = font.render(info_text, True, (255, 255, 255))
    screen.blit(info, (10, 10))

    # Check for game over
    if stone_count == 0 and len(stones) == 0 and not any([stone for stone in stones]):
        game_over_text = font.render(f"Game Over! Final Score: {score}", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False
        continue

    pygame.display.flip()

pygame.quit()
