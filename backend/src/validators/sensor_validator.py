"""Sensor data validation and payload parser."""
from __future__ import annotations

import json
import math
import re
from typing import Any, Mapping

from database.models.sensor_record import BANDS


class SensorValidationError(ValueError):
    """Validation failure in sensor readings or payload format."""


def parse_sensor_payload(payload: str | Mapping[str, Any]) -> dict[str, float]:
    """Parse JSON or text format (e.g. 'R,95.2 S,68.5 ...') into 6 bands."""
    candidate: Mapping[str, Any] | None = None
    raw_text = ""

    if isinstance(payload, Mapping):
        candidate = payload.get("data", payload)
    else:
        raw_text = payload.strip()
        try:
            decoded = json.loads(raw_text)
            if isinstance(decoded, Mapping):
                candidate = decoded.get("data", decoded)
        except json.JSONDecodeError:
            candidate = None

    parsed: dict[str, float] = {}
    if isinstance(candidate, Mapping):
        upper = {str(key).upper(): value for key, value in candidate.items()}
        for band in BANDS:
            if band in upper:
                try:
                    parsed[band] = float(upper[band])
                except (TypeError, ValueError):
                    pass

    if not parsed and raw_text:
        pattern = r"([RSTUVWrstuvw])\s*[,=:]\s*(-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
        for band, value in re.findall(pattern, raw_text):
            parsed[band.upper()] = float(value)

    missing = [band for band in BANDS if band not in parsed]
    if missing:
        raise SensorValidationError(f"Incomplete sensor payload; missing bands: {', '.join(missing)}")

    for band, value in parsed.items():
        if not math.isfinite(value) or value < 0:
            raise SensorValidationError(f"Band {band} must be a finite, non-negative value")

    return {band: parsed[band] for band in BANDS}
