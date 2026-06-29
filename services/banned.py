import json
import os
from config import BANNED_USERS_FILE

def load_banned_users():
    if not os.path.exists(BANNED_USERS_FILE):
        return set()
    with open(BANNED_USERS_FILE, "r") as f:
        return set(json.load(f))

def save_banned_users(users_set):
    with open(BANNED_USERS_FILE, "w") as f:
        json.dump(list(users_set), f)

# Load banned users into memory when the bot starts
banned_users = load_banned_users()
