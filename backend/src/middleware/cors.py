"""CORS middleware helpers for handling preflight requests."""
from __future__ import annotations

from http import HTTPStatus
from typing import Any

from ..utils.response import send_json


def handle_cors_preflight(handler: Any) -> None:
    """Handle HTTP OPTIONS preflight request."""
    send_json(handler, HTTPStatus.OK, {"ok": True})
