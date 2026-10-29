"""Sensor reading schema definitions and data representations."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

BANDS = ("R", "S", "T", "U", "V", "W")

HEADERS = (
    "Sample No.",
    "Date",
    "Time",
    "R - 610 nm",
    "S - 680 nm",
    "T - 730 nm",
    "U - 760 nm",
    "V - 810 nm",
    "W - 860 nm",
    "Red-edge avg",
    "NIR avg",
    "LPQI",
    "Quality",
    "Sensor URL",
)

COLUMN_WIDTHS = (12, 13, 11, 14, 14, 14, 14, 14, 14, 16, 14, 11, 12, 34)


@dataclass
class SensorRecord:
    sample_no: int
    date: str
    time: str
    R: float
    S: float
    T: float
    U: float
    V: float
    W: float
    red_edge_average: float
    nir_average: float
    lpqi: float
    quality: str
    sensor_url: str = ""
    ml_prediction: str = ""
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row_cells(cls, cells: list[Any]) -> "SensorRecord":
        return cls(
            sample_no=int(cells[0]) if cells[0] is not None else 0,
            date=str(cells[1] or ""),
            time=str(cells[2] or ""),
            R=float(cells[3] or 0.0),
            S=float(cells[4] or 0.0),
            T=float(cells[5] or 0.0),
            U=float(cells[6] or 0.0),
            V=float(cells[7] or 0.0),
            W=float(cells[8] or 0.0),
            red_edge_average=float(cells[9] or 0.0),
            nir_average=float(cells[10] or 0.0),
            lpqi=float(cells[11] or 0.0),
            quality=str(cells[12] or ""),
            sensor_url=str(cells[13] or ""),
        )
