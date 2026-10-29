"""Spectral index calculation and quality analysis service."""
from __future__ import annotations

from typing import Any, Mapping

from .ml_service import predict_quality_ml


class AnalysisCalculationError(ValueError):
    """Raised when calculation parameters violate mathematical invariants."""


def analyze_bands(values: Mapping[str, float], model: Any | None = None) -> dict[str, Any]:
    """
    Calculate red-edge average, NIR average, LPQI index, and ML-predicted quality.
    """
    red_edge_average = (float(values["S"]) + float(values["T"])) / 2.0
    nir_average = (float(values["U"]) + float(values["V"]) + float(values["W"])) / 3.0
    denominator = nir_average + red_edge_average
    if denominator <= 0:
        raise AnalysisCalculationError("LPQI cannot be calculated because red-edge and NIR values sum to zero")

    lpqi = (nir_average - red_edge_average) / denominator

    # Use ML model to determine quality
    quality, ml_prediction, confidence = predict_quality_ml(values, model=model)
    if not quality:
        # Fallback to formula threshold if ML model is unavailable
        quality = "Good" if lpqi >= 0.45 else "Moderate" if lpqi >= 0.25 else "Poor"
        ml_prediction = "High" if quality == "Good" else ("Medium" if quality == "Moderate" else "Low")
        confidence = 1.0

    return {
        "red_edge_average": red_edge_average,
        "nir_average": nir_average,
        "lpqi": lpqi,
        "quality": quality,
        "ml_prediction": ml_prediction,
        "confidence": round(confidence, 3),
    }
