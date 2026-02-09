"""Tests for CLI commands."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from resend_cli.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_client():
    with patch("resend_cli.cli.get_client") as mock_gc:
        client = MagicMock()
        mock_gc.return_value = client
        yield client


class TestSendCommand:
    def test_send_text(self, runner, mock_client):
        mock_client.send_email.return_value = {"id": "e1"}
        result = runner.invoke(cli, ["send", "--to", "a@b.com", "--subject", "Hi", "--text", "Hello"])
        assert result.exit_code == 0
        assert "e1" in result.output

    def test_send_html(self, runner, mock_client):
        mock_client.send_email.return_value = {"id": "e2"}
        result = runner.invoke(cli, ["send", "--to", "a@b.com", "--subject", "Hi", "--html", "<b>Hi</b>"])
        assert result.exit_code == 0

    def test_send_dry_run(self, runner, mock_client):
        result = runner.invoke(cli, ["send", "--to", "a@b.com", "--subject", "Hi", "--text", "Body", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        mock_client.send_email.assert_not_called()

    def test_send_no_body(self, runner, mock_client):
        result = runner.invoke(cli, ["send", "--to", "a@b.com", "--subject", "Hi"])
        assert result.exit_code != 0

    def test_send_with_sign(self, runner, mock_client):
        mock_client.send_email.return_value = {"id": "e3"}
        result = runner.invoke(cli, ["send", "--to", "a@b.com", "--subject", "Hi", "--text", "Body", "--sign"])
        assert result.exit_code == 0
        payload = mock_client.send_email.call_args[0][0]
        assert "Auri Wren" in payload["text"]

    def test_send_with_tags(self, runner, mock_client):
        mock_client.send_email.return_value = {"id": "e4"}
        result = runner.invoke(cli, ["send", "--to", "a@b.com", "--subject", "Hi", "--text", "Body", "--tag", "cat=onboard"])
        assert result.exit_code == 0
        payload = mock_client.send_email.call_args[0][0]
        assert payload["tags"] == [{"name": "cat", "value": "onboard"}]

    def test_send_with_cc_bcc(self, runner, mock_client):
        mock_client.send_email.return_value = {"id": "e5"}
        result = runner.invoke(cli, ["send", "--to", "a@b.com", "--cc", "c@d.com", "--bcc", "e@f.com", "--subject", "Hi", "--text", "Body"])
        assert result.exit_code == 0
        payload = mock_client.send_email.call_args[0][0]
        assert payload["cc"] == ["c@d.com"]
        assert payload["bcc"] == ["e@f.com"]

    def test_send_html_file(self, runner, mock_client, tmp_path):
        f = tmp_path / "email.html"
        f.write_text("<h1>Hello</h1>")
        mock_client.send_email.return_value = {"id": "e6"}
        result = runner.invoke(cli, ["send", "--to", "a@b.com", "--subject", "Hi", "--html-file", str(f)])
        assert result.exit_code == 0
        payload = mock_client.send_email.call_args[0][0]
        assert "<h1>Hello</h1>" in payload["html"]

    def test_send_text_file(self, runner, mock_client, tmp_path):
        f = tmp_path / "email.txt"
        f.write_text("Plain text body")
        mock_client.send_email.return_value = {"id": "e7"}
        result = runner.invoke(cli, ["send", "--to", "a@b.com", "--subject", "Hi", "--text-file", str(f)])
        assert result.exit_code == 0
        payload = mock_client.send_email.call_args[0][0]
        assert "Plain text body" in payload["text"]

    def test_send_custom_from(self, runner, mock_client):
        mock_client.send_email.return_value = {"id": "e8"}
        result = runner.invoke(cli, ["send", "--to", "a@b.com", "--subject", "Hi", "--text", "Body", "--from", "Other <other@x.com>"])
        assert result.exit_code == 0
        payload = mock_client.send_email.call_args[0][0]
        assert payload["from"] == "Other <other@x.com>"

    def test_send_error(self, runner, mock_client):
        from resend_cli.client import ResendError
        mock_client.send_email.side_effect = ResendError(422, "Invalid")
        result = runner.invoke(cli, ["send", "--to", "a@b.com", "--subject", "Hi", "--text", "Body"])
        assert result.exit_code != 0


class TestInboxCommand:
    def test_inbox_list(self, runner, mock_client):
        mock_client.list_inbound.return_value = [{"id": "in1", "from": "x@y.com", "subject": "Test", "created_at": "2026-01-01"}]
        result = runner.invoke(cli, ["inbox"])
        assert result.exit_code == 0
        assert "in1" in result.output

    def test_inbox_list_empty(self, runner, mock_client):
        mock_client.list_inbound.return_value = []
        result = runner.invoke(cli, ["inbox"])
        assert result.exit_code == 0
        assert "No inbound" in result.output

    def test_inbox_limit(self, runner, mock_client):
        mock_client.list_inbound.return_value = [{"id": f"in{i}", "from": "", "subject": "", "created_at": ""} for i in range(10)]
        result = runner.invoke(cli, ["inbox", "--limit", "3"])
        assert result.exit_code == 0

    def test_inbox_read(self, runner, mock_client):
        mock_client.get_inbound.return_value = {"id": "in1", "from": "x@y.com", "to": ["a@b.com"], "subject": "Hi", "created_at": "2026-01-01", "text": "Hello", "html": ""}
        result = runner.invoke(cli, ["inbox", "read", "in1"])
        assert result.exit_code == 0
        assert "in1" in result.output


class TestStatusCommand:
    def test_status(self, runner, mock_client):
        mock_client.get_email.return_value = {"id": "e1", "from": "a@b.com", "to": ["c@d.com"], "subject": "Hi", "created_at": "2026-01-01", "last_event": "delivered"}
        result = runner.invoke(cli, ["status", "e1"])
        assert result.exit_code == 0
        assert "delivered" in result.output


class TestDomainsCommand:
    def test_domains_list(self, runner, mock_client):
        mock_client.list_domains.return_value = [{"id": "d1", "name": "auri.email", "status": "verified"}]
        result = runner.invoke(cli, ["domains", "list"])
        assert result.exit_code == 0
        assert "auri.email" in result.output

    def test_domains_verify(self, runner, mock_client):
        mock_client.verify_domain.return_value = {"id": "d1"}
        result = runner.invoke(cli, ["domains", "verify", "d1"])
        assert result.exit_code == 0


class TestAudiencesCommand:
    def test_audiences_list(self, runner, mock_client):
        mock_client.list_audiences.return_value = [{"id": "aud1", "name": "News"}]
        result = runner.invoke(cli, ["audiences", "list"])
        assert result.exit_code == 0
        assert "News" in result.output

    def test_audiences_create(self, runner, mock_client):
        mock_client.create_audience.return_value = {"id": "aud2"}
        result = runner.invoke(cli, ["audiences", "create", "--name", "Test"])
        assert result.exit_code == 0
        assert "aud2" in result.output

    def test_audiences_remove(self, runner, mock_client):
        mock_client.delete_audience.return_value = {"deleted": True}
        result = runner.invoke(cli, ["audiences", "remove", "aud1"])
        assert result.exit_code == 0


class TestContactsCommand:
    def test_contacts_list(self, runner, mock_client):
        mock_client.list_contacts.return_value = [{"id": "c1", "email": "x@y.com", "first_name": "X", "last_name": "Y"}]
        result = runner.invoke(cli, ["contacts", "list", "--audience", "aud1"])
        assert result.exit_code == 0
        assert "x@y.com" in result.output

    def test_contacts_add(self, runner, mock_client):
        mock_client.create_contact.return_value = {"id": "c2"}
        result = runner.invoke(cli, ["contacts", "add", "--audience", "aud1", "--email", "a@b.com", "--first-name", "A"])
        assert result.exit_code == 0
        assert "c2" in result.output

    def test_contacts_remove(self, runner, mock_client):
        mock_client.delete_contact.return_value = {"deleted": True}
        result = runner.invoke(cli, ["contacts", "remove", "--audience", "aud1", "--email", "c1"])
        assert result.exit_code == 0
