"""Sensor communication service for acquiring spectral bands."""
from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..validators.sensor_validator import SensorValidationError, parse_sensor_payload


class SensorConnectionError(RuntimeError):
    """Network connection or timeout failure communicating with sensor hardware."""


class SensorClient:
    """HTTP client communicating with the ESP8266 spectral sensor."""

    def __init__(self, url: str, timeout_seconds: float = 10.0) -> None:
        self.url = url
        self.timeout_seconds = timeout_seconds

    def scan(self) -> dict[str, float]:
        """Request a scan from the sensor, decode, validate, and return the 6 bands."""
        try:
            request = Request(self.url, headers={"Accept": "application/json, text/plain"})
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = response.read().decode("utf-8", errors="replace")
        except TimeoutError as exc:
            raise SensorConnectionError(
                "The sensor timed out. Check its power, Wi-Fi, and IP address."
            ) from exc
        except HTTPError as exc:
            raise SensorConnectionError(f"Sensor returned HTTP {exc.code}.") from exc
        except URLError as exc:
            reason = "timed out" if isinstance(exc.reason, TimeoutError) else str(exc.reason)
            raise SensorConnectionError(f"Cannot connect to the sensor at {self.url}: {reason}") from exc

        try:
            return parse_sensor_payload(payload)
        except SensorValidationError as exc:
            raise SensorConnectionError(str(exc)) from exc
