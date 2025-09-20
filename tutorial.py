import os
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()
pygame.mixer.init()

pygame.display.set_caption("SKYHOPPER")

WIDTH, HEIGHT = 1500, 800
FPS = 60
PLAYER_VEL = 7

window = pygame.display.set_mode((WIDTH, HEIGHT))

# Load sounds
try:
    coin_sound = pygame.mixer.Sound("C:/Users/admin/Desktop/test/img/coin.wav")
    jump_sound = pygame.mixer.Sound("C:/Users/admin/Desktop/test/img/jump.wav")
    game_over_sound = pygame.mixer.Sound("C:/Users/admin/Desktop/test/img/game_over.wav")
    # Set volume for sounds
    coin_sound.set_volume(0.7)
    jump_sound.set_volume(0.7)
    game_over_sound.set_volume(0.7)
except:
    print("Warning: Some sound files could not be loaded. The game will continue without sound.")
    coin_sound = None
    jump_sound = None
    game_over_sound = None

# Load start button
try:
    start_button_img = pygame.image.load("C:/Users/admin/Desktop/test/img/start_btn.png").convert_alpha()
    start_button_img = pygame.transform.scale(start_button_img, (200, 100))
except:
    print("Warning: Start button image could not be loaded. Using placeholder.")
    start_button_img = pygame.Surface((200, 100))
    start_button_img.fill((0, 255, 0))
    font = pygame.font.SysFont('Arial', 30)
    text = font.render('START', True, (0, 0, 0))
    start_button_img.blit(text, (70, 35))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f)) and f.endswith('.png')]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size, block_x=96, block_y=0):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(block_x, block_y, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 4

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.coins = 0  # Track collected coins
        self.alive = True  # Track if player is alive
        self.game_started = False  # Track if game has started

    def jump(self):
        if self.alive and self.game_started:
            self.y_vel = -self.GRAVITY * 8
            self.animation_count = 0
            self.jump_count += 1
            if self.jump_count == 1:
                self.fall_count = 0
            # Play jump sound
            if jump_sound:
                jump_sound.play()

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.alive = False  # Player dies when hit by fire
        # Play game over sound
        if game_over_sound:
            game_over_sound.play()

    def move_left(self, vel):
        if self.alive and self.game_started:
            self.x_vel = -vel
            if self.direction != "left":
                self.direction = "left"
                self.animation_count = 0

    def move_right(self, vel):
        if self.alive and self.game_started:
            self.x_vel = vel
            if self.direction != "right":
                self.direction = "right"
                self.animation_count = 0

    def loop(self, fps):
        if self.alive and self.game_started:
            self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
            self.move(self.x_vel, self.y_vel)

            if self.hit:
                self.hit_count += 1
            if self.hit_count > fps * 2:
                self.hit = False
                self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        if not self.alive:
            sprite_sheet = "hit"
        else:
            sprite_sheet = "idle"
            if self.hit:
                sprite_sheet = "hit"
            elif self.y_vel < 0:
                if self.jump_count == 1:
                    sprite_sheet = "jump"
                elif self.jump_count == 2:
                    sprite_sheet = "double_jump"
            elif self.y_vel > self.GRAVITY * 2:
                sprite_sheet = "fall"
            elif self.x_vel != 0:
                sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        if self.game_started:
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
            # Display coin count with black color and bold font
            font = pygame.font.SysFont('Arial', 30, bold=True)
            coin_text = font.render(f'Coins: {self.coins}', True, (0, 0, 0))  # Black color
            win.blit(coin_text, (10, 10))
            
            # Display game over message if player is dead
            if not self.alive:
                # Create a semi-transparent overlay
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))  # Semi-transparent black
                win.blit(overlay, (0, 0))
                
                # Display impactful game over text
                font_large = pygame.font.SysFont('Arial', 80, bold=True)
                font_medium = pygame.font.SysFont('Arial', 40, bold=True)
                
                game_over_text = font_large.render('GAME OVER', True, (255, 0, 0))
                restart_text = font_medium.render('Press R to Restart', True, (255, 255, 255))
                score_text = font_medium.render(f'Coins Collected: {self.coins}', True, (255, 215, 0))
                
                win.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
                win.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
                win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 60))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size, block_x=100, block_y=0):
        super().__init__(x, y, size, size)
        block = get_block(size, block_x, block_y)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class Coin(Object):
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "coin")
        # Load coin sprites from assets/coins directory
        self.coin_sprites = self.load_coin_sprites(width, height)
        self.image = self.coin_sprites[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.collected = False

    def load_coin_sprites(self, width, height):
        # Load the coin sprite sheet
        path = join("assets", "coins", "coin.png")
        sprite_sheet = pygame.image.load(path).convert_alpha()
        
        sprites = []
        # Assuming the coin sprite sheet has 6 frames
        for i in range(6):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        return sprites

    def loop(self):
        if not self.collected:
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.coin_sprites)
            self.image = self.coin_sprites[sprite_index]
            self.animation_count += 1

            self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
            self.mask = pygame.mask.from_surface(self.image)

            if self.animation_count // self.ANIMATION_DELAY > len(self.coin_sprites):
                self.animation_count = 0

    def collect(self):
        self.collected = True
        self.image = pygame.Surface((0, 0), pygame.SRCALPHA)  # Make invisible
        self.rect = pygame.Rect(0, 0, 0, 0)  # Make collision area zero
        # Play coin sound
        if coin_sound:
            coin_sound.play()


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw_start_screen(win, bg_image, background):
    for tile in background:
        win.blit(bg_image, tile)
    
    # Draw start button
    button_rect = start_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    win.blit(start_button_img, button_rect)
    
    # Draw title
    font = pygame.font.SysFont('Arial', 60, bold=True)
    title_text = font.render('SKY HOPPER', True, (0, 0, 0))
    win.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
    
    # Draw instructions
    font = pygame.font.SysFont('Arial', 30)
    instructions = [
        "Collect coins and avoid fire traps!",
        "Use LEFT and RIGHT arrows to move",
        "Press SPACE to jump",
        "Click START to begin"
    ]
    
    for i, instruction in enumerate(instructions):
        text = font.render(instruction, True, (0, 0, 0))
        win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 80 + i * 40))
    
    pygame.display.update()
    
    return button_rect


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left and player.alive and player.game_started:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right and player.alive and player.game_started:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire" and player.alive and player.game_started:
            player.make_hit()
        elif obj and obj.name == "coin" and not obj.collected and player.alive and player.game_started:
            obj.collect()
            player.coins += 1


