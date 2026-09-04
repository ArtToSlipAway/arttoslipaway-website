import os
from pathlib import Path


PROJECT_ROOT = Path(
    os.getenv(
        "ARTTOSLIPAWAY_ROOT",
        Path(__file__).resolve().parent.parent,
    )
).resolve()

APP_DIR = PROJECT_ROOT / "app"
STATIC_DIR = APP_DIR / "static"
TEMPLATES_DIR = APP_DIR / "templates"
UPLOADS_DIR = APP_DIR / "uploads"
MEDIA_ROOT = UPLOADS_DIR / "media"
PRIVATE_UPLOADS_DIR = PROJECT_ROOT / "private_files"
BACKUPS_DIR = PROJECT_ROOT / "backups"
ENV_PATH = PROJECT_ROOT / ".env"
