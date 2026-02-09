# resend-cli

CLI tool for the [Resend](https://resend.com) email API. Send emails, check your inbox, manage domains, audiences, and contacts from the terminal.

## Install

```bash
git clone https://github.com/auriwren/resend-cli.git
cd resend-cli
pip install -e .
```

## Usage

Set `RESEND_API_KEY` env var or place it in `~/.openclaw/credentials/resend.env`.

```bash
# Send email
resend-cli send --to "user@example.com" --subject "Hello" --text "Hi there"
resend-cli send --to "user@example.com" --subject "Report" --html-file report.html --attach data.csv
resend-cli send --to "user@example.com" --subject "Hello" --text "Hi" --sign --dry-run

# Check inbox (inbound emails)
resend-cli inbox
resend-cli inbox --limit 5
resend-cli inbox read <id>

# Sent email status
resend-cli status <email-id>

# Domains
resend-cli domains list
resend-cli domains verify <id>

# Audiences
resend-cli audiences list
resend-cli audiences create --name "Newsletter"
resend-cli audiences remove <id>

# Contacts
resend-cli contacts list --audience <id>
resend-cli contacts add --audience <id> --email "user@example.com" --first-name "Jane"
resend-cli contacts remove --audience <id> --email <contact-id>
```

## Setting Up resend-cli for Your OpenClaw Agent

This section walks you through giving your OpenClaw agent the ability to send and receive email via Resend.

### 1. Install on your OpenClaw host

SSH into your host (or use the sandbox terminal) and install:

```bash
cd ~/.openclaw/workspace
git clone https://github.com/auriwren/resend-cli.git
cd resend-cli
pip install -e .

# Verify it's on PATH
resend-cli --help
```

If `pip install` complains about externally managed environments, add `--break-system-packages` or use a virtualenv that your agent's shell inherits.

### 2. Set up credentials

Create a credentials file so the agent can authenticate without env vars in every session:

```bash
mkdir -p ~/.openclaw/credentials
echo 'RESEND_API_KEY=re_your_api_key_here' > ~/.openclaw/credentials/resend.env
chmod 600 ~/.openclaw/credentials/resend.env
```

Get your API key from [resend.com/api-keys](https://resend.com/api-keys). The tool checks the `RESEND_API_KEY` environment variable first, then falls back to this file.

### 3. Tell your agent about it

Add a section to your `TOOLS.md` (or whichever context file your agent reads) so it knows the tool exists and how to use it:

```markdown
## Email (Resend)
- **CLI:** `resend-cli` (installed globally)
- **Send:** `resend-cli send --to "addr" --subject "Sub" --text "Body"`
- **Inbox:** `resend-cli inbox` (list inbound), `resend-cli inbox read <id>` (read one)
- **Status:** `resend-cli status <email-id>` (delivery status of sent email)
- **Domains:** `resend-cli domains list` / `resend-cli domains verify <id>`
- **Default from:** Your Name <you@yourdomain.com>
- **Credentials:** ~/.openclaw/credentials/resend.env
```

You can also include instructions in a prompt:

> "When I ask you to send an email, use the `resend-cli send` command. Check for new emails with `resend-cli inbox`. Always use `--dry-run` first for emails to new recipients."

### 4. Example commands your agent would run

Here's what typical agent usage looks like in practice:

```bash
# Agent checks for new inbound emails
resend-cli inbox --limit 10

# Agent reads a specific inbound email
resend-cli inbox read abc123-def456

# Agent sends a reply
resend-cli send --to "colleague@example.com" --subject "Re: Project update" \
  --text "Thanks for the update. I'll review the doc and get back to you." --sign

# Agent sends with an attachment
resend-cli send --to "boss@example.com" --subject "Weekly report" \
  --text "Attached is this week's report." --attach /tmp/report.pdf

# Agent checks delivery status
resend-cli status abc123-def456

# Dry run before sending to a new contact
resend-cli send --to "newperson@example.com" --subject "Introduction" \
  --text "Hello, nice to meet you." --dry-run
```

### 5. Customize the default sender and reply-to

Out of the box, resend-cli sends from `Auri Wren <auri@auri.email>`. To change this for your own domain, edit `resend_cli/config.py`:

```python
DEFAULT_FROM = "Your Agent <agent@yourdomain.com>"
DEFAULT_REPLY_TO = "agent@yourdomain.com"
DEFAULT_SIGNATURE = "-- Your Agent Name"
```

Or override per-command without editing any code:

```bash
resend-cli send --to "user@example.com" --subject "Hi" --text "Hello" \
  --from "My Agent <agent@mydomain.com>" --reply-to "agent@mydomain.com"
```

If your agent always uses a custom sender, add the `--from` and `--reply-to` flags to the example in your `TOOLS.md` so it picks them up automatically.

## License

MIT
