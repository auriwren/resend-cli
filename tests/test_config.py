"""Tests for config module."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from resend_cli.config import load_api_key, DEFAULT_FROM, DEFAULT_REPLY_TO, DEFAULT_SIGNATURE


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


def test_defaults():
    assert "auri@auri.email" in DEFAULT_FROM
    assert DEFAULT_REPLY_TO == "auri@auri.email"
    assert "Auri Wren" in DEFAULT_SIGNATURE
