from pathlib import Path
import os
import sys

from dotenv import load_dotenv


def get_application_root() -> Path:
    """
    Return the folder from which the application should load
    its external configuration.

    During normal development:
        project root

    When running as a PyInstaller executable:
        folder containing the executable
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = get_application_root()

load_dotenv(PROJECT_ROOT / ".env")


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)

    if value is None or value.strip() == "":
        raise ValueError(f"Missing required environment variable: {name}")

    return value


def get_database_config() -> dict:
    return {
        "host": get_env("DB_HOST", "localhost"),
        "user": get_env("DB_USER"),
        "password": get_env("DB_PASSWORD"),
        "database": get_env("DB_NAME"),
    }