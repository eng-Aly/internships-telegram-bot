# bot/telegram_client.py
import os
import requests


class TelegramClient:
    """Thin wrapper around the Telegram Bot API for sending messages."""

    BASE_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, token: str | None = None):
        self.token = token or os.environ["TELEGRAM_BOT_API_KEY"]
        self.session = requests.Session()

    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> dict:
        """Send a message to a single chat_id. Returns Telegram's response JSON."""
        url = self.BASE_URL.format(token=self.token, method="sendMessage")
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False,
        }
        response = self.session.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()