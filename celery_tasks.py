import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

app = Celery("celery_tasks", broker=os.getenv("CELERY_BROKER_URL"), backend=os.getenv("СELERY_RESULT_BACKEND"))


@app.task
def add(x, y):
    return x + y
