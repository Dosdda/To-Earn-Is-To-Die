import pygame
import pygame_menu
from pygame_menu import themes
from settings import *
from sprites import player
from waves import spawn_wave
from save import save_game, reset_save
import state

#menu 
def start_the_game():
    state.game_started = True
    state.player_velocity_y = 0
    state.health = state.max_health
    state.defence = state.max_defence
    state.game_over = False
    state.victory = False
    state.upgrades_open = False
    state.wave_transition = False
    state.last_damage_time = 0

    player.rect.x = 100
    player.rect.y = ground_y

    spawn_wave(state.wave)

#upgraded
def upgrades():
    mainmenu._open(upgrade)

def health_price():
    return UPGRADE_COST + (state.max_health - 100) // 10 * UPGRADE_COST_STEP

def defence_price():
    return UPGRADE_COST + (state.max_defence - 100) // 10 * UPGRADE_COST_STEP

def damage_price():
    return UPGRADE_COST + (state.damage - 5) * UPGRADE_COST_STEP

def upgrade_health():
    price = health_price()
    if state.coins < price:
        return
    state.coins -= price
    state.max_health += 10
    state.health = state.max_health
    update_upgrade_menu()
    save_game()

def upgrade_defence():
    price = defence_price()
    if state.coins < price:
        return
    state.coins -= price
    state.max_defence += 10
    state.defence = state.max_defence
    update_upgrade_menu()
    save_game()

def upgrade_damage():
    price = damage_price()
    if state.coins < price:
        return
    state.coins -= price
    state.damage += 1
    update_upgrade_menu()
    save_game()

#minekarts
def karts_screen():
    mainmenu._open(karts_menu)

def buy_or_equip_kart(index):
    kart = KARTS[index]

    if index not in state.owned_karts:
        if state.coins < kart["cost"]:
            return
        state.coins -= kart["cost"]
        state.owned_karts.append(index)

    state.selected_kart = index
    player.set_kart(index)
    update_upgrade_menu()
    save_game()

def update_upgrade_menu():
    play_button.set_title(f"Play (Wave {state.wave})")
    coins_label.set_title(f"Coins: {state.coins}")
    karts_coins_label.set_title(f"Coins: {state.coins}")

    for i, kart in enumerate(KARTS):
        if i == state.selected_kart:
            kart_buttons[i].set_title(f"{kart['name']} - Equipped")
        elif i in state.owned_karts:
            kart_buttons[i].set_title(f"{kart['name']} - Owned (click to equip)")
        else:
            kart_buttons[i].set_title(f"{kart['name']} - {kart['cost']} coins")

    health_button.set_title(f"Health: {state.max_health} (+10) - {health_price()} coins")
    defence_button.set_title(f"Defence: {state.max_defence} (+10) - {defence_price()} coins")
    damage_button.set_title(f"Damage: {state.damage} (+1) - {damage_price()} coins")

def open_game_upgrades():
    state.upgrades_open = True

def close_game_upgrades():
    state.upgrades_open = False

#settings
reset_confirm = False

def settings_screen():
    global reset_confirm
    reset_confirm = False
    reset_button.set_title("Reset save")
    mainmenu._open(settings_menu)

def reset_save_button():
    global reset_confirm

    #first click asks, second click resets
    if not reset_confirm:
        reset_confirm = True
        reset_button.set_title("Are you sure? Click again")
        return

    reset_confirm = False
    reset_save()
    player.set_kart(state.selected_kart)
    update_upgrade_menu()
    reset_button.set_title("Save reset!")

#menu font
def make_theme(base):
    theme = base.copy()

    if FONT_PATH:
        theme.widget_font = FONT_PATH
        theme.title_font = FONT_PATH
        theme.widget_font_size = MENU_FONT_SIZE
        theme.title_font_size = MENU_TITLE_SIZE

    return theme

#maimenu 
mainmenu = pygame_menu.Menu("Welcome",WIDTH,HEIGHT,theme=make_theme(themes.THEME_SOLARIZED))

play_button = mainmenu.add.button(f"Play (Wave {state.wave})", start_the_game)
mainmenu.add.button("Upgrades", upgrades)
mainmenu.add.button("Minekarts", karts_screen)
mainmenu.add.button("Settings", settings_screen)
mainmenu.add.button("Quit", pygame_menu.events.EXIT)

upgrade = pygame_menu.Menu("Choose your upgrades",WIDTH, HEIGHT,theme=make_theme(themes.THEME_ORANGE))

#upgrade message
coins_label = upgrade.add.label(f"Coins: {state.coins}")
health_button = upgrade.add.button(f"Health: {state.max_health} (+10) - {UPGRADE_COST} coins",upgrade_health)
defence_button = upgrade.add.button(f"Defence: {state.max_defence} (+10) - {UPGRADE_COST} coins",upgrade_defence)
damage_button = upgrade.add.button(f"Damage: {state.damage} (+1) - {UPGRADE_COST} coins",upgrade_damage)

upgrade.add.button("Back", pygame_menu.events.BACK)

#minekart shop
karts_menu = pygame_menu.Menu("Minekarts",WIDTH, HEIGHT,theme=make_theme(themes.THEME_GREEN))

karts_coins_label = karts_menu.add.label(f"Coins: {state.coins}")

kart_buttons = []
for i, kart in enumerate(KARTS):
    kart_buttons.append(karts_menu.add.button(kart["name"], buy_or_equip_kart, i))

karts_menu.add.button("Back", pygame_menu.events.BACK)

#settings menu
settings_menu = pygame_menu.Menu("Settings",WIDTH, HEIGHT,theme=make_theme(themes.THEME_BLUE))

reset_button = settings_menu.add.button("Reset save", reset_save_button)

settings_menu.add.button("Back", pygame_menu.events.BACK)

arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size=(10, 15))