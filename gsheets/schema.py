"""Schema (model) for Google Sheets workbooks.

Define sheet names and their ordered columns here. Utilities will use this
schema to auto-create sheets and set header rows.
"""

from __future__ import annotations

# Ordered list of columns for each worksheet
SHEETS: dict[str, list[str]] = {
    "Статистика": [
        "Дата",
        "Час запуску",
        "Час стопу",
        "Мото години",
    ],
    "Течнічне обслуговування": ["Дата", "Інтервал заміни", "Залишок мотогодин"],
}
