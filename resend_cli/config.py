"""Credential loading and default configuration."""

import os
from pathlib import Path

DEFAULT_FROM = "Auri Wren <auri@auri.email>"
DEFAULT_REPLY_TO = "auri@auri.email"
DEFAULT_SIGNATURE = "-- Auri Wren, Personal Assistant to Eiwe Lingefors"
API_BASE = "https://api.resend.com"
CREDENTIALS_PATH = Path.home() / ".openclaw" / "credentials" / "resend.env"
DEFAULT_TIMEOUT = 30


def load_api_key() -> str:
    """Load RESEND_API_KEY from env, falling back to credentials file."""
    key = os.environ.get("RESEND_API_KEY")
    if key:
        return key.strip()

    if CREDENTIALS_PATH.exists():
        for line in CREDENTIALS_PATH.read_text().splitlines():
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                if k.strip() == "RESEND_API_KEY":
                    return v.strip().strip('"').strip("'")

    raise RuntimeError(
        "RESEND_API_KEY not found. Set it in the environment or in "
        f"{CREDENTIALS_PATH}"
    )
