"""Controller for sensor analysis, status, and Excel database endpoints."""
from __future__ import annotations

import threading
from datetime import datetime
from http import HTTPStatus
from typing import Any

from database.connection.excel_store import DatabaseStorageError
from ..services.analysis_service import AnalysisCalculationError, analyze_bands
from ..services.sensor_service import SensorConnectionError
from ..utils.response import send_file, send_json


class SensorController:
    """Manages application state and coordinates sensor services with persistence."""

    def __init__(self, settings: Any, sensor: Any, store: Any, model: Any | None = None) -> None:
        self.settings = settings
        self.sensor = sensor
        self.store = store
        self.model = model
        self.last_scan_ok: bool | None = None
        self.last_scan_error: str | None = None
        self.last_scan_time: str | None = None
        self.scan_lock = threading.Lock()

    def scan(self) -> dict[str, Any]:
        """Perform a single sensor scan, analyze with ML model, and persist to Excel."""
        if not self.scan_lock.acquire(blocking=False):
            raise SensorConnectionError("A sensor scan is already in progress")
        try:
            values = self.sensor.scan()
            analysis = analyze_bands(values, model=self.model)
            record = self.store.append(values, analysis, self.settings.sensor_url)
            self.last_scan_ok, self.last_scan_error = True, None
            self.last_scan_time = f"{record['date']} {record['time']}"
            return {"ok": True, **record}
        except (SensorConnectionError, AnalysisCalculationError, DatabaseStorageError) as exc:
            self.last_scan_ok, self.last_scan_error = False, str(exc)
            self.last_scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            raise
        finally:
            self.scan_lock.release()

    def status(self) -> dict[str, Any]:
        """Return connectivity and system status."""
        return {
            "ok": True,
            "sensor_url": self.settings.sensor_url,
            "excel_file": str(self.settings.excel_file),
            "model_file": str(self.settings.model_file),
            "model_loaded": self.model is not None,
            "samples": self.store.count(),
            "last_scan_ok": self.last_scan_ok,
            "last_scan_error": self.last_scan_error,
            "last_scan_time": self.last_scan_time,
        }

    # HTTP Handler methods
    def get_status(self, handler: Any) -> None:
        send_json(handler, HTTPStatus.OK, self.status())

    def get_history(self, handler: Any) -> None:
        send_json(handler, HTTPStatus.OK, {"ok": True, "rows": self.store.history()})

    def post_scan(self, handler: Any) -> None:
        try:
            record = self.scan()
            send_json(handler, HTTPStatus.OK, record)
        except Exception as exc:
            send_json(handler, HTTPStatus.BAD_GATEWAY, {"ok": False, "error": str(exc)})

    def export_excel(self, handler: Any) -> None:
        try:
            data = self.store.export_bytes()
        except OSError as exc:
            send_json(handler, HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": str(exc)})
            return
        send_file(
            handler,
            data=data,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="sensor_data.xlsx",
        )

    def clear_history(self, handler: Any) -> None:
        self.store.clear()
        send_json(handler, HTTPStatus.OK, {"ok": True})
