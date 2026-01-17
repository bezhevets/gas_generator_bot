import os
from functools import wraps

from dotenv import load_dotenv

from telegram_bot.bot_instance import bot

load_dotenv()

USERS = {
    int(os.getenv("ADMIN_ID")): "admin",
}

ROLE_LEVEL = {"viewer": 0, "operator": 1, "admin": 2}


def get_role(message) -> str:
    return USERS.get(message.from_user.id, "viewer")


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
