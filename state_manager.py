import json
import os

STATE_FILE = "system_state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def update_fact(key, value):
    state = load_state()
    state[key] = value
    save_state(state)
    return state

def get_fact(key, default=None):
    state = load_state()
    return state.get(key, default)
