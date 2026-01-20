import os
from datetime import datetime

from celery import Celery
from dotenv import load_dotenv

from telegram_bot.utils import write_start_time, write_stop_time, log_oil_change_time, get_statistic

load_dotenv()

app = Celery("celery_tasks", broker=os.getenv("CELERY_BROKER_URL"), backend=os.getenv("CELERY_RESULT_BACKEND"))


@app.task(name="start_generator", queue="gasgen")
def start_generator_task(start_time: datetime, chat_id: int) -> None:
    return write_start_time(start_time, chat_id)


@app.task(name="stop_generator", queue="gasgen")
def stop_generator_task(stop_time: datetime, chat_id: int) -> None:
    return write_stop_time(stop_time, chat_id)


@app.task(name="change_oil", queue="gasgen")
def change_oil_task(stop_time: datetime, chat_id: int) -> None:
    return log_oil_change_time(stop_time, chat_id)


@app.task(name="statistics", queue="gasgen")
def statistics_task(chat_id: int) -> None:
    return get_statistic(chat_id)
