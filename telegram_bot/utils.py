import os
from datetime import datetime, date

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


if __name__ == "__main__":
    write_start_time()
