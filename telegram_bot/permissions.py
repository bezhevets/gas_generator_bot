import json
import os
from functools import wraps

from dotenv import load_dotenv

from telegram_bot.bot_instance import bot

load_dotenv()

ROLES_FILE = "roles.json"

# .env: ADMIN_ID=123456789
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not ADMIN_ID:
    raise RuntimeError("ADMIN_ID is not set in environment")

ROLE_LEVEL = {"viewer": 0, "operator": 1, "admin": 2}
VALID_ROLES = set(ROLE_LEVEL.keys())


def load_roles() -> dict:
    if not os.path.exists(ROLES_FILE):
        return {}
    try:
        with open(ROLES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_roles(data: dict) -> None:
    tmp = ROLES_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, ROLES_FILE)  # атомарна заміна


def get_role_by_user_id(user_id: int) -> str:
    if user_id == ADMIN_ID:
        return "admin"
    data = load_roles()
    return data.get(str(user_id), {}).get("role", "viewer")


def get_role(message) -> str:
    return get_role_by_user_id(message.from_user.id)


def require_role(min_role: str = "operator"):
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            role = get_role(message)
            if ROLE_LEVEL[role] < ROLE_LEVEL[min_role]:
                bot.reply_to(message, "⛔️ У вас немає доступу до цієї команди.")
                return
            return func(message, *args, **kwargs)

        return wrapper

    return decorator
