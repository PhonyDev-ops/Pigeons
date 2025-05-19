import pygame
import math
import random
import time

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('music/bgm1.mp3')
pygame.mixer.music.play(-1)

explode_sound = pygame.mixer.Sound('music/explode1.mp3')
throw_sound = pygame.mixer.Sound('music/throw1.wav')
select_sound = pygame.mixer.Sound('music/select1.wav')

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pigeons!")

SKY = pygame.image.load('assets/nightcity.png').convert()
clock = pygame.time.Clock()
FPS = 60
GRAVITY = 9.8

birb_frames = [
    pygame.transform.scale(pygame.image.load(f'assets/brib_f{i+1}.png').convert_alpha(), (50, 40))
    for i in range(8)
]
zombieboy_frames = [
    pygame.image.load(f'assets/zombieboy{i+1}.png').convert_alpha()
    for i in range(5)
]
zombieboy_frame_index = 0
zombieboy_animating = False
zombieboy_anim_timer = 0
zombieboy_anim_speed = 0.07

font = pygame.font.SysFont('VCR OSD Mono', 36)
boy_pos = (100, HEIGHT - 120)
angle = 45
velocity = 50
stones = []
birds = []
score = 0
stone_count = 20
stone_img = pygame.transform.scale(pygame.image.load('assets/stone.png').convert_alpha(), (24, 24))

class Bird:
    def __init__(self):
        self.x = WIDTH
        self.y = random.randint(100, 300)
        self.speed = random.uniform(2, 5)
        self.radius = 20
        self.frame_index = 0
        self.last_anim_time = time.time()
        self.image = birb_frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    def move(self):
        self.x -= self.speed
        self.rect.x = int(self.x)
        now = time.time()
        if now - self.last_anim_time > 0.08:
            self.frame_index = (self.frame_index + 1) % len(birb_frames)
            self.image = birb_frames[self.frame_index]
            self.last_anim_time = now
    def draw(self):
        screen.blit(self.image, self.rect)

class Stone:
    def __init__(self, angle, velocity):
        self.x = boy_pos[0] + 90
        self.y = boy_pos[1] + 7
        self.angle = math.radians(angle)
        self.velocity = velocity
        self.time = 0
        self.image = stone_img
    def update(self):
        t = self.time
        self.x = boy_pos[0] + 90 + self.velocity * math.cos(self.angle) * t
        self.y = boy_pos[1] + 7 - (self.velocity * math.sin(self.angle) * t - 0.5 * GRAVITY * t ** 2)
        self.time += 0.1
    def draw(self):
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.image, rect)
    def is_off_screen(self):
        return self.x > WIDTH or self.y > HEIGHT or self.y < 0

def check_collision(stone, bird):
    dx = stone.x - (bird.x + 25)
    dy = stone.y - (bird.y + 20)
    return math.hypot(dx, dy) < 28

