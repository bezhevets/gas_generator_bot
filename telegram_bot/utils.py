import os
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv

from gsheets.sheets_service import (
    read_google_sheet,
    upload_dataframe_to_worksheet,
    get_or_create_worksheet_with_headers,
)
from gsheets.schema import SHEETS
from telegram_bot.bot_instance import bot

load_dotenv()

GOOGLE_SHEET = os.getenv("GOOGLE_SHEET")

STAT = "Статистика"
TO = "Течнічне обслуговування"


def write_start_time(time_now: datetime, chat_id: int) -> None:
    workbook = read_google_sheet(GOOGLE_SHEET)
    if not workbook:
        return
    worksheet = get_or_create_worksheet_with_headers(workbook, STAT, SHEETS.get(STAT))

    # Ensure we respect schema column order
    columns = SHEETS.get(STAT, [])

    records = worksheet.get_all_records()
    if records:
        last_row = records[-1]
        # If last row already has start time filled -> add a new row for a new start
        if last_row.get("Час запуску"):
            new_row = {col: "" for col in columns}
            new_row["Дата"] = time_now.strftime("%d.%m.%Y")
            new_row["Час запуску"] = time_now.strftime("%d.%m.%Y %H:%M")
            records.append(new_row)
        else:
            # If start is empty, fill it in the last row
            last_row["Дата"] = time_now.strftime("%d.%m.%Y")
            last_row["Час запуску"] = time_now.strftime("%d.%m.%Y %H:%M")
    else:
        # No data yet – create the very first row
        new_row = {col: "" for col in columns}
        new_row["Дата"] = time_now.strftime("%d.%m.%Y")
        new_row["Час запуску"] = time_now.strftime("%d.%m.%Y %H:%M")
        records.append(new_row)

    df = pd.DataFrame(records)
    upload_dataframe_to_worksheet(worksheet, df)

    msg = "✅ Запис додано"
    bot.send_message(chat_id, msg, parse_mode="Markdown")


def moto_hours(data: dict) -> str:
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


def hm_to_minutes(hm: str) -> int:
    h, m = hm.strip().split(":")[:2]
    return int(h) * 60 + int(m)


def remaining_motor_hours(moto_hm: str, remaining_hours: str) -> str:
    new_remaining_minutes = hm_to_minutes(remaining_hours) - hm_to_minutes(moto_hm)
    total_minutes = max(0, new_remaining_minutes)
    h, m = divmod(total_minutes, 60)
    return f"{h}:{m:02d}"


def write_stop_time(time_now: datetime, chat_id: int) -> None:
    workbook = read_google_sheet(GOOGLE_SHEET)
    if not workbook:
        return
    worksheet = get_or_create_worksheet_with_headers(workbook, STAT, SHEETS.get(STAT))
    records = worksheet.get_all_records()

    if records:
        last_row = records[-1]
        if not last_row.get("Час стопу"):
            last_row["Час стопу"] = time_now.strftime("%d.%m.%Y %H:%M")
            moto_h = moto_hours(last_row)
            last_row["Мотогодини"] = moto_h
            try:
                worksheet_to = get_or_create_worksheet_with_headers(workbook, TO, SHEETS.get(TO))
                records_to = worksheet_to.get_all_records()
                if not records_to:
                    log_oil_change_time(time_now, chat_id)
                    worksheet_to = get_or_create_worksheet_with_headers(workbook, TO, SHEETS.get(TO))
                    records_to = worksheet_to.get_all_records()

                last_row_to = records_to[-1]
                last_row_to["Залишок мотогодин"] = remaining_motor_hours(moto_h, last_row_to["Залишок мотогодин"])
                df_to = pd.DataFrame(records_to)
                upload_dataframe_to_worksheet(worksheet_to, df_to)
                msg = f"✅ Запис додано\nПрацював: *{moto_h}*"
            except Exception as e:
                print(f"Error get remaining_motor_hours: {e}")
                msg = f"Сталась помилка: {e}"
        else:
            msg = "Останній запис уже містить час зупинки"
    else:
        msg = "Не отримано даних з таблиці"

    df = pd.DataFrame(records)
    upload_dataframe_to_worksheet(worksheet, df)

    bot.send_message(chat_id, msg, parse_mode="Markdown")


def log_oil_change_time(today: datetime, chat_id: int) -> None:
    workbook = read_google_sheet(GOOGLE_SHEET)
    if not workbook:
        return
    worksheet = get_or_create_worksheet_with_headers(workbook, TO, SHEETS.get(TO))
    records = worksheet.get_all_records()

    columns = SHEETS.get(TO, [])

    oil_interval = os.getenv("OIL_INTERVAL")
    new_row = {col: "" for col in columns}
    new_row["Дата"] = today.strftime("%d.%m.%Y")
    new_row["Інтервал заміни"] = oil_interval
    new_row["Залишок мотогодин"] = f"{oil_interval}:00"
    records.append(new_row)

    df = pd.DataFrame(records)
    upload_dataframe_to_worksheet(worksheet, df)
    msg = "✅ Запис додано"
    bot.send_message(chat_id, msg, parse_mode="Markdown")


def get_statistic(chat_id: int) -> None:
    workbook = read_google_sheet(GOOGLE_SHEET)
    if not workbook:
        return
    worksheet_to = get_or_create_worksheet_with_headers(workbook, TO, SHEETS.get(TO))
    records_to = worksheet_to.get_all_records()
    last_row_to = records_to[-1]

    worksheet_stat = get_or_create_worksheet_with_headers(workbook, STAT, SHEETS.get(STAT))
    records_stat = worksheet_stat.get_all_records()
    last_row_stat = records_stat[-1]

    total_moto_hours = sum([hm_to_minutes(i["Мотогодини"]) for i in records_stat if i["Мотогодини"]])

    remaining = last_row_to["Залишок мотогодин"]  # скільки мотогодин залишилось
    bar_total = 10  # скільки "клітинок" у барі (довжина)
    interval = int(os.getenv("OIL_INTERVAL"))  # інтервал заміни в мотогодинах
    used = interval - int(remaining.strip().split(":")[0])
    filled = round((used / interval) * bar_total)
    bar = "🟫" * filled + "⬜️" * (bar_total - filled)

    msg = (
        "📊 *Статистика генератора*\n\n"
        "🧰 *Заміна мастила*\n"
        f"{bar}\n"
        f"Залишилось: *{remaining}* мотогодин\n\n"
        f"🛢️ *Остання заміна масла:* {last_row_to['Дата']}\n"
        f"🛢️ *Всього замін масла:* {len(records_to)}\n\n"
        f"🚀 *Останній запуск:* {last_row_stat['Час запуску']}\n"
        f"🔁 *Усього запусків:* {len(records_stat)}\n"
        f"⏱️ *Всього мотогодин:* {total_moto_hours // 60} год.\n"
    )
    bot.send_message(chat_id, msg, parse_mode="Markdown")
