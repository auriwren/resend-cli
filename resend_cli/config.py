"""Credential loading and default configuration."""

import os
from pathlib import Path

API_BASE = "https://api.resend.com"
CREDENTIALS_PATH = Path.home() / ".openclaw" / "credentials" / "resend.env"
DEFAULT_TIMEOUT = 30

# Defaults are loaded from env vars or credentials file.
# Set these in your environment or credentials file:
#   RESEND_FROM="Your Name <you@yourdomain.com>"
#   RESEND_REPLY_TO="you@yourdomain.com"
#   RESEND_SIGNATURE="-- Your Name, Your Title"
_FALLBACK_FROM = "sender@example.com"
_FALLBACK_REPLY_TO = ""
_FALLBACK_SIGNATURE = ""


def _load_credentials() -> dict[str, str]:
    """Load key=value pairs from the credentials file."""
    creds: dict[str, str] = {}
    if CREDENTIALS_PATH.exists():
        for line in CREDENTIALS_PATH.read_text().splitlines():
            line = line.strip()
            if line.startswith("#") or not line or "=" not in line:
                continue
            k, v = line.split("=", 1)
            creds[k.strip()] = v.strip().strip('"').strip("'")
    return creds


def load_api_key() -> str:
    """Load RESEND_API_KEY from env, falling back to credentials file."""
    key = os.environ.get("RESEND_API_KEY")
    if key:
        return key.strip()

    creds = _load_credentials()
    if "RESEND_API_KEY" in creds:
        return creds["RESEND_API_KEY"]

    raise RuntimeError(
        "RESEND_API_KEY not found. Set it in the environment or in "
        f"{CREDENTIALS_PATH}"
    )


def get_default_from() -> str:
    """Get default sender from env/credentials or fallback."""
    return os.environ.get("RESEND_FROM") or _load_credentials().get("RESEND_FROM", _FALLBACK_FROM)


def get_default_reply_to() -> str:
    """Get default reply-to from env/credentials or fallback."""
    return os.environ.get("RESEND_REPLY_TO") or _load_credentials().get("RESEND_REPLY_TO", _FALLBACK_REPLY_TO)


def get_default_signature() -> str:
    """Get default signature from env/credentials or fallback."""
    return os.environ.get("RESEND_SIGNATURE") or _load_credentials().get("RESEND_SIGNATURE", _FALLBACK_SIGNATURE)
