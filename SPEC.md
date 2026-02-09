# resend-cli: Specification

## Overview
A Python CLI tool wrapping the full Resend API. Replaces ad-hoc curl/script calls with a proper, tested interface.

## Tech Stack
- Python 3.10+
- Click (CLI framework)
- requests (HTTP, avoids Cloudflare 403s with urllib)
- Rich (formatted output)
- pytest (testing)

## Credentials
- Reads `RESEND_API_KEY` from environment
- Falls back to `~/.openclaw/credentials/resend.env`
- Base URL: `https://api.resend.com`

## Default Sender
- From: `Auri Wren <auri@auri.email>`
- Reply-To: `auri@auri.email`
- Signature (appended to text/html when --sign flag used):
  `-- Auri Wren, Personal Assistant to Eiwe Lingefors`

## Command Groups

### `resend-cli send`
Send an email.
```
resend-cli send --to "addr@example.com" --subject "Subject" --text "Body"
resend-cli send --to "addr@example.com" --subject "Subject" --html "<h1>Hi</h1>"
resend-cli send --to "addr@example.com" --subject "Subject" --html-file path/to/email.html
resend-cli send --to "a@b.com" --cc "c@d.com" --bcc "e@f.com" --subject "Sub" --text "Body"
resend-cli send --to "a@b.com" --subject "Sub" --text "Body" --attach file.pdf
resend-cli send --to "a@b.com" --subject "Sub" --text "Body" --from "Other <other@auri.email>"
resend-cli send --to "a@b.com" --subject "Sub" --text "Body" --sign
resend-cli send --to "a@b.com" --subject "Sub" --text "Body" --tag category=onboarding
```

Options:
- `--to` (required, multiple)
- `--subject` (required)
- `--text` (body as plain text)
- `--html` (body as HTML string)
- `--html-file` (read HTML from file)
- `--text-file` (read text from file)
- `--from` (override sender, default: Auri Wren <auri@auri.email>)
- `--reply-to` (override reply-to)
- `--cc` (multiple)
- `--bcc` (multiple)
- `--attach` (multiple, file paths)
- `--sign` (append signature)
- `--tag` (multiple, key=value)
- `--idempotency-key` (prevent duplicates)
- `--dry-run` (print payload, don't send)

### `resend-cli inbox`
Check inbound emails (receiving endpoint).
```
resend-cli inbox                    # list recent inbound
resend-cli inbox --limit 5          # limit results
resend-cli inbox read <id>          # read specific inbound email
```

### `resend-cli status <email-id>`
Retrieve sent email status/details.
```
resend-cli status <id>              # show delivery status, timestamps
```

### `resend-cli domains`
List and manage domains.
```
resend-cli domains list
resend-cli domains verify <id>
```

### `resend-cli contacts`
Manage contacts/audiences.
```
resend-cli contacts list --audience <id>
resend-cli contacts add --audience <id> --email "x@y.com" --first-name "X"
resend-cli contacts remove --audience <id> --email "x@y.com"
```

### `resend-cli audiences`
Manage audiences.
```
resend-cli audiences list
resend-cli audiences create --name "Newsletter"
resend-cli audiences remove <id>
```

## Architecture

```
resend-cli/
  resend_cli/
    __init__.py
    cli.py          # Click entry point
    client.py       # ResendClient class (all API calls)
    config.py       # Credential loading, defaults
    formatters.py   # Rich output formatting
  tests/
    conftest.py     # Fixtures, mock client
    test_client.py  # Unit tests for API client (mocked)
    test_cli.py     # CLI integration tests
    test_config.py  # Config/credential tests
  setup.py
  pyproject.toml
  README.md
  LICENSE
  .gitignore
```

## Client Design
- `ResendClient` class wraps all API endpoints
- All HTTP via `requests.Session` with auth header
- Returns typed dicts, raises `ResendError` on failures
- Rate limit handling: respect 429 with retry-after
- Timeout: 30s default

## Testing Strategy
- Mock all HTTP calls with `unittest.mock.patch` on `requests.Session`
- Test each client method returns correct parsed response
- Test CLI commands produce correct output
- Test credential loading from env and file
- Test attachment encoding (base64)
- Test dry-run mode
- Target: 90%+ coverage

## Installation
```bash
cd resend-cli && pip install -e .
```
Creates `resend-cli` entry point on PATH.

## Key Behaviors
1. Always use `requests` (never `urllib`) to avoid Cloudflare 403
2. Default from/reply-to baked in but overridable
3. HTML emails: if --text not provided alongside --html, auto-generate plain text fallback
4. Attachments: base64-encode file contents, set filename from path
5. Inbound: GET /emails/receiving (NOT /emails/{id})
6. Sent status: GET /emails/{id}
7. Pretty-print all output with Rich (tables for lists, panels for single items)
