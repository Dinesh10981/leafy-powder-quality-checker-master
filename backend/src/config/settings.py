"""Backend configuration and environment settings."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_dotenv(dotenv_path: Path | None = None) -> None:
    """Simple zero-dependency .env file loader."""
    if dotenv_path is None:
        dotenv_path = Path(__file__).resolve().parents[3] / ".env"
    if not dotenv_path.exists():
        return
    try:
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        pass


# Automatically load .env if present
load_dotenv()


@dataclass(frozen=True)
class Settings:
    sensor_url: str
    excel_file: Path
    model_file: Path
    host: str = "127.0.0.1"
    port: int = 5050
    timeout_seconds: float = 10.0
    project_root: Path = Path(__file__).resolve().parents[3]
    web_root: Path = Path(__file__).resolve().parents[3] / "frontend"

    @classmethod
    def from_environment(cls) -> "Settings":
        root = Path(__file__).resolve().parents[3]
        sensor_url = os.getenv("MORINGA_SENSOR_URL", "http://10.149.144.149/scan")
        if not sensor_url.rstrip("/").endswith("/scan"):
            sensor_url = sensor_url.rstrip("/") + "/scan"

        # Check default paths with fallback to legacy outputs if needed
        default_excel = root / "database" / "outputs" / "sensor_data.xlsx"
        legacy_excel = root / "outputs" / "moringa_sensor_integration" / "sensor_data.xlsx"
        excel_path = Path(os.getenv("MORINGA_EXCEL_FILE", str(default_excel if default_excel.exists() else legacy_excel))).expanduser()

        default_model = root / "backend" / "models" / "moringa_model.pkl"
        legacy_model = root / "moringa_model.pkl"
        model_path = Path(os.getenv("MORINGA_MODEL_FILE", str(default_model if default_model.exists() else legacy_model))).expanduser()

        return cls(
            sensor_url=sensor_url,
            excel_file=excel_path,
            model_file=model_path,
            host=os.getenv("MORINGA_HOST", "127.0.0.1"),
            port=int(os.getenv("MORINGA_PORT", "5050")),
            timeout_seconds=float(os.getenv("MORINGA_SENSOR_TIMEOUT", "10")),
            project_root=root,
            web_root=root / "frontend",
        )
