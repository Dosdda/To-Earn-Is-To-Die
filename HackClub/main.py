import pygame
import sys
from settings import *
from sprites import *
from menus import *
from waves import spawn_wave, player_attack, change_wave
from save import save_game, load_game
import state

#main running loop
def main():
    #load the save
    load_game()
    player.set_kart(state.selected_kart)
    update_upgrade_menu()

    running = True

    while running:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                save_game()
                running = False

            if state.game_started and not state.game_over and not state.victory and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x and not state.upgrades_open:
                    player_attack()

                if event.key == pygame.K_q and not state.upgrades_open:
                    change_wave(-1)

                if event.key == pygame.K_e and not state.upgrades_open:
                    change_wave(1)

            if state.game_started and not state.game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if state.upgrades_open:
                    close_button = pygame.Rect(340, 400, 120, 40)

                    if close_button.collidepoint(event.pos):
                        close_game_upgrades()
                else:
                    upgrades_button = pygame.Rect(650, 20, 130, 40)

                    if upgrades_button.collidepoint(event.pos):
                        open_game_upgrades()

        if not state.game_started:
            screen.fill(BLACK)

            if mainmenu.is_enabled():
                mainmenu.update(events)
                mainmenu.draw(screen)

                selected = mainmenu.get_current().get_selected_widget()

                if selected:
                    arrow.draw(screen, selected)
        
        else:
            if state.wave >= FINAL_WAVE:
                screen.blit(boss_background, (0, 0))
            else:
                screen.blit(background, (0, 0))

            if not state.game_over and not state.victory:
                keys = pygame.key.get_pressed()

                if not state.upgrades_open:
                    if keys[pygame.K_LEFT]:
                        player.rect.x -= player_speed
                        state.facing = -1

                    if keys[pygame.K_RIGHT]:
                        player.rect.x += player_speed
                        state.facing = 1

                    if keys[pygame.K_SPACE] and player.rect.y >= ground_y:
                        state.player_velocity_y = jump_strength

                    state.player_velocity_y += gravity
                    player.rect.y += state.player_velocity_y

                    enemies.update()

                if player.rect.y >= ground_y:
                    player.rect.y = ground_y
                    state.player_velocity_y = 0

                if player.rect.x < 0:
                    player.rect.x = 0

                if player.rect.right > WIDTH:
                    player.rect.right = WIDTH

                current_time = pygame.time.get_ticks()

                for enemy in enemies:
                    if player.rect.colliderect(enemy.rect):
                        if current_time - state.last_damage_time >= 1000:
                            #defence cuts damage taken (minimum 1)
                            state.health -= max(1, int(enemy.contact_damage * 100 / state.max_defence))
                            state.last_damage_time = current_time
                        break

                #wave progress
                if state.wave_transition:
                    if current_time - state.wave_clear_time >= 1500:
                        state.wave_transition = False
                        spawn_wave(state.wave)

                elif len(enemies) == 0:
                    if state.wave >= FINAL_WAVE:
                        state.victory = True
                        state.victory_time = current_time
                        state.wave = 1
                        save_game()
                    else:
                        state.wave += 1
                        state.highest_wave = max(state.highest_wave, state.wave)
                        state.wave_transition = True
                        state.wave_clear_time = current_time
                        save_game()

                if state.health <= 0:
                    state.health = 0
                    state.game_over = True
                    state.game_over_time = current_time

                    if ADVANCE_ON_DEATH:
                        state.wave = min(state.wave + 1, FINAL_WAVE)
                        state.highest_wave = max(state.highest_wave, state.wave)

                    save_game()

            #sprites sink into the floor (drawing only)
            screen.blit(player.image, player.rect.move(0, KART_SINK))

            for enemy in enemies:
                screen.blit(enemy.image, enemy.rect.move(0, enemy.sink))

            for enemy in enemies:
                enemy_bar_fill = int((enemy.hp / enemy.max_hp) * enemy.rect.width)
                pygame.draw.rect(screen, GRAY, (enemy.rect.x, enemy.rect.y - 8 + enemy.sink, enemy.rect.width, 5))
                pygame.draw.rect(screen, RED, (enemy.rect.x, enemy.rect.y - 8 + enemy.sink, enemy_bar_fill, 5))

            if state.attack_rect and pygame.time.get_ticks() - state.attack_time < 100:
                pygame.draw.rect(screen, GRAY, state.attack_rect, 2)

            screen.blit(floors[state.wave - 1], (0, floor_top))

            health_bar_width = 200
            health_fill = int((state.health / state.max_health) * health_bar_width)

            screen.blit(health_icon, (20, 20))
            pygame.draw.rect(screen, GRAY, (60, 25, health_bar_width, 20))
            pygame.draw.rect(screen, RED, (60, 25, health_fill, 20))
            pygame.draw.rect(screen, BLACK, (60, 25, health_bar_width, 20), 2)

            health_text = game_font.render(f"{state.health}/{state.max_health}",True,WHITE)
            screen.blit(health_text, (265, 23))

            defence_bar_width = 200
            defence_fill = int((state.defence / state.max_defence) * defence_bar_width)

            screen.blit(defence_icon, (20, 55))
            pygame.draw.rect(screen, GRAY, (60, 60, defence_bar_width, 20))
            pygame.draw.rect(screen, WHITE, (60, 60, defence_fill, 20))
            pygame.draw.rect(screen, BLACK, (60, 60, defence_bar_width, 20), 2)

            defence_text = game_font.render(f"{state.defence}/{state.max_defence}",True,WHITE)
            screen.blit(defence_text, (265, 58))

            screen.blit(coin_icon, (20, 90))
            coin_text = game_font.render(str(state.coins),True,BLACK)
            screen.blit(coin_text, (60, 95))

            wave_label = "Boss" if state.wave >= FINAL_WAVE else f"Wave {state.wave}"
            wave_text = game_font.render(wave_label,True,BLACK)
            wave_text_rect = wave_text.get_rect(center=(WIDTH // 2 + 60, 35))
            screen.blit(wave_text, wave_text_rect)

            wave_hint = game_font.render(f"Q/E: wave (max {state.highest_wave})",True,BLACK)
            wave_hint_rect = wave_hint.get_rect(center=(WIDTH // 2 + 60, 65))
            screen.blit(wave_hint, wave_hint_rect)

            if state.wave_transition:
                cleared_text = game_font.render("Wave cleared!",True,BLACK)
                cleared_rect = cleared_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
                screen.blit(cleared_text, cleared_rect)

            upgrades_button = pygame.Rect(650, 20, 130, 40)
            pygame.draw.rect(screen, GRAY, upgrades_button)

            upgrades_text = game_font.render("Upgrades",True,WHITE)
            upgrades_text_rect = upgrades_text.get_rect(center=upgrades_button.center)
            screen.blit(upgrades_text, upgrades_text_rect)

            #upgrades
            if state.upgrades_open and not state.game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 220))
                screen.blit(overlay, (0, 0))

                title = game_font.render("Your upgrades",True,WHITE)

                health_upgrade_text = game_font.render(f"Health: {state.max_health}",True,WHITE)
                defence_text = game_font.render(f"Defence: {state.max_defence}",True,WHITE)
                damage_text = game_font.render(f"Damage: {state.damage}",True,WHITE)

                screen.blit(title, (300, 150))

                screen.blit(health_icon, (260, 210))
                screen.blit(health_upgrade_text, (300, 220))

                screen.blit(defence_icon, (260, 250))
                screen.blit(defence_text, (300, 260))

                screen.blit(damage_icon, (260, 290))
                screen.blit(damage_text, (300, 300))

                close_button = pygame.Rect(340, 400, 120, 40)
                pygame.draw.rect(screen, GRAY, close_button)

                close_text = game_font.render("Close",True,WHITE)
                close_text_rect = close_text.get_rect(center=close_button.center)
                screen.blit(close_text, close_text_rect)

            #victory
            if state.victory:
                screen.fill(BLACK)

                victory_text = game_over_font.render("YOU WIN", True, WHITE)
                victory_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
                screen.blit(victory_text, victory_rect)

                if pygame.time.get_ticks() - state.victory_time >= 3000:
                    state.game_started = False
                    state.victory = False
                    state.upgrades_open = False
                    update_upgrade_menu()
                    mainmenu.enable()

            #game over
            if state.game_over:
                screen.fill(BLACK)

                game_over_text = game_over_font.render("GAME OVER", True, RED)
                text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
                screen.blit(game_over_text, text_rect)

                time_left = 2 - (pygame.time.get_ticks() - state.game_over_time) / 1000
                time_left = max(0, time_left)

                countdown_text = game_font.render(f"Returning to main menu in {time_left:.1f}",True,WHITE)
                countdown_rect = countdown_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
                screen.blit(countdown_text, countdown_rect)

                if pygame.time.get_ticks() - state.game_over_time >= 2000:
                    state.game_started = False
                    state.game_over = False
                    state.upgrades_open = False
                    update_upgrade_menu()
                    mainmenu.enable()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
