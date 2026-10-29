"""Application factory and HTTP request handler configuration."""
from __future__ import annotations

import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from database.connection.excel_store import ExcelStore
from .config.settings import Settings
from .controllers.sensor_controller import SensorController
from .routes.api_routes import dispatch_api_route
from .services.analysis_service import analyze_bands
from .services.ml_service import load_ml_model
from .services.sensor_service import SensorClient
from .utils.response import send_json


def resolve_frontend_file(web_root: Path, path: str) -> Path | None:
    """Resolve a URL path to an actual file inside the frontend directory structure."""
    clean_path = urlparse(path).path.lstrip("/")

    # Root mapping
    if not clean_path or clean_path == "index.html":
        candidates = [
            web_root / "src" / "pages" / "index.html",
            web_root / "pages" / "index.html",
            web_root / "index.html",
        ]
        for c in candidates:
            if c.exists():
                return c

    if clean_path == "dashboard.html":
        candidates = [
            web_root / "src" / "pages" / "dashboard.html",
            web_root / "pages" / "dashboard.html",
            web_root / "dashboard.html",
        ]
        for c in candidates:
            if c.exists():
                return c

    # Common script mappings
    if clean_path in ("dashboard.js", "scripts/dashboard.js"):
        candidates = [
            web_root / "src" / "scripts" / "dashboard.js",
            web_root / "scripts" / "dashboard.js",
            web_root / "dashboard.js",
        ]
        for c in candidates:
            if c.exists():
                return c

    if clean_path in ("auth.js", "scripts/auth.js"):
        candidates = [
            web_root / "src" / "scripts" / "auth.js",
            web_root / "scripts" / "auth.js",
        ]
        for c in candidates:
            if c.exists():
                return c

    # Common style mappings
    if clean_path in ("dashboard.css", "styles/dashboard.css"):
        candidates = [
            web_root / "src" / "styles" / "dashboard.css",
            web_root / "styles" / "dashboard.css",
        ]
        for c in candidates:
            if c.exists():
                return c

    if clean_path in ("auth.css", "styles/auth.css"):
        candidates = [
            web_root / "src" / "styles" / "auth.css",
            web_root / "styles" / "auth.css",
        ]
        for c in candidates:
            if c.exists():
                return c

    # Asset mappings
    if clean_path in ("favicon.svg", "assets/favicon.svg"):
        candidates = [
            web_root / "public" / "favicon.svg",
            web_root / "src" / "assets" / "favicon.svg",
            web_root / "favicon.svg",
        ]
        for c in candidates:
            if c.exists():
                return c

    # Generic lookup inside web_root, web_root/src, web_root/public
    for base in [web_root, web_root / "src", web_root / "public", web_root / "src" / "pages"]:
        target = (base / clean_path).resolve()
        if target.is_file() and str(target).startswith(str(web_root.resolve())):
            return target

    return None


def create_request_handler(controller: SensorController, settings: Settings):
    """Create a configured SimpleHTTPRequestHandler subclass."""

    class ApplicationRequestHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(settings.web_root), **kwargs)

        def do_OPTIONS(self) -> None:
            if not dispatch_api_route(self, controller, "OPTIONS", self.path):
                super().do_OPTIONS()

        def do_GET(self) -> None:
            if dispatch_api_route(self, controller, "GET", self.path):
                return

            # Static file handling
            file_path = resolve_frontend_file(settings.web_root, self.path)
            if file_path and file_path.is_file():
                self.directory = str(file_path.parent)
                self.path = f"/{file_path.name}"
                super().do_GET()
            else:
                send_json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": f"File not found: {self.path}"})

        def do_POST(self) -> None:
            if not dispatch_api_route(self, controller, "POST", self.path):
                send_json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": f"Route not found: {self.path}"})

        def do_DELETE(self) -> None:
            if not dispatch_api_route(self, controller, "DELETE", self.path):
                send_json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": f"Route not found: {self.path}"})

        def log_message(self, format_string: str, *args: Any) -> None:
            print(f"{self.address_string()} - {format_string % args}")

    return ApplicationRequestHandler


def create_application(
    settings: Settings | None = None,
    sensor: Any | None = None,
    store: Any | None = None,
    model: Any | None = None,
) -> tuple[SensorController, Settings]:
    """Initialize application context, services, and controller."""
    config = settings or Settings.from_environment()
    sensor_client = sensor or SensorClient(config.sensor_url, config.timeout_seconds)
    ml_model = model if model is not None else load_ml_model(config.model_file)

    def analysis_callback(values: dict[str, float]) -> dict[str, Any]:
        return analyze_bands(values, model=ml_model)

    data_store = store or ExcelStore(config.excel_file, analysis_fn=analysis_callback)
    controller = SensorController(
        settings=config,
        sensor=sensor_client,
        store=data_store,
        model=ml_model,
    )
    return controller, config


def create_server(controller: SensorController, settings: Settings) -> ThreadingHTTPServer:
    """Create and configure the ThreadingHTTPServer instance."""
    handler_class = create_request_handler(controller, settings)
    return ThreadingHTTPServer((settings.host, settings.port), handler_class)
