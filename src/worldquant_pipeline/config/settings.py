"""Settings and configuration loaders for worldquant_pipeline."""
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CONFIGS_DIR = PROJECT_ROOT / "configs"


def load_yaml_config(file_path: Path) -> dict[str, Any]:
    """Safely load and parse a YAML configuration file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


class Settings:
    """Application settings loaded from environment and config directory."""

    def __init__(self) -> None:
        self.project_root: Path = PROJECT_ROOT
        self.configs_dir: Path = CONFIGS_DIR
        self.research_config_path: Path = CONFIGS_DIR / "research.yaml"
        self.data_sources_path: Path = CONFIGS_DIR / "data_sources.yaml"

        # Database URL
        raw_db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/worldquant_brain",
        )
        # Strip ?schema= parameter if present, as psycopg/libpq does not recognize it
        if "?schema=" in raw_db_url:
            raw_db_url = raw_db_url.split("?schema=")[0]
        # Prefer psycopg2 driver if raw postgresql:// is provided
        if raw_db_url.startswith("postgresql://"):
            raw_db_url = raw_db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

        self.database_url: str = raw_db_url
        self.research_domain: str = os.getenv("RESEARCH_DOMAIN", "price_volume")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

    @property
    def research_config(self) -> dict[str, Any]:
        """Cached access to research.yaml."""
        return load_yaml_config(self.research_config_path)

    @property
    def data_sources_config(self) -> dict[str, Any]:
        """Cached access to data_sources.yaml."""
        return load_yaml_config(self.data_sources_path)

    def get_allowed_operators(self) -> dict[str, dict[str, Any]]:
        """Flatten and return all allowed operators with their arity and types."""
        cfg = self.research_config.get("operators", {})
        result = {}
        for category in ["time_series", "cross_sectional", "elementwise"]:
            for op in cfg.get(category, []):
                result[op["name"]] = op
        return result

    def get_allowed_fields(self) -> dict[str, dict[str, Any]]:
        """Return all approved fields from data_sources.yaml with event and unit metadata."""
        cfg = self.data_sources_config.get("fields", [])
        known_event_fields = {
            "anl4_buy",
            "anl4_sell",
            "anl4_hold",
            "anl4_strong_buy",
            "anl4_strong_sell",
            "anl4_underperform",
            "anl4_outperform",
        }
        res: dict[str, dict[str, Any]] = {}
        for f in cfg:
            if f.get("permitted_use", True):
                fk = f["field_key"]
                field_dict = dict(f)
                if "is_event" not in field_dict:
                    field_dict["is_event"] = (
                        fk in known_event_fields
                        or f.get("category") == "events"
                        or fk.startswith("event_")
                    )
                if "unit_type" not in field_dict:
                    field_dict["unit_type"] = f.get("unit") or "dimensionless"
                res[fk] = field_dict
        return res


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a singleton instance of application settings."""
    return Settings()
