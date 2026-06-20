"""ASPIS settings — typed, central configuration.

Loaded once and shared across the engine (single source). Defaults come from
:mod:`aspis.constants` and may be overridden by ``ASPIS_*`` environment
variables. Pydantic validates every value, so a bad override fails fast with a
clear error instead of surfacing as a confusing bug later.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from aspis import constants


class Settings(BaseSettings):
    """Process-wide ASPIS configuration."""

    model_config = SettingsConfigDict(env_prefix="ASPIS_", extra="ignore")

    #: Folder that marks a directory as an ASPIS project.
    brain_dir: str = constants.BRAIN_DIR

    #: Hook subfolder under the brain (event folders live beneath it).
    hooks_dir: str = constants.HOOKS_DIR


@lru_cache
def get_settings() -> Settings:
    """Return the cached, process-wide settings instance."""
    return Settings()
