import time
from pathlib import Path

import gspread
import gspread_dataframe
import pandas as pd

ROOT_FOLDER = Path(__file__).parent

GOOGLE_SERVICE_ACCOUNT = Path(ROOT_FOLDER, "service_account.json")


def get_gspread_service(path_to_config: Path | str = GOOGLE_SERVICE_ACCOUNT):
    return gspread.service_account(path_to_config)


def read_google_sheet(google_sheet_url: str) -> gspread.Spreadsheet | None:
    try:
        client = get_gspread_service()
        workbook = client.open_by_url(google_sheet_url)
        return workbook
    except Exception as e:
        # TODO: read_google_sheet exception handler
        print(e)
        # logger.exception(f"Error read_google_sheet: {e}")
        return


def get_or_create_worksheet(workbook: gspread.Spreadsheet, sheet_name: str) -> gspread.Worksheet:
    try:
        worksheet = workbook.worksheet(sheet_name)
        return worksheet
    except gspread.exceptions.WorksheetNotFound:
        worksheet = workbook.add_worksheet(title=sheet_name, rows=100, cols=40)
        return worksheet


def upload_dataframe_to_worksheet(worksheet: gspread.Worksheet, dataframe: pd.DataFrame) -> gspread.Worksheet:
    for _ in range(10):
        try:
            gspread_dataframe.set_with_dataframe(worksheet, dataframe, allow_formulas=False)
            worksheet.format("1", {"textFormat": {"bold": True}})
            return worksheet
        except gspread.exceptions.APIError as error:
            # logger.exception(f"Error in upload_dataframe_to_worksheet: {error}")
            time.sleep(6.1)
    return worksheet
