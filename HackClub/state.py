#values that change while playing

#player
player_velocity_y = 0
facing = 1
attack_time = -1000
attack_rect = None

#upgrades
health = 100
max_health = 100
defence = 100
max_defence = 100
damage = 5

#currency
coins = 0

#minekarts (positions in KARTS)
owned_karts = [0]
selected_kart = 0

#const
game_started = False
upgrades_open = False
game_over = False
game_over_time = 0
last_damage_time = 0

#waves
wave = 1
highest_wave = 1
wave_transition = False
wave_clear_time = 0
victory = False
victory_time = 0