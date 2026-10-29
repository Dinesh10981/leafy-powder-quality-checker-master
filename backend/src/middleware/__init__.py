"""Backend middleware package."""
from .cors import handle_cors_preflight

__all__ = ["handle_cors_preflight"]
