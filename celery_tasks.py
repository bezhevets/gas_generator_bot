import os
from datetime import datetime

from celery import Celery
from dotenv import load_dotenv

from telegram_bot.utils import write_start_time

load_dotenv()

app = Celery("celery_tasks", broker=os.getenv("CELERY_BROKER_URL"), backend=os.getenv("СELERY_RESULT_BACKEND"))


@app.task(name="start_generator")
def start_generator_task(start_time: datetime):
    return write_start_time(start_time)
