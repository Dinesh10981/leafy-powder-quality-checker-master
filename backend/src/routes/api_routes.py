"""API routes dispatcher for sensor gateway endpoints."""
from __future__ import annotations

from http import HTTPStatus
from typing import Any
from urllib.parse import urlparse

from ..controllers.sensor_controller import SensorController
from ..middleware.cors import handle_cors_preflight
from ..utils.response import send_json


def dispatch_api_route(
    handler: Any,
    controller: SensorController,
    method: str,
    path: str,
) -> bool:
    """
    Route API requests to appropriate controller actions.
    Returns True if an API route was handled, False if unhandled (e.g. static file).
    """
    route = urlparse(path).path.rstrip("/") or "/"

    if method == "OPTIONS":
        handle_cors_preflight(handler)
        return True

    if method == "GET":
        if route in ("/api/status", "/status"):
            controller.get_status(handler)
            return True
        if route in ("/api/history", "/history"):
            controller.get_history(handler)
            return True
        if route in ("/api/scan", "/scan"):
            controller.post_scan(handler)
            return True
        if route == "/api/export":
            controller.export_excel(handler)
            return True

    elif method == "POST":
        if route in ("/api/scan", "/scan"):
            controller.post_scan(handler)
            return True
        if route.startswith("/api/"):
            send_json(handler, HTTPStatus.NOT_FOUND, {"ok": False, "error": f"Endpoint not found: {route}"})
            return True

    elif method == "DELETE":
        if route in ("/api/history", "/clear"):
            controller.clear_history(handler)
            return True
        if route.startswith("/api/"):
            send_json(handler, HTTPStatus.NOT_FOUND, {"ok": False, "error": f"Endpoint not found: {route}"})
            return True

    return False
