"""Tests for the ResendClient."""

import base64
import pytest
from unittest.mock import patch, MagicMock

from resend_cli.client import ResendClient, ResendError


class TestResendClient:
    def test_send_email(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(200, {"id": "email_123"})
        result = client.send_email({"to": ["a@b.com"], "subject": "Hi", "text": "Hello"})
        assert result["id"] == "email_123"
        mock_session.request.assert_called_once()
        args = mock_session.request.call_args
        assert args[0] == ("POST", "https://api.resend.com/emails")

    def test_get_email(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(200, {"id": "e1", "last_event": "delivered"})
        result = client.get_email("e1")
        assert result["last_event"] == "delivered"

    def test_list_inbound(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(200, {"data": [{"id": "in1"}]})
        result = client.list_inbound()
        assert len(result) == 1
        assert result[0]["id"] == "in1"

    def test_list_inbound_plain_list(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(200, [{"id": "in1"}])
        result = client.list_inbound()
        assert result == [{"id": "in1"}]

    def test_get_inbound(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(200, {"id": "in1", "subject": "Test"})
        result = client.get_inbound("in1")
        assert result["subject"] == "Test"
        args = mock_session.request.call_args
        assert "/emails/receiving/in1" in args[0][1]

    def test_list_domains(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(200, {"data": [{"id": "d1", "name": "auri.email"}]})
        result = client.list_domains()
        assert result[0]["name"] == "auri.email"

    def test_verify_domain(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(200, {"id": "d1"})
        result = client.verify_domain("d1")
        assert result["id"] == "d1"

    def test_list_audiences(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(200, {"data": [{"id": "aud1", "name": "News"}]})
        result = client.list_audiences()
        assert result[0]["name"] == "News"

    def test_create_audience(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(200, {"id": "aud2"})
        result = client.create_audience("Test")
        assert result["id"] == "aud2"

    def test_delete_audience(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(200, {"deleted": True})
        result = client.delete_audience("aud1")
        assert result["deleted"] is True

    def test_list_contacts(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(200, {"data": [{"id": "c1", "email": "x@y.com"}]})
        result = client.list_contacts("aud1")
        assert result[0]["email"] == "x@y.com"

    def test_create_contact(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(200, {"id": "c2"})
        result = client.create_contact("aud1", "a@b.com", first_name="A")
        assert result["id"] == "c2"

    def test_delete_contact(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(200, {"deleted": True})
        result = client.delete_contact("aud1", "c1")
        assert result["deleted"] is True

    def test_api_error(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(400, {"message": "Bad request"})
        with pytest.raises(ResendError) as exc:
            client.send_email({})
        assert exc.value.status_code == 400

    def test_api_error_no_json(self, client, mock_session):
        resp = MagicMock()
        resp.status_code = 500
        resp.json.side_effect = Exception("no json")
        resp.text = "Internal Server Error"
        resp.headers = {}
        mock_session.request.return_value = resp
        with pytest.raises(ResendError, match="Internal Server Error"):
            client.get_email("x")

    def test_204_returns_none(self, client, mock_session, mock_response):
        mock_session.request.return_value = mock_response(204)
        result = client._request("DELETE", "/something")
        assert result is None

    def test_rate_limit_retry(self, client, mock_session, mock_response):
        rate_resp = mock_response(429, headers={"Retry-After": "0"})
        ok_resp = mock_response(200, {"id": "ok"})
        mock_session.request.side_effect = [rate_resp, ok_resp]
        result = client.send_email({"to": ["a@b.com"]})
        assert result["id"] == "ok"
        assert mock_session.request.call_count == 2

    def test_encode_attachment(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"hello world")
        att = ResendClient.encode_attachment(str(f))
        assert att["filename"] == "test.txt"
        assert base64.b64decode(att["content"]) == b"hello world"
