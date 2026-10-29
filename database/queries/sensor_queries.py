"""Sensor database queries and record extractors."""
from __future__ import annotations

from typing import Any
from ..models.sensor_record import SensorRecord


def get_next_sample_number(sheet: Any) -> int:
    """Find the next auto-incrementing sample ID."""
    numbers = [
        value for (value,) in sheet.iter_rows(min_row=2, max_col=1, values_only=True)
        if isinstance(value, (int, float))
    ]
    return int(max(numbers, default=0)) + 1


def count_records(sheet: Any) -> int:
    """Return total valid reading records in the sheet."""
    return sum(
        1 for (value,) in sheet.iter_rows(min_row=2, max_col=1, values_only=True)
        if value is not None
    )


def row_to_dict(sheet: Any, row: int) -> dict[str, Any]:
    """Convert an individual sheet row into a dictionary record."""
    cells = [sheet.cell(row, col).value for col in range(1, 15)]
    return SensorRecord.from_row_cells(cells).to_dict()


def fetch_history(sheet: Any, limit: int = 500) -> list[dict[str, Any]]:
    """Retrieve history records in reverse chronological order."""
    start = max(2, sheet.max_row - limit + 1)
    records = [row_to_dict(sheet, row) for row in range(start, sheet.max_row + 1)]
    return [record for record in reversed(records) if record["sample_no"]]


def delete_all_records(sheet: Any) -> None:
    """Clear all records from the sheet while keeping header row."""
    if sheet.max_row > 1:
        sheet.delete_rows(2, sheet.max_row - 1)
    for table in sheet.tables.values():
        table.ref = "A1:N2"
    sheet.auto_filter.ref = "A1:N1"
