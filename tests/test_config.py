"""Tests for config module."""

import os
import pytest
from unittest.mock import patch

from resend_cli.config import (
    load_api_key,
    get_default_from,
    get_default_reply_to,
    get_default_signature,
)


def test_load_from_env():
    with patch.dict(os.environ, {"RESEND_API_KEY": "re_test123"}):
        assert load_api_key() == "re_test123"


def test_load_from_env_strips():
    with patch.dict(os.environ, {"RESEND_API_KEY": "  re_test123  "}):
        assert load_api_key() == "re_test123"


def test_load_from_file():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("RESEND_API_KEY", None)
        file_content = 'RESEND_API_KEY=re_fromfile\n'
        with patch("resend_cli.config.CREDENTIALS_PATH") as mock_path:
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = file_content
            assert load_api_key() == "re_fromfile"


def test_load_from_file_quoted():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("RESEND_API_KEY", None)
        file_content = 'RESEND_API_KEY="re_quoted"\n'
        with patch("resend_cli.config.CREDENTIALS_PATH") as mock_path:
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = file_content
            assert load_api_key() == "re_quoted"


def test_load_missing_raises():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("RESEND_API_KEY", None)
        with patch("resend_cli.config.CREDENTIALS_PATH") as mock_path:
            mock_path.exists.return_value = False
            with pytest.raises(RuntimeError, match="RESEND_API_KEY not found"):
                load_api_key()


def test_load_file_with_comments():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("RESEND_API_KEY", None)
        file_content = '# comment\n\nRESEND_API_KEY=re_val\n'
        with patch("resend_cli.config.CREDENTIALS_PATH") as mock_path:
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = file_content
            assert load_api_key() == "re_val"


def test_get_default_from_env():
    with patch.dict(os.environ, {"RESEND_FROM": "Test <test@example.com>"}):
        assert get_default_from() == "Test <test@example.com>"


def test_get_default_from_file():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("RESEND_FROM", None)
        with patch("resend_cli.config.CREDENTIALS_PATH") as mock_path:
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = 'RESEND_FROM="Agent <agent@domain.com>"\n'
            assert get_default_from() == "Agent <agent@domain.com>"


def test_get_default_from_fallback():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("RESEND_FROM", None)
        with patch("resend_cli.config.CREDENTIALS_PATH") as mock_path:
            mock_path.exists.return_value = False
            assert get_default_from() == "sender@example.com"


def test_get_default_reply_to_env():
    with patch.dict(os.environ, {"RESEND_REPLY_TO": "reply@example.com"}):
        assert get_default_reply_to() == "reply@example.com"


def test_get_default_signature_env():
    with patch.dict(os.environ, {"RESEND_SIGNATURE": "-- Test Agent"}):
        assert get_default_signature() == "-- Test Agent"
