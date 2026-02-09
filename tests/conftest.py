"""Shared fixtures for tests."""

import pytest
from unittest.mock import MagicMock, patch

from resend_cli.client import ResendClient


@pytest.fixture
def mock_session():
    with patch("resend_cli.client.requests.Session") as MockSession:
        session = MagicMock()
        MockSession.return_value = session
        yield session


@pytest.fixture
def client(mock_session):
    return ResendClient("test_api_key")


@pytest.fixture
def mock_response():
    """Factory for mock responses."""
    def _make(status_code=200, json_data=None, text="", headers=None):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = json_data or {}
        resp.text = text
        resp.headers = headers or {}
        return resp
    return _make
