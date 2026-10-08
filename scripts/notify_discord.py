"""Send a message to the Discord alert channel.

The webhook URL is a secret: it is read from DISCORD_WEBHOOK_URL, either from
the environment (CI) or from the local .env file (never committed).

Usage (from the project root):
    python scripts/notify_discord.py "your message"
"""
import logging
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DISCORD_LIMIT = 1900  # Discord allows 2000 characters per message


def send(message: str) -> None:
    """Post one message to the Discord webhook; fail loudly on errors."""
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not url:
        raise RuntimeError("DISCORD_WEBHOOK_URL is not set (see .env.example)")
    response = requests.post(url, json={"content": message[:DISCORD_LIMIT]}, timeout=15)
    response.raise_for_status()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    send(" ".join(sys.argv[1:]) or "Test message from azure-distribution-pipeline")
    logging.info("Message sent to Discord")