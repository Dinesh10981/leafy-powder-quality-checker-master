#!/usr/bin/env python3
"""Backend server entry point for Leafy Powder Quality Checker."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path so modules can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.src.app import create_application, create_server
from backend.src.config.settings import Settings


def build_parser() -> argparse.ArgumentParser:
    defaults = Settings.from_environment()
    parser = argparse.ArgumentParser(description="Leafy Powder Quality Checker Gateway & Analysis Server")
    parser.add_argument("--sensor-url", default=defaults.sensor_url, help="ESP scan URL")
    parser.add_argument("--excel-file", type=Path, default=defaults.excel_file, help="Workbook path")
    parser.add_argument("--model-file", type=Path, default=defaults.model_file, help="Path to trained moringa_model.pkl")
    parser.add_argument("--host", default=defaults.host, help="Bind host")
    parser.add_argument("--port", type=int, default=defaults.port, help="Listen port")
    parser.add_argument("--timeout", type=float, default=defaults.timeout_seconds, help="Sensor timeout in seconds")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings(
        sensor_url=args.sensor_url,
        excel_file=args.excel_file.resolve(),
        model_file=args.model_file.resolve(),
        host=args.host,
        port=args.port,
        timeout_seconds=args.timeout,
    )

    controller, configured_settings = create_application(settings=settings)
    server = create_server(controller, configured_settings)

    print("=" * 64)
    print("🌿 LEAFY POWDER QUALITY CHECKER — ANALYSIS BACKEND")
    print(f"Server URL: http://{configured_settings.host}:{configured_settings.port}")
    print(f"Dashboard : http://{configured_settings.host}:{configured_settings.port}/dashboard.html")
    print(f"Sensor    : {configured_settings.sensor_url}")
    print(f"Database  : {configured_settings.excel_file}")
    model_status = "loaded" if controller.model is not None else "not found (using formula fallback)"
    print(f"ML Model  : {configured_settings.model_file.name} ({model_status})")
    print("Press Ctrl+C to stop.")
    print("=" * 64)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
