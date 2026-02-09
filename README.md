# resend-cli

CLI tool for the [Resend](https://resend.com) email API. Send emails, check your inbox, manage domains, audiences, and contacts from the terminal. Built for [OpenClaw](https://github.com/openclaw/openclaw) agents but works standalone too.

## Install

```bash
git clone https://github.com/auriwren/resend-cli.git
cd resend-cli
pip install -e .
```

## Configuration

Create a credentials file:

```bash
mkdir -p ~/.openclaw/credentials
cat > ~/.openclaw/credentials/resend.env << 'EOF'
RESEND_API_KEY=re_your_api_key_here
RESEND_FROM="Your Name <you@yourdomain.com>"
RESEND_REPLY_TO=you@yourdomain.com
RESEND_SIGNATURE="-- Your Name, Your Title"
EOF
chmod 600 ~/.openclaw/credentials/resend.env
```

Get your API key from [resend.com/api-keys](https://resend.com/api-keys).

All config values can also be set as environment variables (which take precedence over the file).

| Variable | Purpose | Required |
|---|---|---|
| `RESEND_API_KEY` | Resend API key | Yes |
| `RESEND_FROM` | Default sender (e.g. `Your Name <you@domain.com>`) | No |
| `RESEND_REPLY_TO` | Default reply-to address | No |
| `RESEND_SIGNATURE` | Signature appended when `--sign` is used | No |

## Usage

```bash
# Send email
resend-cli send --to "user@example.com" --subject "Hello" --text "Hi there"
resend-cli send --to "user@example.com" --subject "Report" --html-file report.html --attach data.csv
resend-cli send --to "user@example.com" --subject "Hello" --text "Hi" --sign --dry-run

# Override sender for a single email
resend-cli send --to "user@example.com" --subject "Hi" --text "Hello" \
  --from "Other Name <other@domain.com>"

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

## Setting Up for Your OpenClaw Agent

### 1. Install on your OpenClaw host

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

Follow the [Configuration](#configuration) section above. At minimum you need the API key. Setting `RESEND_FROM` and `RESEND_REPLY_TO` means your agent won't need to specify them on every send.

### 3. Tell your agent about it

Add to your `TOOLS.md`:

```markdown
## Email (Resend)
- **CLI:** `resend-cli` (installed in workspace)
- **Send:** `resend-cli send --to "addr" --subject "Sub" --text "Body"`
- **HTML:** `resend-cli send --to "addr" --subject "Sub" --html-file path/to/email.html`
- **Inbox:** `resend-cli inbox` (list inbound), `resend-cli inbox read <id>` (read one)
- **Status:** `resend-cli status <email-id>` (delivery status of sent email)
- **Credentials:** ~/.openclaw/credentials/resend.env
```

### 4. One-shot setup prompt

Give your agent this to set everything up automatically:

> I have a Resend API key: [PASTE KEY]. My email domain is [YOUR DOMAIN] and I want to send from [YOUR NAME] <[YOUR EMAIL]>. Clone auriwren/resend-cli into the workspace, install it, create the credentials file, and test it with a dry-run send to confirm it works.

## License

MIT
