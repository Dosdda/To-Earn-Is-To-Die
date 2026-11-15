import random
import pygame
from settings import *
from sprites import player, enemies, Enemy, SLIME_STATS, BOSS_STATS
from save import save_game
import state

def spawn_wave(wave):
    enemies.empty()

    #wave 6 is the boss
    if wave >= FINAL_WAVE:
        enemies.add(Enemy(BOSS_STATS, WIDTH - 200, -1, wave))
        return

    #later waves mix in the newer slimes
    for i in range(wave + 2):
        stats = SLIME_STATS[random.randrange(min(wave, len(SLIME_STATS)))]
        x = random.randint(350, WIDTH - player_size[0])
        enemies.add(Enemy(stats, x, random.choice([-1, 1]), wave))

def change_wave(step):
    #-1 goes back, 1 goes forward (up to the unlocked wave)
    new_wave = state.wave + step

    if new_wave < 1 or new_wave > state.highest_wave:
        return

    state.wave = new_wave
    state.wave_transition = False
    spawn_wave(state.wave)
    save_game()

def player_attack():
    now = pygame.time.get_ticks()

    if now - state.attack_time < ATTACK_COOLDOWN:
        return

    state.attack_time = now

    if state.facing == 1:
        state.attack_rect = pygame.Rect(player.rect.right, player.rect.y, ATTACK_RANGE, player.rect.height)
    else:
        state.attack_rect = pygame.Rect(player.rect.left - ATTACK_RANGE, player.rect.y, ATTACK_RANGE, player.rect.height)

    for enemy in enemies.sprites():
        if state.attack_rect.colliderect(enemy.rect):
            #defence cuts damage (minimum 1)
            dealt = max(1, int(state.damage * 100 / (100 + enemy.defence)))
            enemy.hp -= dealt

            if enemy.hp <= 0:
                state.coins += enemy.coin_value + COIN_BONUS
                enemy.kill()
                save_game()