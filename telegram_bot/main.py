import json
import os
from datetime import datetime

import telebot
from telebot import types

from celery_tasks import start_generator_task, stop_generator_task, change_oil_task, statistics_task
from telegram_bot.bot_instance import bot
from telegram_bot.permissions import (
    require_role,
    VALID_ROLES,
    load_roles,
    save_roles,
    get_role_by_user_id,
    ROLE_LEVEL,
)

HELP_TEXT = (
    "Доступні команди:\n"
    "/start - привітання\n"
    "/help - список команд\n"
    "/ping - перевірка\n"
    "/info - інфо\n"
    "\n"
    "/myid - дізнатись свій user_id\n"
    "\n"
    "/start_generator - фіксація часу запуску генератора\n"
    "/stop_generator - фіксація часу зупинки генератора\n"
    "/change_oil - фіксація дати заміни мастила\n"
    "/stat - статистика\n"
)


@bot.message_handler(commands=["myid"])
def myid(message):
    bot.reply_to(message, f"Ваш user_id: {message.from_user.id}")


def get_display_name(message: telebot.types.Message) -> str:
    u = message.from_user
    if u.first_name:
        return f"{u.first_name}{' ' + u.last_name if u.last_name else ''}"
    if u.username:
        return f"@{u.username}"
    return "друг"


def format_gen_message(action: str, time_now: datetime) -> str:
    time_str = time_now.strftime("%H:%M")
    if action == "start":
        return f"✅ **Генератор запущено**\n🕒 Час: {time_str}"
    if action == "stop":
        return f"🛑 **Генератор зупинено**\n🕒 Час: {time_str}"
    return f"ℹ️ Подія генератора\n🕒 Час: {time_str}"


@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id
    role = get_role_by_user_id(user_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_help = types.KeyboardButton("Допомога")
    btn_start = types.KeyboardButton("🟢START")
    btn_stop = types.KeyboardButton("🔴STOP")

    if ROLE_LEVEL[role] >= ROLE_LEVEL["operator"]:
        markup.add(btn_start, btn_stop)

    markup.add(btn_help)

    name = get_display_name(message)

    data = load_roles()
    user = data.get(str(user_id))
    if role != "admin" and not user:
        data[str(user_id)] = {"role": role, "name": name}
        save_roles(data)

    bot.send_message(message.chat.id, f"Привіт, {name}!\n\n{HELP_TEXT}", reply_markup=markup)


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.send_message(message.chat.id, HELP_TEXT)


@bot.message_handler(commands=["ping"])
def ping(message):
    bot.reply_to(message, "pong ✅")


@bot.message_handler(commands=["start_generator"])
@require_role("operator")
def start_generator(message):
    time_now = datetime.now()
    start_generator_task.delay(time_now)
    msg = format_gen_message("start", time_now)
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")


@bot.message_handler(commands=["stop_generator"])
@require_role("operator")
def stop_generator(message):
    time_now = datetime.now()
    stop_generator_task.delay(time_now)
    msg = format_gen_message("stop", time_now)
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")


@bot.message_handler(commands=["change_oil"])
@require_role("operator")
def oil_change_time(message):
    date_today = datetime.now()
    change_oil_task.delay(date_today)
    msg = f"✅ **Дату заміни мастила зафіксовано**\n📆 Дата: {date_today.strftime('%d.%m.%Y')}"
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def info(message):
    contacts = json.loads(os.getenv("CONTACTS_JSON"))
    c_text = ""
    if contacts:
        c_text += f"*📞Контакти:*\n"
        for contact in contacts:
            for k, v in contact.items():
                c_text += f"*{k}:* {v}\n"
            c_text += "\n"
        c_text += "\n"
    table = os.getenv("GOOGLE_SHEET")
    if table:
        c_text += f"*Таблиця записів*:\n🔗[Відкрити таблицю ->]({table})\n"
    bot.send_message(message.chat.id, c_text, parse_mode="Markdown")


@bot.message_handler(commands=["stat"])
def stat(message):
    msg = "Збираю дані з таблиці, протягом 1-2 хв я надішлю статистику."
    statistics_task.delay(message.chat.id)
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")


@bot.message_handler(commands=["grant"])
@require_role("admin")
def grant_role(message):
    parts = (message.text or "").split()

    if len(parts) != 4 or not parts[1].isdigit():
        bot.reply_to(
            message, f"Використання:\n/grant <user_id> <name> <role>\n Доступні ролі: {', '.join(sorted(VALID_ROLES))}"
        )
        return

    target_id = int(parts[1])
    name = parts[2].strip().capitalize()
    role = parts[3].strip().lower()
    if role not in VALID_ROLES:
        bot.reply_to(message, f"Невідома роль. Доступні: {', '.join(sorted(VALID_ROLES))}")
        return

    data = load_roles()
    data[str(target_id)] = {"role": role, "name": name}
    save_roles(data)
    bot.reply_to(message, f"✅ Роль для {target_id}/{name} встановлено: {role}")


@bot.message_handler(func=lambda m: True, content_types=["text"])
def fallback(message):
    if message.text == "Допомога":
        send_help(message)
    elif message.text == "🟢START":
        start_generator(message)
    elif message.text == "🔴STOP":
        stop_generator(message)
    else:
        bot.reply_to(message, "Вибач, я не маю відповіді на твою команду.\nЯ розумію лише команди.\n\n" + HELP_TEXT)


if __name__ == "__main__":
    bot.infinity_polling()
