import pygame
import random
import math

# Background dimensions
# 16x16 tiles
# Image Width 944 px, Height 512 px
# W: 59 tiles, H: 32 tiles

def ExtractDog(sprite_sheet_path):
    pygame.init()
    sprite_sheet = pygame.image.load(sprite_sheet_path)
    sprite_height = 27
    sprite_width = 46
    num_sprites = 4
    sprites = {"Moving": [], "Idle": None}

    for i in range(num_sprites):
        x = (i % 2) * sprite_width
        y = (i // 2) * sprite_height
        rect = pygame.Rect(x, y, sprite_width, sprite_height)
        sprite = sprite_sheet.subsurface(rect).copy()
        
        if i < 3:
            sprites["Moving"].append(sprite)
        else:
            sprites["Idle"] = sprite

    return sprites

class Character:
    def __init__(self, x, y, speed, sprites, barriers):
        self.x = x
        self.y = y
        self.speed = speed
        self.sprites = sprites
        self.image = self.sprites["Idle"]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.barriers = barriers
        self.state = "Idle"  # Initial state
        self.current_sprite = 0  # Index for animation
        self.animation_timer = 0  # Timer for animation speed
        self.animation_speed = 10  # Control how fast the sprite changes
        self.direction = 'R'  # Default direction is Right
        self.last_key_pressed = None  # To keep track of the last key pressed

    def move(self, dx, dy):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        new_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)

        if not is_collision(new_rect, self.barriers):
            self.x = new_x
            self.y = new_y
            self.rect.topleft = (self.x, self.y)
            self.state = "Moving"  # Update state to Moving

            # Update direction based on movement input if movement key is pressed
            if dx > 0:
                self.direction = 'R'
                self.last_key_pressed = pygame.K_RIGHT
            elif dx < 0:
                self.direction = 'L'
                self.last_key_pressed = pygame.K_LEFT
        else:
            self.state = "Idle"  # Update state to Idle if collision

        # Update sprite based on state
        self.update_sprite()

    def update_sprite(self):
        if self.state == "Moving":
            # Update sprite for animation
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_sprite = (self.current_sprite + 1) % len(self.sprites["Moving"])
                self.image = self.sprites["Moving"][self.current_sprite]
        else:
            self.image = self.sprites["Idle"]

    def draw(self, screen):
        # Flip the image based on direction when drawing
        if self.direction == 'L':
            screen.blit(self.image, self.rect)
        else:
            # Flip image horizontally for right direction
            flipped_image = pygame.transform.flip(self.image, True, False)
            screen.blit(flipped_image, self.rect)

def ExtractSheepImages(image_path):
    sheet = pygame.image.load(image_path).convert_alpha()
    sprite_width = 128
    sprite_height = 128
    num_sprites_x = 4
    num_sprites_y = 4
    directions = ['N', 'W', 'S', 'E']
    sprites = {direction: [] for direction in directions}

    for row, direction in enumerate(directions):
        for col in range(num_sprites_x):
            rect = pygame.Rect(col * sprite_width, row * sprite_height, sprite_width, sprite_height)
            sprite = sheet.subsurface(rect)
            sprites[direction].append(sprite)
    
    return sprites

