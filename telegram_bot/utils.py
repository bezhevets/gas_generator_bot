import os
from datetime import datetime, date, timedelta

import pandas as pd
from dotenv import load_dotenv

from gsheets.sheets_service import read_google_sheet, upload_dataframe_to_worksheet

load_dotenv()

GOOGLE_SHEET = os.getenv("GOOGLE_SHEET")

STAT = "Статистика"


def write_start_time(time_now: datetime) -> bool:
    # TODO: refactor
    workbook = read_google_sheet(GOOGLE_SHEET)
    worksheet = workbook.worksheet(STAT)
    records = worksheet.get_all_records()
    print(records)
    columns = worksheet.get_values()[0]
    print(columns)
    last_row = records[-1]
    row_date = datetime.strptime(last_row["Дата"], "%d.%m.%Y").date()
    is_today = row_date == date.today()
    if last_row["Час запуску"]:
        empty_row = dict.fromkeys(columns, "")
        empty_row["Дата"] = time_now.strftime("%d.%m.%Y")
        empty_row["Час запуску"] = time_now.strftime("%d.%m.%Y %H:%M")
        records.append(empty_row)

    upload_dataframe_to_worksheet(worksheet, pd.DataFrame(records))
    return True


def moto_hours(data: dict):
    start = data.get("Час запуску")
    stop = data.get("Час стопу")
    if not start or not stop:
        return ""

    start = datetime.strptime(start, "%d.%m.%Y %H:%M")
    stop = datetime.strptime(stop, "%d.%m.%Y %H:%M")

    if stop < start:  # перехід через північ
        stop += timedelta(days=1)

    delta = stop - start
    total_minutes = int(delta.total_seconds() // 60)
    h, m = divmod(total_minutes, 60)
    return f"{h}:{m:02d}"


def write_stop_time(time_now: datetime) -> bool:
    # TODO: refactor
    workbook = read_google_sheet(GOOGLE_SHEET)
    worksheet = workbook.worksheet(STAT)
    records = worksheet.get_all_records()
    last_row = records[-1]
    if not last_row["Час стопу"]:
        last_row["Час стопу"] = time_now.strftime("%d.%m.%Y %H:%M")
        last_row["Мото години"] = moto_hours(last_row)

    upload_dataframe_to_worksheet(worksheet, pd.DataFrame(records))
    return True
