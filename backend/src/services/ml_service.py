"""Machine learning service for moringa powder quality classification."""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Mapping

from database.models.sensor_record import BANDS

_MODEL_CACHE: Any | None = None
_MODEL_LOAD_PATH: Path | None = None
_MODEL_LOCK = threading.Lock()

QUALITY_MAP = {
    "High": "Good",
    "Medium": "Moderate",
    "Low": "Poor",
}


def load_ml_model(model_path: Path | str | None = None) -> Any | None:
    """Load and cache the trained ML model (RandomForestClassifier)."""
    global _MODEL_CACHE, _MODEL_LOAD_PATH
    with _MODEL_LOCK:
        if model_path is None:
            # Check default backend model directory or workspace root
            target_path = Path(__file__).resolve().parents[2] / "models" / "moringa_model.pkl"
            if not target_path.exists():
                target_path = Path(__file__).resolve().parents[3] / "moringa_model.pkl"
        else:
            target_path = Path(model_path).resolve()

        if _MODEL_CACHE is not None and _MODEL_LOAD_PATH == target_path:
            return _MODEL_CACHE
        if not target_path.exists():
            return None

        try:
            import joblib
            _MODEL_CACHE = joblib.load(target_path)
            _MODEL_LOAD_PATH = target_path
            return _MODEL_CACHE
        except Exception as exc:
            import warnings
            warnings.warn(f"Failed to load ML model from {target_path}: {exc}", stacklevel=2)
            return None


def scale_features_for_inference(raw_values: list[float]) -> list[float]:
    """
    Scale spectral readings into [0.0, 1.0] expected by the model.
    - If already normalized (<= 1.0), use directly.
    - If percentage values (<= 100.0), scale by / 100.
    - If raw uncalibrated ADC counts (> 100.0), normalize by max band.
    """
    max_val = max(raw_values) if raw_values else 0.0
    if max_val <= 1.0:
        return raw_values
    if max_val <= 100.0:
        return [min(1.0, max(0.0, x / 100.0)) for x in raw_values]
    return [min(1.0, max(0.0, x / max_val)) for x in raw_values]


def predict_quality_ml(
    values: Mapping[str, float],
    model: Any | None = None,
) -> tuple[str, str, float]:
    """
    Predict quality using the trained ML model.
    Returns: (quality_label, ml_prediction, confidence_score)
    """
    target_model = model if model is not None else load_ml_model()
    if target_model is None:
        return "", "", 0.0

    raw = [float(values[b]) for b in BANDS]
    scaled = scale_features_for_inference(raw)

    try:
        import pandas as pd
        feature_names = getattr(target_model, "feature_names_in_", ["W1", "W2", "W3", "W4", "W5", "W6"])
        df = pd.DataFrame([scaled], columns=feature_names)
        pred = target_model.predict(df)[0]
        confidence = 1.0
        if hasattr(target_model, "predict_proba"):
            probas = target_model.predict_proba(df)[0]
            classes = list(getattr(target_model, "classes_", []))
            if pred in classes:
                confidence = float(probas[classes.index(pred)])
            else:
                confidence = float(max(probas))

        ml_prediction = str(pred)
        quality = QUALITY_MAP.get(ml_prediction, ml_prediction)
        return quality, ml_prediction, confidence
    except Exception as exc:
        import warnings
        warnings.warn(f"ML model prediction error: {exc}", stacklevel=2)
        return "", "", 0.0