class Menu:
    def __init__(self, screen, sky, width, height, select_sound=None):
        self.screen = screen
        self.sky = sky
        self.width = width
        self.height = height
        self.select_sound = select_sound
        self.title_font = pygame.font.SysFont('VCR OSD Mono', 72)
        self.button_font = pygame.font.SysFont('VCR OSD Mono', 48)
        self.options = ['Start', 'Quit']
        self.selected_idx = 0
    def draw(self):
        self.screen.blit(self.sky, (0, 0))
        title = self.title_font.render('Pigeons!', True, (255, 255, 255))
        pigeon_img = pygame.transform.scale(birb_frames[0], (150, 150))
        total_width = title.get_width() + pigeon_img.get_width() + 10
        title_x = self.width // 2 - total_width // 2
        title_y = self.height // 4
        self.screen.blit(title, (title_x, title_y))
        self.screen.blit(pigeon_img, (title_x + title.get_width() + 10, title_y + (title.get_height() - pigeon_img.get_height()) // 2))
        for i, text in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_idx else (255, 255, 255)
            option_text = self.button_font.render(text, True, color)
            rect = option_text.get_rect(center=(self.width // 2, self.height // 2 + i * 100))
            pygame.draw.rect(self.screen, (0, 0, 0), rect.inflate(40, 20))
            self.screen.blit(option_text, rect)
        pygame.display.flip()
    def run(self):
        while True:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        if self.select_sound:
                            self.select_sound.play()
                        self.selected_idx = (self.selected_idx - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        if self.select_sound:
                            self.select_sound.play()
                        self.selected_idx = (self.selected_idx + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if self.selected_idx == 0:
                            return 'start'
                        elif self.selected_idx == 1:
                            pygame.quit()
                            exit()

def reset_game_variables():
    global angle, velocity, stones, birds, score, stone_count, zombieboy_frame_index, zombieboy_animating, zombieboy_anim_timer
    angle = 45
    velocity = 50
    stones = []
    birds = []
    score = 0
    stone_count = 20
    zombieboy_frame_index = 0
    zombieboy_animating = False
    zombieboy_anim_timer = 0

menu = Menu(screen, SKY, WIDTH, HEIGHT, select_sound)
menu_result = menu.run()
reset_game_variables()
running = menu_result == 'start'
bird_spawn_timer = 0

while running:
    screen.blit(SKY, (0, 0))
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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
            throw_sound.play()
            stone_count -= 1
            zombieboy_animating = True
            zombieboy_frame_index = 0
            zombieboy_anim_timer = time.time()
    bird_spawn_timer += 1
    if bird_spawn_timer > 90:
        birds.append(Bird())
        bird_spawn_timer = 0
    for bird in birds[:]:
        bird.move()
        bird.draw()
        if bird.x < -50:
            birds.remove(bird)
    for stone in stones[:]:
        stone.update()
        stone.draw()
        if stone.is_off_screen():
            stones.remove(stone)
            continue
        for bird in birds[:]:
            if check_collision(stone, bird):
                explode_sound.play()
                birds.remove(bird)
                stones.remove(stone)
                score += 100
                stone_count += 1
                break
    if zombieboy_animating:
        now = time.time()
        if zombieboy_frame_index < len(zombieboy_frames) - 1:
            if now - zombieboy_anim_timer > zombieboy_anim_speed:
                zombieboy_frame_index += 1
                zombieboy_anim_timer = now
        else:
            zombieboy_animating = False
            zombieboy_frame_index = 0
    zombieboy_img = pygame.transform.scale(zombieboy_frames[zombieboy_frame_index], (100, 100))
    screen.blit(zombieboy_img, boy_pos)
    tracer_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    tracer_points = []
    tracer_x = boy_pos[0] + 90
    tracer_y = boy_pos[1] + 7
    tracer_angle = math.radians(angle)
    tracer_velocity = velocity
    t = 0
    while True:
        x = tracer_x + tracer_velocity * math.cos(tracer_angle) * t
        y = tracer_y - (tracer_velocity * math.sin(tracer_angle) * t - 0.5 * GRAVITY * t ** 2)
        if x > WIDTH or y > HEIGHT or y < 0:
            break
        tracer_points.append((int(x), int(y)))
        t += 0.05
    for i, point in enumerate(tracer_points):
        if i % 7 == 0:
            alpha = max(0, 180 - int(120 * (i / len(tracer_points))))
            tracer_color = (255, 255, 255, alpha)
            tracer_circle = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(tracer_circle, tracer_color, (6, 6), 6)
            tracer_surface.blit(tracer_circle, (point[0] - 6, point[1] - 6))
    screen.blit(tracer_surface, (0, 0))
    info_text = f"Angle: {angle}°  Velocity: {velocity}  Score: {score}  Stones: {stone_count}"
    shadow = font.render(info_text, True, (0, 0, 0))
    screen.blit(shadow, (14, 14))
    info = font.render(info_text, True, (255, 255, 255))
    screen.blit(info, (10, 10))
    if stone_count == 0 and len(stones) == 0 and not any([stone for stone in stones]):
        game_over_text = font.render(f"Game Over! Final Score: {score}", True, (255, 0, 0))
        shadow = font.render(f"Game Over! Final Score: {score}", True, (0, 0, 0))
        x = WIDTH // 2 - game_over_text.get_width() // 2
        y = HEIGHT // 2
        screen.blit(shadow, (x + 4, y + 4))
        screen.blit(game_over_text, (x, y))
        pygame.display.flip()
        pygame.time.wait(3000)
        reset_game_variables()
        menu.selected_idx = 0
        menu_result = menu.run()
        running = menu_result == 'start'
        continue
    pygame.display.flip()
pygame.quit()
