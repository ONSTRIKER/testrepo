"""Shared utilities for Teacher UI."""

from .api_client import APIClient
from .config import UI_CONFIG, apply_custom_css

__all__ = ["APIClient", "UI_CONFIG", "apply_custom_css"]
