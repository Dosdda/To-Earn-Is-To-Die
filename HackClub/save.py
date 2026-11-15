import json
import os
import state
from settings import FINAL_WAVE, KARTS

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "savegame.json")

#starting values before any save loads
START_VALUES = {
    "wave": state.wave,
    "highest_wave": state.highest_wave,
    "coins": state.coins,
    "max_health": state.max_health,
    "max_defence": state.max_defence,
    "damage": state.damage,
    "owned_karts": list(state.owned_karts),
    "selected_kart": state.selected_kart,
}

def reset_save():
    for name, value in START_VALUES.items():
        setattr(state, name, list(value) if isinstance(value, list) else value)

    state.health = state.max_health
    state.defence = state.max_defence
    save_game()

def save_game():
    data = {
        "wave": state.wave,
        "highest_wave": state.highest_wave,
        "coins": state.coins,
        "max_health": state.max_health,
        "max_defence": state.max_defence,
        "damage": state.damage,
        "owned_karts": state.owned_karts,
        "selected_kart": state.selected_kart,
    }

    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except OSError:
        print("Could not save the game")

def load_game():
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return

    state.wave = min(max(int(data.get("wave", 1)), 1), FINAL_WAVE)
    state.highest_wave = min(max(int(data.get("highest_wave", state.wave)), state.wave), FINAL_WAVE)
    state.coins = data.get("coins", 0)
    state.max_health = data.get("max_health", state.max_health)
    state.max_defence = data.get("max_defence", state.max_defence)
    state.damage = data.get("damage", state.damage)
    state.health = state.max_health
    state.defence = state.max_defence

    #keep valid karts and always own the starter
    owned = [i for i in data.get("owned_karts", [0]) if isinstance(i, int) and 0 <= i < len(KARTS)]
    if 0 not in owned:
        owned.append(0)
    state.owned_karts = owned

    selected = data.get("selected_kart", 0)
    state.selected_kart = selected if selected in owned else 0