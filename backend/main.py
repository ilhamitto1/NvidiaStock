"""Vercel entrypoint — app instance must be named `app`."""
from app.main import app  # noqa: F401

__all__ = ["app"]
