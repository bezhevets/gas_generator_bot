import os
from datetime import datetime

import telebot
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv("TG_TOKEN"))

HELP_TEXT = (
    "Доступні команди:\n"
    "/start - привітання\n"
    "/help - список команд\n"
    "/ping - перевірка\n"
    "\n"
    "/start_generator - фіксація часу запуску генератора\n"
    "/stop_generator - фіксація часу зупинки генератора\n"
    "/stat - статистика\n"
)


def get_display_name(message: telebot.types.Message) -> str:
    u = message.from_user
    if u.first_name:
        return u.first_name
    if u.username:
        return f"@{u.username}"
    return "друг"


def format_gen_message(action: str) -> str:
    time_str = datetime.now().strftime("%H:%M")
    if action == "start":
        return f"✅ **Генератор запущено**\n🕒 Час: {time_str}"
    if action == "stop":
        return f"🛑 **Генератор зупинено**\n🕒 Час: {time_str}"
    return f"ℹ️ Подія генератора\n🕒 Час: {time_str}"


@bot.message_handler(commands=["start"])
def send_welcome(message):
    name = get_display_name(message)
    bot.send_message(message.chat.id, f"Привіт, {name}!\n\n{HELP_TEXT}")


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.send_message(message.chat.id, HELP_TEXT)


@bot.message_handler(commands=["ping"])
def ping(message):
    bot.reply_to(message, "pong ✅")


@bot.message_handler(commands=["start_generator"])
def start_generator(message):
    # TODO: Google Sheets
    msg = format_gen_message("start")
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")


@bot.message_handler(commands=["stop_generator"])
def stop_generator(message):
    # TODO: Google Sheets
    msg = format_gen_message("stop")
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")


@bot.message_handler(commands=["stat"])
def stop_generator(message):
    # TODO: stats
    msg = (
        "📊 **Статистика генератора**\n\n"
        "⏱️ **Мотогодин:** 40 год.\n"
        f"🛢️ **Остання заміна мастила:** {datetime.now().strftime('%d.%m.%Y')}\n"
        "🧰 **Наступна заміна:** через 14 мотогодин\n\n"
        f"🚀 **Останній запуск:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        "🔁 **Усього запусків:** 5\n"
    )
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")


@bot.message_handler(func=lambda m: True, content_types=["text"])
def fallback(message):
    bot.reply_to(message, "Вибач, я не маю відповіді на твою команду.\nЯ розумію лише команди.\n\n" + HELP_TEXT)


bot.infinity_polling()
