import pygame
import math
import random
import time
import json
import os
from datetime import datetime

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('music/bgm1.mp3')
pygame.mixer.music.play(-1)

explode_sound = pygame.mixer.Sound('music/explode1.mp3')
throw_sound = pygame.mixer.Sound('music/throw1.wav')
select_sound = pygame.mixer.Sound('music/select1.wav')
high_score_sound = pygame.mixer.Sound('music/highscore.wav')
powerup_sound = pygame.mixer.Sound('music/powerup.wav')

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

# Add power-up related constants
POWERUP_DURATION = 5  # seconds
POWERUP_TYPES = {
    'red': {'name': '2x Points', 'color': (255, 0, 0), 'image': 'powerup_2x.png'},
    'blue': {'name': 'Big Stones', 'color': (0, 0, 255), 'image': 'powerup_bigstones.png'},
    'green': {'name': 'Extra Stones', 'color': (0, 255, 0), 'image': 'powerup_extrastones.png'},
    'yellow': {'name': 'Slow Motion', 'color': (255, 255, 0), 'image': 'powerup_slow.png'}
}

# Load powerup images
powerup_images = {
    type_name: pygame.transform.scale(pygame.image.load(f'assets/{info["image"]}').convert_alpha(), (80, 80))
    for type_name, info in POWERUP_TYPES.items()
}

def load_leaderboard():
    try:
        if os.path.exists('leaderboard.json'):
            with open('leaderboard.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_leaderboard(leaderboard):
    try:
        with open('leaderboard.json', 'w') as f:
            json.dump(leaderboard, f)
    except:
        pass

def get_highest_score():
    leaderboard = load_leaderboard()
    if leaderboard:
        return leaderboard[0]['score']  # Leaderboard is already sorted by score
    return 0

def add_to_leaderboard(name, score):
    leaderboard = load_leaderboard()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    leaderboard.append({
        'name': name,
        'score': score,
        'date': current_time
    })
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    leaderboard = leaderboard[:5]  # Keep only top 5 scores
    save_leaderboard(leaderboard)
    return leaderboard

def get_name_input(screen, font):
    name = ""
    input_active = True
    while input_active:
        screen.fill((0, 0, 0))
        prompt = font.render("Enter your name:", True, (255, 255, 255))
        name_text = font.render(name + "|", True, (255, 255, 255))
        continue_text = font.render("Press ENTER to continue", True, (255, 255, 255))
        
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - 50))
        screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, HEIGHT//2))
        screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 10 and event.unicode.isalnum():
                    name += event.unicode
    return name

class PowerUp:
    def __init__(self, type_name):
        self.type = type_name
        self.start_time = time.time()
        self.active = True
    
    def is_expired(self):
        return time.time() - self.start_time > POWERUP_DURATION

class Bird:
    def __init__(self):
        self.x = WIDTH
        self.y = random.randint(100, 300)
        self.original_speed = random.uniform(2, 5)
        self.speed = self.original_speed
        self.radius = 20
        self.frame_index = 0
        self.last_anim_time = time.time()
        # Randomly assign power-up type to some birds
        self.powerup_type = random.choice(list(POWERUP_TYPES.keys())) if random.random() < 0.2 else None
        
        if self.powerup_type:
            # Use the powerup image
            self.image = powerup_images[self.powerup_type]
            self.frames = [self.image]  # Single frame for power-up birds
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
        else:
            # Regular bird animation
            self.frames = birb_frames
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def move(self):
        self.x -= self.speed
        self.rect.x = int(self.x)
        
        # Only animate if it's a regular bird
        if not self.powerup_type:
            now = time.time()
            if now - self.last_anim_time > 0.08:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
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
    # Get the center points of both objects
    stone_center = (stone.x, stone.y)
    if bird.powerup_type:
        # For powerups, use the center of the 80x80 image
        bird_center = (bird.x + 40, bird.y + 40)
        collision_radius = 40  # Half of the powerup image size
    else:
        # For regular birds, use the original collision radius
        bird_center = (bird.x + 25, bird.y + 20)
        collision_radius = 28
    
    # Calculate distance between centers
    dx = stone_center[0] - bird_center[0]
    dy = stone_center[1] - bird_center[1]
    distance = math.hypot(dx, dy)
    
    return distance < collision_radius

