"""HTTP response helpers for formatting JSON and binary payloads."""
from __future__ import annotations

import json
from http import HTTPStatus
from typing import Any, Mapping


def send_json(handler: Any, status: HTTPStatus, payload: Mapping[str, Any]) -> None:
    """Send JSON response with correct headers and status code."""
    body = json.dumps(payload, allow_nan=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, Accept")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def send_file(
    handler: Any,
    data: bytes,
    content_type: str,
    filename: str | None = None,
) -> None:
    """Send binary file response (e.g. Excel export)."""
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", content_type)
    if filename:
        handler.send_header("Content-Disposition", f'attachment; filename="{filename}"')
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)
