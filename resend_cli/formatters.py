"""Rich output formatting for CLI results."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_email_sent(data: dict) -> None:
    console.print(Panel(f"[green]Email sent![/green]\nID: {data.get('id', 'N/A')}"))


def print_email_status(data: dict) -> None:
    table = Table(title="Email Status")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for key in ("id", "from", "to", "subject", "created_at", "last_event"):
        val = data.get(key, "N/A")
        if isinstance(val, list):
            val = ", ".join(val)
        table.add_row(key, str(val))
    console.print(table)


def print_inbound_list(items: list) -> None:
    if not items:
        console.print("[dim]No inbound emails found.[/dim]")
        return
    table = Table(title="Inbound Emails")
    table.add_column("ID", style="cyan")
    table.add_column("From")
    table.add_column("Subject")
    table.add_column("Date")
    for item in items:
        table.add_row(
            str(item.get("id", "")),
            str(item.get("from", "")),
            str(item.get("subject", "")),
            str(item.get("created_at", "")),
        )
    console.print(table)


def print_inbound_detail(data: dict) -> None:
    table = Table(title="Inbound Email")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for key in ("id", "from", "to", "subject", "created_at", "text", "html"):
        val = data.get(key, "N/A")
        if isinstance(val, list):
            val = ", ".join(val)
        table.add_row(key, str(val))
    console.print(table)


def print_domains(items: list) -> None:
    if not items:
        console.print("[dim]No domains found.[/dim]")
        return
    table = Table(title="Domains")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Status")
    for item in items:
        table.add_row(
            str(item.get("id", "")),
            str(item.get("name", "")),
            str(item.get("status", "")),
        )
    console.print(table)


def print_domain_verified(data: dict) -> None:
    console.print(Panel(f"[green]Domain verification initiated[/green]\nID: {data.get('id', 'N/A') if data else 'N/A'}"))


def print_audiences(items: list) -> None:
    if not items:
        console.print("[dim]No audiences found.[/dim]")
        return
    table = Table(title="Audiences")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    for item in items:
        table.add_row(str(item.get("id", "")), str(item.get("name", "")))
    console.print(table)


def print_audience_created(data: dict) -> None:
    console.print(Panel(f"[green]Audience created![/green]\nID: {data.get('id', 'N/A')}"))


def print_audience_deleted(data: dict) -> None:
    console.print(Panel("[green]Audience deleted.[/green]"))


def print_contacts(items: list) -> None:
    if not items:
        console.print("[dim]No contacts found.[/dim]")
        return
    table = Table(title="Contacts")
    table.add_column("ID", style="cyan")
    table.add_column("Email")
    table.add_column("First Name")
    table.add_column("Last Name")
    for item in items:
        table.add_row(
            str(item.get("id", "")),
            str(item.get("email", "")),
            str(item.get("first_name", "")),
            str(item.get("last_name", "")),
        )
    console.print(table)


def print_contact_created(data: dict) -> None:
    console.print(Panel(f"[green]Contact created![/green]\nID: {data.get('id', 'N/A')}"))


def print_contact_deleted(data: dict) -> None:
    console.print(Panel("[green]Contact deleted.[/green]"))


def print_dry_run(payload: dict) -> None:
    import json
    console.print(Panel(json.dumps(payload, indent=2), title="[yellow]DRY RUN[/yellow]"))
