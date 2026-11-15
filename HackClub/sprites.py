import pygame
from settings import *

#background + floor sprites
floor_top = ground_y + player_size[1]

try:
    background = pygame.image.load("HackClub/background.png").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except (pygame.error, FileNotFoundError):
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(WHITE)

#boss background
try:
    boss_background = pygame.image.load("HackClub/background2.png").convert()
    boss_background = pygame.transform.scale(boss_background, (WIDTH, HEIGHT))
except (pygame.error, FileNotFoundError):
    boss_background = background

#how many pixels off the floor
KART_SINK = 15
SLIME_SINK = 15
BOSS_SINK = 31

#floors (one per wave)
floors = []
floor_height = HEIGHT - floor_top


FLOOR_TILED = True
FLOOR_CORNER_TRANSPARENT = True #keep True for floor
FLOOR_TRIM = True

for i in range(FINAL_WAVE):
    try:
        floor_image = pygame.image.load(f"HackClub/floor{i + 1}.png").convert_alpha()

        if FLOOR_CORNER_TRANSPARENT:
            corner = floor_image.get_at((0, 0))

            for px in range(floor_image.get_width()):
                for py in range(floor_image.get_height()):
                    color = floor_image.get_at((px, py))

                    if (color.r, color.g, color.b) == (corner.r, corner.g, corner.b):
                        floor_image.set_at((px, py), (corner.r, corner.g, corner.b, 0))

        if FLOOR_TRIM:
            bounds = floor_image.get_bounding_rect()

            if bounds.height > 0:
                floor_image = floor_image.subsurface((0, bounds.y, floor_image.get_width(), bounds.height)).copy()

        if FLOOR_TILED:
            #scale to the floor height, then repeat across the width
            tile_width = max(1, floor_image.get_width() * floor_height // floor_image.get_height())
            tile = pygame.transform.scale(floor_image, (tile_width, floor_height))

            floor_image = pygame.Surface((WIDTH, floor_height), pygame.SRCALPHA)

            for x in range(0, WIDTH, tile_width):
                floor_image.blit(tile, (x, 0))
        else:
            floor_image = pygame.transform.scale(floor_image, (WIDTH, floor_height))
    except (pygame.error, FileNotFoundError):
        floor_image = pygame.Surface((WIDTH, HEIGHT - floor_top))
        floor_image.fill(BLACK)

    floors.append(floor_image)

#upgrade sprites
try:
    health_icon = pygame.image.load("HackClub/health.png").convert_alpha()
    health_icon = pygame.transform.scale(health_icon, (30, 30))
except pygame.error:
    health_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(health_icon, RED, (15, 15), 12)

try:
    damage_icon = pygame.image.load("HackClub/damage.png").convert_alpha()
    damage_icon = pygame.transform.scale(damage_icon, (30, 30))
except pygame.error:
    damage_icon = pygame.Surface((30, 30), pygame.SRCALPHA)

try:
    defence_icon = pygame.image.load("HackClub/defence.png").convert_alpha()
    defence_icon = pygame.transform.scale(defence_icon, (30, 30))
except pygame.error:
    defence_icon = pygame.Surface((30, 30), pygame.SRCALPHA)

try:
    coin_icon = pygame.image.load("HackClub/coin.png").convert_alpha()
    coin_icon = pygame.transform.scale(coin_icon, (30, 30))
except pygame.error:
    coin_icon = pygame.Surface((30, 30), pygame.SRCALPHA)

#player sprites
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.set_kart(0)

    def set_kart(self, index):
        kart = KARTS[index]

        try:
            self.image = pygame.image.load(kart["image"]).convert_alpha()
            self.image = pygame.transform.scale(self.image, player_size)
        except (pygame.error, FileNotFoundError) as error:
            print("could not load", kart["image"], "-", error)
            self.image = pygame.Surface(player_size)
            self.image.fill(kart["color"])

        #keep the player in place
        position = self.rect.topleft if hasattr(self, "rect") else (0, 0)
        self.rect = self.image.get_rect(topleft=position)


#defence cuts the damage you deal
SLIME_STATS = [
    {"image": "HackClub/greenslime.png", "hp": 16, "defence": 0, "speed": 2, "coins": 5, "damage": 16, "color": (0, 200, 0)},
    {"image": "HackClub/jungleslime.png", "hp": 26, "defence": 8, "speed": 3, "coins": 10, "damage": 20, "color": (0, 120, 40)},
    {"image": "HackClub/blueslime.png", "hp": 42, "defence": 16, "speed": 3, "coins": 15, "damage": 24, "color": (0, 150, 255)},
    {"image": "HackClub/iceslime.png", "hp": 65, "defence": 24, "speed": 4, "coins": 25, "damage": 30, "color": (150, 230, 255)},
]

BOSS_STATS = {"image": "HackClub/bigslime.png", "hp": 200, "defence": 28, "speed": 4, "coins": 25, "damage": 30, "color": (120, 0, 160), "size": (120, 120), "sink": BOSS_SINK}

class Enemy(pygame.sprite.Sprite):
    def __init__(self, stats, x, direction, wave=1):
        super().__init__()

        size = stats.get("size", player_size)

        try:
            self.image = pygame.image.load(stats["image"]).convert_alpha()
            self.image = pygame.transform.scale(self.image, size)
        except (pygame.error, FileNotFoundError):
            self.image = pygame.Surface(size)
            self.image.fill(stats["color"])

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = floor_top

        #health and defence scale with the wave
        self.max_hp = int(stats["hp"] * ENEMY_HP_SCALE ** (wave - 1))
        self.hp = self.max_hp
        self.defence = stats["defence"] * ENEMY_DEFENCE_SCALE ** (wave - 1)
        self.speed = stats["speed"]
        self.coin_value = stats["coins"]
        self.contact_damage = stats["damage"]
        self.direction = direction

        #the boss has its own sink, slimes use SLIME_SINK
        self.sink = stats.get("sink", SLIME_SINK)

    def update(self):
        self.rect.x += self.speed * self.direction

        if self.rect.left <= 0:
            self.rect.left = 0
            self.direction = 1

        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH
            self.direction = -1

#minecart sprites
minecart1 = "IronKart.png"
minecart2 = "mechKart.png"
minecart3 = "FartKart.png"

#players + enemies
player = Player()
player.rect.x = player_pos[0]
player.rect.y = player_pos[1]

enemies = pygame.sprite.Group()
