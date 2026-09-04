"""Create a local .env with independent random secrets; never overwrite one."""
from pathlib import Path
import secrets


def setup():
    root = Path(__file__).resolve().parents[1]
    destination = root / ".env"
    source = (root / ".env.example").read_text()
    replacements = {
        "DB_PASSWORD": secrets.token_urlsafe(32),
        "ADMIN_PASSWORD": secrets.token_urlsafe(24),
        "ADMIN_SESSION_SECRET": secrets.token_urlsafe(48),
        "STATS_IP_HASH_SECRET": secrets.token_urlsafe(48),
        "DEMO_MODE": "true",
    }
    lines = []
    for line in source.splitlines():
        key = line.split("=", 1)[0]
        lines.append(f"{key}={replacements[key]}" if key in replacements else line)
    # Exclusive creation protects the user's existing local configuration.
    with destination.open("x") as output:
        destination.chmod(0o600)
        output.write("\n".join(lines) + "\n")
    print("Created .env with random secrets. Admin login/password are stored only in that local file.")


if __name__ == "__main__":
    setup()
