"""Database migration package."""
from .schema_migration import apply_schema_migration

__all__ = ["apply_schema_migration"]
