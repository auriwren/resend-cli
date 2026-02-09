"""Click CLI entry point."""

import sys
from pathlib import Path

import click

from .client import ResendClient, ResendError
from .config import DEFAULT_FROM, DEFAULT_REPLY_TO, DEFAULT_SIGNATURE, load_api_key
from .formatters import (
    print_audience_created,
    print_audience_deleted,
    print_audiences,
    print_contact_created,
    print_contact_deleted,
    print_contacts,
    print_domain_verified,
    print_domains,
    print_dry_run,
    print_email_sent,
    print_email_status,
    print_inbound_detail,
    print_inbound_list,
)


def get_client() -> ResendClient:
    api_key = load_api_key()
    return ResendClient(api_key)


@click.group()
def cli():
    """Resend CLI - manage emails via the Resend API."""
    pass


@cli.command()
@click.option("--to", "to_addrs", required=True, multiple=True, help="Recipient(s)")
@click.option("--subject", required=True, help="Subject line")
@click.option("--text", "text_body", default=None, help="Plain text body")
@click.option("--html", "html_body", default=None, help="HTML body")
@click.option("--html-file", default=None, type=click.Path(exists=True), help="Read HTML from file")
@click.option("--text-file", default=None, type=click.Path(exists=True), help="Read text from file")
@click.option("--from", "from_addr", default=None, help=f"Sender (default: {DEFAULT_FROM})")
@click.option("--reply-to", "reply_to", default=None, help="Reply-to address")
@click.option("--cc", multiple=True, help="CC recipient(s)")
@click.option("--bcc", multiple=True, help="BCC recipient(s)")
@click.option("--attach", multiple=True, type=click.Path(exists=True), help="Attachment(s)")
@click.option("--sign", is_flag=True, help="Append signature")
@click.option("--tag", multiple=True, help="Tags as key=value")
@click.option("--idempotency-key", default=None, help="Idempotency key")
@click.option("--dry-run", is_flag=True, help="Print payload without sending")
def send(to_addrs, subject, text_body, html_body, html_file, text_file,
         from_addr, reply_to, cc, bcc, attach, sign, tag, idempotency_key, dry_run):
    """Send an email."""
    if html_file:
        html_body = Path(html_file).read_text()
    if text_file:
        text_body = Path(text_file).read_text()

    if not text_body and not html_body:
        click.echo("Error: provide --text, --html, --text-file, or --html-file", err=True)
        sys.exit(1)

    if sign:
        if text_body:
            text_body = text_body + f"\n\n{DEFAULT_SIGNATURE}"
        if html_body:
            html_body = html_body + f"<br><br>{DEFAULT_SIGNATURE}"

    payload: dict = {
        "from": from_addr or DEFAULT_FROM,
        "to": list(to_addrs),
        "subject": subject,
        "reply_to": [reply_to or DEFAULT_REPLY_TO],
    }
    if text_body:
        payload["text"] = text_body
    if html_body:
        payload["html"] = html_body
    if cc:
        payload["cc"] = list(cc)
    if bcc:
        payload["bcc"] = list(bcc)
    if attach:
        payload["attachments"] = [ResendClient.encode_attachment(a) for a in attach]
    if tag:
        payload["tags"] = []
        for t in tag:
            if "=" in t:
                k, v = t.split("=", 1)
                payload["tags"].append({"name": k, "value": v})
    if idempotency_key:
        payload["headers"] = {"Idempotency-Key": idempotency_key}

    if dry_run:
        print_dry_run(payload)
        return

    try:
        client = get_client()
        result = client.send_email(payload)
        print_email_sent(result)
    except (ResendError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.group(invoke_without_command=True)
@click.option("--limit", default=None, type=int, help="Max results")
@click.pass_context
def inbox(ctx, limit):
    """List or read inbound emails."""
    if ctx.invoked_subcommand is None:
        try:
            client = get_client()
            items = client.list_inbound()
            if limit:
                items = items[:limit]
            print_inbound_list(items)
        except (ResendError, RuntimeError) as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)


@inbox.command("read")
@click.argument("email_id")
def inbox_read(email_id):
    """Read a specific inbound email."""
    try:
        client = get_client()
        data = client.get_inbound(email_id)
        print_inbound_detail(data)
    except (ResendError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("email_id")
def status(email_id):
    """Get sent email delivery status."""
    try:
        client = get_client()
        data = client.get_email(email_id)
        print_email_status(data)
    except (ResendError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def domains():
    """Manage domains."""
    pass


@domains.command("list")
def domains_list():
    """List all domains."""
    try:
        client = get_client()
        items = client.list_domains()
        print_domains(items)
    except (ResendError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@domains.command("verify")
@click.argument("domain_id")
def domains_verify(domain_id):
    """Verify a domain."""
    try:
        client = get_client()
        data = client.verify_domain(domain_id)
        print_domain_verified(data)
    except (ResendError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def audiences():
    """Manage audiences."""
    pass


@audiences.command("list")
def audiences_list():
    """List all audiences."""
    try:
        client = get_client()
        items = client.list_audiences()
        print_audiences(items)
    except (ResendError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@audiences.command("create")
@click.option("--name", required=True, help="Audience name")
def audiences_create(name):
    """Create an audience."""
    try:
        client = get_client()
        data = client.create_audience(name)
        print_audience_created(data)
    except (ResendError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@audiences.command("remove")
@click.argument("audience_id")
def audiences_remove(audience_id):
    """Remove an audience."""
    try:
        client = get_client()
        data = client.delete_audience(audience_id)
        print_audience_deleted(data)
    except (ResendError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def contacts():
    """Manage contacts."""
    pass


@contacts.command("list")
@click.option("--audience", required=True, help="Audience ID")
def contacts_list(audience):
    """List contacts in an audience."""
    try:
        client = get_client()
        items = client.list_contacts(audience)
        print_contacts(items)
    except (ResendError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@contacts.command("add")
@click.option("--audience", required=True, help="Audience ID")
@click.option("--email", required=True, help="Contact email")
@click.option("--first-name", default=None, help="First name")
@click.option("--last-name", default=None, help="Last name")
def contacts_add(audience, email, first_name, last_name):
    """Add a contact to an audience."""
    try:
        client = get_client()
        kwargs = {}
        if first_name:
            kwargs["first_name"] = first_name
        if last_name:
            kwargs["last_name"] = last_name
        data = client.create_contact(audience, email, **kwargs)
        print_contact_created(data)
    except (ResendError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@contacts.command("remove")
@click.option("--audience", required=True, help="Audience ID")
@click.option("--email", required=True, help="Contact email/ID to remove")
def contacts_remove(audience, email):
    """Remove a contact from an audience."""
    try:
        client = get_client()
        data = client.delete_contact(audience, email)
        print_contact_deleted(data)
    except (ResendError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    cli()


if __name__ == "__main__":
    main()