def reset_game(player, objects, fire_traps, coins):
    # Reset player
    player.rect.x = 50
    player.rect.y = 50
    player.x_vel = 0
    player.y_vel = 0
    player.hit = False
    player.hit_count = 0
    player.coins = 0
    player.alive = True
    player.game_started = True
    
    # Reset coins
    for coin in coins:
        coin.collected = False
        coin.image = coin.coin_sprites[0]
        coin.rect = pygame.Rect(coin.rect.x, coin.rect.y, 32, 32)
        coin.mask = pygame.mask.from_surface(coin.image)
    
    return 0  # Reset offset_x


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("sky.png")

    block_size = 96

    player = Player(50, 50, 50, 50)
    
    # Floor blocks spanning wide area
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 6) // block_size)]  # Extended further to the right

    # Extra terrain blocks with different block types - Filled with many more platforms
    extra_blocks = [
        # First section
        Block(0, HEIGHT - block_size * 2, block_size, block_x=0),
        Block(block_size * 2, HEIGHT - block_size * 3, block_size, block_x=96),
        Block(block_size * 4, HEIGHT - block_size * 4, block_size, block_x=192),
        Block(block_size * 6, HEIGHT - block_size * 3, block_size, block_x=288),
        Block(block_size * 8, HEIGHT - block_size * 5, block_size, block_x=384),
        
        # Second section
        Block(block_size * 10, HEIGHT - block_size * 2, block_size, block_x=0),
        Block(block_size * 12, HEIGHT - block_size * 4, block_size, block_x=96),
        Block(block_size * 14, HEIGHT - block_size * 3, block_size, block_x=192),
        Block(block_size * 16, HEIGHT - block_size * 5, block_size, block_x=288),
        Block(block_size * 18, HEIGHT - block_size * 2, block_size, block_x=384),
        
        # Third section
        Block(block_size * 20, HEIGHT - block_size * 4, block_size, block_x=0),
        Block(block_size * 22, HEIGHT - block_size * 3, block_size, block_x=96),
        Block(block_size * 24, HEIGHT - block_size * 5, block_size, block_x=192),
        Block(block_size * 26, HEIGHT - block_size * 2, block_size, block_x=288),
        Block(block_size * 28, HEIGHT - block_size * 4, block_size, block_x=384),
        
        # Fourth section
        Block(block_size * 30, HEIGHT - block_size * 3, block_size, block_x=0),
        Block(block_size * 32, HEIGHT - block_size * 5, block_size, block_x=96),
        Block(block_size * 34, HEIGHT - block_size * 2, block_size, block_x=192),
        Block(block_size * 36, HEIGHT - block_size * 4, block_size, block_x=288),
        Block(block_size * 38, HEIGHT - block_size * 3, block_size, block_x=384),
        
        # Fifth section
        Block(block_size * 40, HEIGHT - block_size * 5, block_size, block_x=0),
        Block(block_size * 42, HEIGHT - block_size * 2, block_size, block_x=96),
        Block(block_size * 44, HEIGHT - block_size * 4, block_size, block_x=192),
        Block(block_size * 46, HEIGHT - block_size * 3, block_size, block_x=288),
        Block(block_size * 48, HEIGHT - block_size * 5, block_size, block_x=384),
    ]

    # Fire traps - Many more added to fill the level
    fire_traps = [
        # First section fires
        Fire(block_size * 5, HEIGHT - block_size * 3 - 64, 16, 32),
        Fire(block_size * 7, HEIGHT - block_size * 4 - 64, 16, 32),
        Fire(block_size * 9, HEIGHT - block_size * 5 - 64, 16, 32),
        
        # Second section fires
        Fire(block_size * 11, HEIGHT - block_size * 2 - 64, 16, 32),
        Fire(block_size * 13, HEIGHT - block_size * 3 - 64, 16, 32),
        Fire(block_size * 15, HEIGHT - block_size * 4 - 64, 16, 32),
        Fire(block_size * 17, HEIGHT - block_size * 5 - 64, 16, 32),
        Fire(block_size * 19, HEIGHT - block_size * 2 - 64, 16, 32),
        
        # Third section fires
        Fire(block_size * 21, HEIGHT - block_size * 3 - 64, 16, 32),
        Fire(block_size * 23, HEIGHT - block_size * 4 - 64, 16, 32),
        Fire(block_size * 25, HEIGHT - block_size * 5 - 64, 16, 32),
        Fire(block_size * 27, HEIGHT - block_size * 2 - 64, 16, 32),
        Fire(block_size * 29, HEIGHT - block_size * 3 - 64, 16, 32),
        
        # Fourth section fires
        Fire(block_size * 31, HEIGHT - block_size * 4 - 64, 16, 32),
        Fire(block_size * 33, HEIGHT - block_size * 5 - 64, 16, 32),
        Fire(block_size * 35, HEIGHT - block_size * 2 - 64, 16, 32),
        Fire(block_size * 37, HEIGHT - block_size * 3 - 64, 16, 32),
        Fire(block_size * 39, HEIGHT - block_size * 4 - 64, 16, 32),
        
        # Fifth section fires
        Fire(block_size * 41, HEIGHT - block_size * 5 - 64, 16, 32),
        Fire(block_size * 43, HEIGHT - block_size * 2 - 64, 16, 32),
        Fire(block_size * 45, HEIGHT - block_size * 3 - 64, 16, 32),
        Fire(block_size * 47, HEIGHT - block_size * 4 - 64, 16, 32),
        Fire(block_size * 49, HEIGHT - block_size * 5 - 64, 16, 32),
    ]
    for fire_trap in fire_traps:
        fire_trap.on()

    # Coins placed above platforms - Many more added
    coins = [
        # First section coins
        Coin(block_size * 1, HEIGHT - block_size * 3, 32, 32),
        Coin(block_size * 3, HEIGHT - block_size * 4, 32, 32),
        Coin(block_size * 5, HEIGHT - block_size * 5, 32, 32),
        Coin(block_size * 7, HEIGHT - block_size * 6, 32, 32),
        Coin(block_size * 9, HEIGHT - block_size * 6, 32, 32),
        
        # Second section coins
        Coin(block_size * 11, HEIGHT - block_size * 3, 32, 32),
        Coin(block_size * 13, HEIGHT - block_size * 5, 32, 32),
        Coin(block_size * 15, HEIGHT - block_size * 6, 32, 32),
        Coin(block_size * 17, HEIGHT - block_size * 7, 32, 32),
        Coin(block_size * 19, HEIGHT - block_size * 3, 32, 32),
        
        # Third section coins
        Coin(block_size * 21, HEIGHT - block_size * 5, 32, 32),
        Coin(block_size * 23, HEIGHT - block_size * 6, 32, 32),
        Coin(block_size * 25, HEIGHT - block_size * 7, 32, 32),
        Coin(block_size * 27, HEIGHT - block_size * 3, 32, 32),
        Coin(block_size * 29, HEIGHT - block_size * 4, 32, 32),
        
        # Fourth section coins
        Coin(block_size * 31, HEIGHT - block_size * 5, 32, 32),
        Coin(block_size * 33, HEIGHT - block_size * 6, 32, 32),
        Coin(block_size * 35, HEIGHT - block_size * 3, 32, 32),
        Coin(block_size * 37, HEIGHT - block_size * 4, 32, 32),
        Coin(block_size * 39, HEIGHT - block_size * 5, 32, 32),
        
        # Fifth section coins
        Coin(block_size * 41, HEIGHT - block_size * 6, 32, 32),
        Coin(block_size * 43, HEIGHT - block_size * 3, 32, 32),
        Coin(block_size * 45, HEIGHT - block_size * 4, 32, 32),
        Coin(block_size * 47, HEIGHT - block_size * 5, 32, 32),
        Coin(block_size * 49, HEIGHT - block_size * 6, 32, 32),
    ]

    # Combine all objects
    objects = [*floor, *extra_blocks, *fire_traps, *coins]

    offset_x = 0
    scroll_area_width = 200

    # Show start screen first
    start_button_rect = draw_start_screen(window, bg_image, background)
    game_started = False
    
    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2 and player.alive and game_started:
                    player.jump()
                if event.key == pygame.K_r and not player.alive and game_started:
                    # Reset game when R is pressed after death
                    offset_x = reset_game(player, objects, fire_traps, coins)
            
            if event.type == pygame.MOUSEBUTTONDOWN and not game_started:
                if start_button_rect.collidepoint(event.pos):
                    game_started = True
                    player.game_started = True

        if game_started:
            player.loop(FPS)

            for fire_trap in fire_traps:
                fire_trap.loop()

            for obj in objects:
                if obj.name == "coin":
                    obj.loop()

            handle_move(player, objects)
            draw(window, background, bg_image, player, objects, offset_x)

            if player.alive and ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                    (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
                offset_x += player.x_vel
        else:
            # Keep showing the start screen
            start_button_rect = draw_start_screen(window, bg_image, background)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)