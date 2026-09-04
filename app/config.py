"""Deployment settings shared by route modules."""
import os


def site_base_url() -> str:
    return os.getenv("SITE_BASE_URL", "http://localhost:8000").rstrip("/")
