import os
from datetime import datetime

from celery import Celery
from dotenv import load_dotenv

from telegram_bot.utils import write_start_time, write_stop_time, log_oil_change_time

load_dotenv()

app = Celery("celery_tasks", broker=os.getenv("CELERY_BROKER_URL"), backend=os.getenv("СELERY_RESULT_BACKEND"))


@app.task(name="start_generator")
def start_generator_task(start_time: datetime):
    return write_start_time(start_time)


@app.task(name="stop_generator")
def stop_generator_task(stop_time: datetime):
    return write_stop_time(stop_time)


@app.task(name="change_oil")
def change_oil_task(stop_time: datetime):
    return log_oil_change_time(stop_time)
