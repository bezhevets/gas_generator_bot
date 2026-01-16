import os
from dotenv import load_dotenv
import telebot


load_dotenv()

TG_TOKEN = os.getenv("TG_TOKEN")
if not TG_TOKEN:
    raise RuntimeError("TG_TOKEN is not set in environment")

# Single shared TeleBot instance for the whole app
bot = telebot.TeleBot(TG_TOKEN)
