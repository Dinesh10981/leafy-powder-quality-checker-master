"""Seed data script for sensor readings."""
from __future__ import annotations

from typing import Any

INITIAL_SEEDS = [
    {
        "date": "2026-08-27",
        "time": "21:06:02",
        "values": {"R": 95.67, "S": 68.5, "T": 9.27, "U": 15.13, "V": 22.46, "W": 16.36},
        "analysis": {
            "red_edge_average": 38.885,
            "nir_average": 17.9833,
            "lpqi": -0.3675,
            "quality": "Poor",
        },
        "sensor_url": "Imported reading",
    },
    {
        "date": "2026-08-27",
        "time": "21:35:04",
        "values": {"R": 11909.36, "S": 1487.57, "T": 1052.76, "U": 678.47, "V": 1026.35, "W": 563.93},
        "analysis": {
            "red_edge_average": 1270.165,
            "nir_average": 756.25,
            "lpqi": -0.2536,
            "quality": "Poor",
        },
        "sensor_url": "Imported reading",
    },
]


def seed_database(store: Any) -> int:
    """Seed sample records if database is empty."""
    if store.count() > 0:
        return 0

    count = 0
    for item in INITIAL_SEEDS:
        store.append(item["values"], item["analysis"], item["sensor_url"])
        count += 1
    return count