class LeaderboardScreen:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.title_font = pygame.font.SysFont('VCR OSD Mono', 72)
        self.score_font = pygame.font.SysFont('VCR OSD Mono', 36)
        self.date_font = pygame.font.SysFont('VCR OSD Mono', 24)
        self.continue_font = pygame.font.SysFont('VCR OSD Mono', 36)
    
    def draw(self, leaderboard):
        self.screen.fill((0, 0, 0))
        
        # Draw title
        title = self.title_font.render("Leaderboard", True, (255, 255, 255))
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 50))
        
        # Draw column headers
        headers = ["Rank", "Name", "Score", "Date"]
        header_x = [self.width//2 - 250, self.width//2 - 150, self.width//2 + 50, self.width//2 + 200]
        for i, header in enumerate(headers):
            header_text = self.score_font.render(header, True, (255, 255, 0))
            self.screen.blit(header_text, (header_x[i], 120))
        
        # Draw scores
        y = 180
        for i, entry in enumerate(leaderboard):
            rank = f"{i+1}."
            name = entry['name']
            score = str(entry['score'])
            date = entry.get('date', 'N/A')
            
            rank_text = self.score_font.render(rank, True, (255, 255, 0))
            name_text = self.score_font.render(name, True, (255, 255, 255))
            score_text = self.score_font.render(score, True, (255, 255, 255))
            date_text = self.date_font.render(date, True, (200, 200, 200))
            
            self.screen.blit(rank_text, (header_x[0], y))
            self.screen.blit(name_text, (header_x[1], y))
            self.screen.blit(score_text, (header_x[2], y))
            self.screen.blit(date_text, (header_x[3], y))
            y += 60
        
        # Draw continue text
        continue_text = self.continue_font.render("Press SPACE to continue", True, (255, 255, 255))
        self.screen.blit(continue_text, (self.width//2 - continue_text.get_width()//2, self.height - 100))
        
        pygame.display.flip()
    
    def run(self, leaderboard):
        self.draw(leaderboard)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False

class Menu:
    def __init__(self, screen, sky, width, height, select_sound=None):
        self.screen = screen
        self.sky = sky
        self.width = width
        self.height = height
        self.select_sound = select_sound
        self.title_font = pygame.font.SysFont('VCR OSD Mono', 72)
        self.button_font = pygame.font.SysFont('VCR OSD Mono', 48)
        self.options = ['Start', 'Leaderboard', 'Quit']
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
                            leaderboard_screen = LeaderboardScreen(self.screen, self.width, self.height)
                            leaderboard_screen.run(load_leaderboard())
                        elif self.selected_idx == 2:
                            pygame.quit()
                            exit()

def reset_game_variables():
    global angle, velocity, stones, birds, score, stone_count, zombieboy_frame_index, zombieboy_animating, zombieboy_anim_timer, high_score_achieved, active_powerups
    angle = 45
    velocity = 50
    stones = []
    birds = []
    score = 0
    stone_count = 20
    zombieboy_frame_index = 0
    zombieboy_animating = False
    zombieboy_anim_timer = 0
    high_score_achieved = False
    active_powerups = []  # Reset active power-ups

menu = Menu(screen, SKY, WIDTH, HEIGHT, select_sound)
menu_result = menu.run()
reset_game_variables()
running = menu_result == 'start'
bird_spawn_timer = 0
high_score_achieved = False
active_powerups = []  # Initialize active power-ups list

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
                # Check for power-up activation
                if bird.powerup_type:
                    powerup_sound.play()
                    active_powerups.append(PowerUp(bird.powerup_type))
                birds.remove(bird)
                stones.remove(stone)
                # Apply power-up effects
                points = 100
                for powerup in active_powerups:
                    if powerup.type == 'red':  # 2x Points
                        points *= 2
                score += points
                if score > get_highest_score() and not high_score_achieved:
                    high_score_sound.play()
                    high_score_achieved = True
                # Apply other power-up effects
                for powerup in active_powerups:
                    if powerup.type == 'green':  # Extra Stones
                        stone_count += 1
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
    if stone_count == 0 and len(stones) == 0 and not any([stone for stone in stones]):
        leaderboard = load_leaderboard()
        if score > 0 and (len(leaderboard) < 5 or score > leaderboard[-1]['score']):
            name = get_name_input(screen, font)
            leaderboard = add_to_leaderboard(name, score)
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_font = pygame.font.SysFont('VCR OSD Mono', 72)
        score_font = pygame.font.SysFont('VCR OSD Mono', 48)
        
        game_over_text = game_over_font.render("Game Over!", True, (255, 0, 0))
        final_score_text = score_font.render(f"Final Score: {score}", True, (255, 255, 255))
        continue_text = score_font.render("Press SPACE to continue", True, (255, 255, 255))
        
        # Center all text
        x = WIDTH // 2
        y = HEIGHT // 2 - 100
        
        screen.blit(game_over_text, (x - game_over_text.get_width() // 2, y))
        screen.blit(final_score_text, (x - final_score_text.get_width() // 2, y + 80))
        screen.blit(continue_text, (x - continue_text.get_width() // 2, y + 200))
        
        pygame.display.flip()
        
        # Wait for space key
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
        
        # Show leaderboard
        leaderboard_screen = LeaderboardScreen(screen, WIDTH, HEIGHT)
        leaderboard_screen.run(leaderboard)
        
        reset_game_variables()
        menu.selected_idx = 0
        menu_result = menu.run()
        running = menu_result == 'start'
        continue

    # Update active power-ups
    active_powerups = [p for p in active_powerups if not p.is_expired()]
    
    # Apply power-up effects to stone size
    stone_scale = 1.0
    for powerup in active_powerups:
        if powerup.type == 'blue':  # Big Stones
            stone_scale = 2.0
            break

    # Apply power-up effects to game speed
    game_speed = 1.0
    for powerup in active_powerups:
        if powerup.type == 'yellow':  # Slow Motion
            game_speed = 0.5
            break

    # Update stone size based on power-up
    stone_img = pygame.transform.scale(pygame.image.load('assets/stone.png').convert_alpha(), 
                                    (int(24 * stone_scale), int(24 * stone_scale)))

    # Instead, apply speed to bird movement
    for bird in birds:
        bird.speed = bird.original_speed * game_speed

    # Update the info display to get the current highest score
    angle_text = f"Angle: {angle}°  Velocity: {velocity}  Score: "
    score_text = f"{score}"
    high_score_text = f"  Stones: {stone_count}  High Score: {get_highest_score()}"
    
    # Render each part with its own color
    angle_shadow = font.render(angle_text, True, (0, 0, 0))
    score_shadow = font.render(score_text, True, (0, 0, 0))
    high_score_shadow = font.render(high_score_text, True, (0, 0, 0))
    
    angle_info = font.render(angle_text, True, (255, 255, 255))
    score_info = font.render(score_text, True, (0, 255, 0))  # Green color
    high_score_info = font.render(high_score_text, True, (255, 255, 0))  # Yellow color
    
    # Draw shadows
    screen.blit(angle_shadow, (14, 14))
    screen.blit(score_shadow, (14 + angle_shadow.get_width(), 14))
    screen.blit(high_score_shadow, (14 + angle_shadow.get_width() + score_shadow.get_width(), 14))
    
    # Draw colored text
    screen.blit(angle_info, (10, 10))
    screen.blit(score_info, (10 + angle_info.get_width(), 10))
    screen.blit(high_score_info, (10 + angle_info.get_width() + score_info.get_width(), 10))

    # Draw active power-ups
    powerup_y = 50
    for powerup in active_powerups:
        remaining_time = POWERUP_DURATION - (time.time() - powerup.start_time)
        powerup_text = f"{POWERUP_TYPES[powerup.type]['name']}: {remaining_time:.1f}s"
        powerup_surface = font.render(powerup_text, True, POWERUP_TYPES[powerup.type]['color'])
        screen.blit(powerup_surface, (10, powerup_y))
        powerup_y += 30

    pygame.display.flip()
pygame.quit()
=======
import pygame
import math
import random
import time
import json
import os
from datetime import datetime

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('music/bgm1.mp3')
pygame.mixer.music.play(-1)

explode_sound = pygame.mixer.Sound('music/explode1.mp3')
throw_sound = pygame.mixer.Sound('music/throw1.wav')
select_sound = pygame.mixer.Sound('music/select1.wav')
high_score_sound = pygame.mixer.Sound('music/highscore.wav')

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

def load_leaderboard():
    try:
        if os.path.exists('leaderboard.json'):
            with open('leaderboard.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_leaderboard(leaderboard):
    try:
        with open('leaderboard.json', 'w') as f:
            json.dump(leaderboard, f)
    except:
        pass

def get_highest_score():
    leaderboard = load_leaderboard()
    if leaderboard:
        return leaderboard[0]['score']  # Leaderboard is already sorted by score
    return 0

def add_to_leaderboard(name, score):
    leaderboard = load_leaderboard()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    leaderboard.append({
        'name': name,
        'score': score,
        'date': current_time
    })
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    leaderboard = leaderboard[:5]  # Keep only top 5 scores
    save_leaderboard(leaderboard)
    return leaderboard

def get_name_input(screen, font):
    name = ""
    input_active = True
    while input_active:
        screen.fill((0, 0, 0))
        prompt = font.render("Enter your name:", True, (255, 255, 255))
        name_text = font.render(name + "|", True, (255, 255, 255))
        continue_text = font.render("Press ENTER to continue", True, (255, 255, 255))
        
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - 50))
        screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, HEIGHT//2))
        screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 10 and event.unicode.isalnum():
                    name += event.unicode
    return name

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

class LeaderboardScreen:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.title_font = pygame.font.SysFont('VCR OSD Mono', 72)
        self.score_font = pygame.font.SysFont('VCR OSD Mono', 36)
        self.date_font = pygame.font.SysFont('VCR OSD Mono', 24)
        self.continue_font = pygame.font.SysFont('VCR OSD Mono', 36)
    
    def draw(self, leaderboard):
        self.screen.fill((0, 0, 0))
        
        # Draw title
        title = self.title_font.render("Leaderboard", True, (255, 255, 255))
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 50))
        
        # Draw column headers
        headers = ["Rank", "Name", "Score", "Date"]
        header_x = [self.width//2 - 250, self.width//2 - 150, self.width//2 + 50, self.width//2 + 200]
        for i, header in enumerate(headers):
            header_text = self.score_font.render(header, True, (255, 255, 0))
            self.screen.blit(header_text, (header_x[i], 120))
        
        # Draw scores
        y = 180
        for i, entry in enumerate(leaderboard):
            rank = f"{i+1}."
            name = entry['name']
            score = str(entry['score'])
            date = entry.get('date', 'N/A')
            
            rank_text = self.score_font.render(rank, True, (255, 255, 0))
            name_text = self.score_font.render(name, True, (255, 255, 255))
            score_text = self.score_font.render(score, True, (255, 255, 255))
            date_text = self.date_font.render(date, True, (200, 200, 200))
            
            self.screen.blit(rank_text, (header_x[0], y))
            self.screen.blit(name_text, (header_x[1], y))
            self.screen.blit(score_text, (header_x[2], y))
            self.screen.blit(date_text, (header_x[3], y))
            y += 60
        
        # Draw continue text
        continue_text = self.continue_font.render("Press SPACE to continue", True, (255, 255, 255))
        self.screen.blit(continue_text, (self.width//2 - continue_text.get_width()//2, self.height - 100))
        
        pygame.display.flip()
    
    def run(self, leaderboard):
        self.draw(leaderboard)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False

class Menu:
    def __init__(self, screen, sky, width, height, select_sound=None):
        self.screen = screen
        self.sky = sky
        self.width = width
        self.height = height
        self.select_sound = select_sound
        self.title_font = pygame.font.SysFont('VCR OSD Mono', 72)
        self.button_font = pygame.font.SysFont('VCR OSD Mono', 48)
        self.options = ['Start', 'Leaderboard', 'Quit']
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
                            leaderboard_screen = LeaderboardScreen(self.screen, self.width, self.height)
                            leaderboard_screen.run(load_leaderboard())
                        elif self.selected_idx == 2:
                            pygame.quit()
                            exit()

def reset_game_variables():
    global angle, velocity, stones, birds, score, stone_count, zombieboy_frame_index, zombieboy_animating, zombieboy_anim_timer, high_score_achieved
    angle = 45
    velocity = 50
    stones = []
    birds = []
    score = 0
    stone_count = 20
    zombieboy_frame_index = 0
    zombieboy_animating = False
    zombieboy_anim_timer = 0
    high_score_achieved = False  # Reset the high score achievement flag

menu = Menu(screen, SKY, WIDTH, HEIGHT, select_sound)
menu_result = menu.run()
reset_game_variables()
running = menu_result == 'start'
bird_spawn_timer = 0
high_score_achieved = False  # Initialize the high score achievement flag

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
                # Check if this score exceeds the current highest score and sound hasn't played yet
                if score > get_highest_score() and not high_score_achieved:
                    high_score_sound.play()
                    high_score_achieved = True  # Mark that we've played the sound
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
    if stone_count == 0 and len(stones) == 0 and not any([stone for stone in stones]):
        leaderboard = load_leaderboard()
        if score > 0 and (len(leaderboard) < 5 or score > leaderboard[-1]['score']):
            name = get_name_input(screen, font)
            leaderboard = add_to_leaderboard(name, score)
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_font = pygame.font.SysFont('VCR OSD Mono', 72)
        score_font = pygame.font.SysFont('VCR OSD Mono', 48)
        
        game_over_text = game_over_font.render("Game Over!", True, (255, 0, 0))
        final_score_text = score_font.render(f"Final Score: {score}", True, (255, 255, 255))
        continue_text = score_font.render("Press SPACE to continue", True, (255, 255, 255))
        
        # Center all text
        x = WIDTH // 2
        y = HEIGHT // 2 - 100
        
        screen.blit(game_over_text, (x - game_over_text.get_width() // 2, y))
        screen.blit(final_score_text, (x - final_score_text.get_width() // 2, y + 80))
        screen.blit(continue_text, (x - continue_text.get_width() // 2, y + 200))
        
        pygame.display.flip()
        
        # Wait for space key
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
        
        # Show leaderboard
        leaderboard_screen = LeaderboardScreen(screen, WIDTH, HEIGHT)
        leaderboard_screen.run(leaderboard)
        
        reset_game_variables()
        menu.selected_idx = 0
        menu_result = menu.run()
        running = menu_result == 'start'
        continue

    # Update the info display to get the current highest score
    angle_text = f"Angle: {angle}°  Velocity: {velocity}  Score: "
    score_text = f"{score}"
    high_score_text = f"High Score: {get_highest_score()}  Stones: {stone_count}"

    # Render each part with its own color
    angle_shadow = font.render(angle_text, True, (0, 0, 0))
    score_shadow = font.render(score_text, True, (0, 0, 0))
    high_score_shadow = font.render(high_score_text, True, (0, 0, 0))

    angle_info = font.render(angle_text, True, (255, 255, 255))
    score_info = font.render(score_text, True, (0, 255, 0))  # Green color
    high_score_info = font.render(high_score_text, True, (255, 255, 0))  # Yellow color

    # Draw shadows (first line)
    screen.blit(angle_shadow, (14, 14))
    screen.blit(score_shadow, (14 + angle_shadow.get_width(), 14))
    # Draw colored text (first line)
    screen.blit(angle_info, (10, 10))
    screen.blit(score_info, (10 + angle_info.get_width(), 10))

    # Draw shadow and colored text for high score (second line)
    screen.blit(high_score_shadow, (14, 14 + angle_shadow.get_height()))
    screen.blit(high_score_info, (10, 10 + angle_info.get_height()))
    pygame.display.flip()
pygame.quit()
