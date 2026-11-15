import os
import pygame

pygame.init()

#pygame intialize
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("To Earn is To Die")
clock = pygame.time.Clock()

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)

#player settings
player_size = (50, 50)
player_pos = [100, 500]
player_speed = 5
gravity = 0.5
jump_strength = -10
ground_y = 450

#attack settings
ATTACK_COOLDOWN = 400
ATTACK_RANGE = 60

#wave settings
FINAL_WAVE = 6
ADVANCE_ON_DEATH = False #keep false

#enemy scaling 
ENEMY_HP_SCALE = 1.2
ENEMY_DEFENCE_SCALE = 1.2

#coin settings
COIN_BONUS = 5

#upgrade settings
UPGRADE_COST = 10
UPGRADE_COST_STEP = 5

file1 = 'HackClub/01.OverworldDay.mp3'
file2 = 'HackClub/08.Corruption.mp3'


#minekarts
#first one is the starter kart
KARTS = [
    {"name": "IronKart", "image": "HackClub/IronKart.png", "cost": 0, "color": (255, 0, 0)},
    {"name": "MechKart", "image": "HackClub/mechKart.png", "cost": 250, "color": (0, 150, 255)},
    {"name": "FartKart", "image": "HackClub/FartKart.png", "cost": 500, "color": (255, 200, 0)},
]

#font settings
FONT_PATH = "HackClub/8BIT.ttf"
FONT_SIZE = 20
BIG_FONT_SIZE = 50
MENU_FONT_SIZE = 20
MENU_TITLE_SIZE = 30

#use the default font if the file is missing
if not os.path.exists(FONT_PATH):
    FONT_PATH = None

#global font
game_font = pygame.font.Font(FONT_PATH, FONT_SIZE)
game_over_font = pygame.font.Font(FONT_PATH, BIG_FONT_SIZE)