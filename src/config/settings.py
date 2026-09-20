

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root = SmartInvoicePro-Fresh/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load .env from project root regardless of where a script is run from
load_dotenv(PROJECT_ROOT / ".env")


def get_env(name: str, default: str | None = None) -> str:
    """Read a required environment variable."""
    value = os.getenv(name, default)
    if value is None or value.strip() == "":
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def get_database_config() -> dict:
    """Return database connection settings from .env."""
    return {
        "host": get_env("DB_HOST", "localhost"),
        "user": get_env("DB_USER"),
        "password": get_env("DB_PASSWORD"),
        "database": get_env("DB_NAME"),
    }