class Sheep:
    def __init__(self, x, y, base_speed, moving_sprites, idle_sprites, barriers):
        self.x = x
        self.y = y
        self.base_speed = base_speed
        self.speed = base_speed
        self.moving_sprites = moving_sprites
        self.idle_sprites = idle_sprites
        self.orientation = 'S'  # Default orientation
        self.current_sprite = 0
        self.moving = False
        self.image = self.idle_sprites[self.orientation][0]  # Default idle sprite
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.animation_timer = 0
        self.animation_speed = 10
        self.run_away_distance = 100  # Distance to start running away
        self.max_speed = 5  # Maximum speed when very close to the player
        self.barriers = barriers

    def update(self, player_x, player_y):
        distance = math.hypot(self.x - player_x, self.y - player_y)

        # Adjust speed based on distance
        if distance < self.run_away_distance:
            self.speed = self.base_speed + (self.run_away_distance - distance) / self.run_away_distance * (self.max_speed - self.base_speed)
            self.move_away(player_x, player_y)
        else:
            self.speed = self.base_speed
            self.moving = False

        self.update_sprite()

    def move_away(self, player_x, player_y):
        dx = self.x - player_x
        dy = self.y - player_y

        magnitude = math.hypot(dx, dy)
        if magnitude != 0:
            dx /= magnitude
            dy /= magnitude

        move_vector = pygame.Vector2(dx * self.speed, dy * self.speed)
        new_rect = pygame.Rect(self.rect.topleft, self.rect.size)
        new_rect.move_ip(move_vector)

        # Check for collision and adjust position
        if is_collision(new_rect, self.barriers):
            # Move sheep back to the previous position if collision occurs
            self.x -= move_vector.x
            self.y -= move_vector.y
            self.rect.topleft = (self.x, self.y)
        else:
            # Update position and rect if no collision
            self.x += move_vector.x
            self.y += move_vector.y
            self.rect.topleft = (self.x, self.y)

        # Update orientation based on movement direction
        if abs(dx) > abs(dy):
            self.orientation = 'W' if dx > 0 else 'E'
        else:
            self.orientation = 'S' if dy > 0 else 'N'

        self.moving = True

    def update_sprite(self):
        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_sprite = (self.current_sprite + 1) % len(self.moving_sprites[self.orientation])
                self.image = self.moving_sprites[self.orientation][self.current_sprite]
        else:
            self.image = self.idle_sprites[self.orientation][0]  # Default idle sprite for orientation

    def draw(self, screen):
        screen.blit(self.image, self.rect)

def create_barriers(image_width, image_height, tile_size=16):
    barriers = []
    
    for x in range(0, image_width, tile_size):
        barriers.append(pygame.Rect(x, 0, tile_size, tile_size))
        barriers.append(pygame.Rect(x, image_height - tile_size, tile_size, tile_size))
    
    for y in range(0, image_height, tile_size):
        barriers.append(pygame.Rect(0, y, tile_size, tile_size))
        barriers.append(pygame.Rect(image_width - tile_size, y, tile_size, tile_size))
    
    return barriers

def is_collision(rect, barriers):
    for barrier in barriers:
        if rect.colliderect(barrier):
            return True
    return False

def firstLevel():
    pygame.init()
    screen_width, screen_height = 944, 512
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("First Level")

    # Load images
    background = pygame.image.load('Shepherd/background.png').convert()
    dog_sprites = ExtractDog('Shepherd/Dog/DogFrames.png')
    moving_sheep_sprites = ExtractSheepImages('Shepherd/Sheep/sheep_walk.png')
    idle_sheep_sprites = ExtractSheepImages('Shepherd/Sheep/sheep_eat.png')

    # Create barriers
    barriers = create_barriers(screen_width, screen_height, tile_size=16)

    # Create character and sheep instances
    dog = Character(100, 100, 5, dog_sprites, barriers)
    sheeps = [
        Sheep(200, 200, 3, moving_sheep_sprites, idle_sheep_sprites, barriers),
        Sheep(300, 300, 3, moving_sheep_sprites, idle_sheep_sprites, barriers),
        Sheep(400, 400, 3, moving_sheep_sprites, idle_sheep_sprites, barriers)
    ]

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0
        if keys[pygame.K_RIGHT]:
            dx = 1
            dog.move(dx, dy)
        elif keys[pygame.K_LEFT]:
            dx = -1
            dog.move(dx, dy)
        elif keys[pygame.K_DOWN]:
            dy = 1
            dog.move(dx, dy)
        elif keys[pygame.K_UP]:
            dy = -1
            dog.move(dx, dy)
        else:
            dog.state = "Idle"
            dog.update_sprite()

        for sheep in sheeps:
            sheep.update(dog.x, dog.y)

        screen.blit(background, (0, 0))
        dog.draw(screen)
        for sheep in sheeps:
            sheep.draw(screen)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    firstLevel()
