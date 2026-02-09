# resend-cli

CLI tool for the [Resend](https://resend.com) email API.

## Install

```bash
pip install -e .
```

## Usage

Set `RESEND_API_KEY` env var or place it in `~/.openclaw/credentials/resend.env`.

```bash
# Send email
resend-cli send --to "user@example.com" --subject "Hello" --text "Hi there"

# Check inbox
resend-cli inbox
resend-cli inbox read <id>

# Email status
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
resend-cli contacts add --audience <id> --email "user@example.com"
resend-cli contacts remove --audience <id> --email <contact-id>
```

## License

MIT
