"""Vercel serverless entrypoint — keeps imports relative to the backend root."""
from app.main import app

__all__ = ["app"]
