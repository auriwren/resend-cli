"""Resend API client wrapping all endpoints."""

import base64
import time
from pathlib import Path
from typing import Any

import requests

from .config import API_BASE, DEFAULT_TIMEOUT


class ResendError(Exception):
    """Raised on API errors."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Resend API error {status_code}: {message}")


class ResendClient:
    """Wraps the Resend REST API."""

    def __init__(self, api_key: str, base_url: str = API_BASE, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        kwargs.setdefault("timeout", self.timeout)
        url = f"{self.base_url}{path}"
        resp = self.session.request(method, url, **kwargs)

        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "1"))
            time.sleep(retry_after)
            resp = self.session.request(method, url, **kwargs)

        if resp.status_code >= 400:
            try:
                detail = resp.json().get("message", resp.text)
            except Exception:
                detail = resp.text
            raise ResendError(resp.status_code, detail)

        if resp.status_code == 204:
            return None
        return resp.json()

    # --- Email sending ---

    def send_email(self, payload: dict) -> dict:
        return self._request("POST", "/emails", json=payload)

    # --- Sent email status ---

    def get_email(self, email_id: str) -> dict:
        return self._request("GET", f"/emails/{email_id}")

    # --- Inbound (receiving) ---

    def list_inbound(self) -> list:
        data = self._request("GET", "/emails/receiving")
        if isinstance(data, dict):
            return data.get("data", [])
        return data

    def get_inbound(self, email_id: str) -> dict:
        return self._request("GET", f"/emails/receiving/{email_id}")

    # --- Domains ---

    def list_domains(self) -> list:
        data = self._request("GET", "/domains")
        if isinstance(data, dict):
            return data.get("data", [])
        return data

    def verify_domain(self, domain_id: str) -> dict:
        return self._request("POST", f"/domains/{domain_id}/verify")

    # --- Audiences ---

    def list_audiences(self) -> list:
        data = self._request("GET", "/audiences")
        if isinstance(data, dict):
            return data.get("data", [])
        return data

    def create_audience(self, name: str) -> dict:
        return self._request("POST", "/audiences", json={"name": name})

    def delete_audience(self, audience_id: str) -> dict:
        return self._request("DELETE", f"/audiences/{audience_id}")

    # --- Contacts ---

    def list_contacts(self, audience_id: str) -> list:
        data = self._request("GET", f"/audiences/{audience_id}/contacts")
        if isinstance(data, dict):
            return data.get("data", [])
        return data

    def create_contact(self, audience_id: str, email: str, **kwargs: Any) -> dict:
        payload: dict = {"email": email}
        if "first_name" in kwargs:
            payload["first_name"] = kwargs["first_name"]
        if "last_name" in kwargs:
            payload["last_name"] = kwargs["last_name"]
        if "unsubscribed" in kwargs:
            payload["unsubscribed"] = kwargs["unsubscribed"]
        return self._request("POST", f"/audiences/{audience_id}/contacts", json=payload)

    def delete_contact(self, audience_id: str, contact_id: str) -> dict:
        return self._request("DELETE", f"/audiences/{audience_id}/contacts/{contact_id}")

    # --- Helpers ---

    @staticmethod
    def encode_attachment(file_path: str) -> dict:
        p = Path(file_path)
        content = base64.b64encode(p.read_bytes()).decode()
        return {"filename": p.name, "content": content}
