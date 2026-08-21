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
    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML", reply_markup: dict | None = None) -> dict:
        url = self.BASE_URL.format(token=self.token, method="sendMessage")
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        response = self.session.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    def edit_message_text(self, chat_id: int, message_id: int, text: str, parse_mode: str = "HTML", reply_markup: dict | None = None) -> dict:
        url = self.BASE_URL.format(token=self.token, method="editMessageText")
        payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode}
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        response = self.session.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    def edit_message_reply_markup(self, chat_id: int, message_id: int, reply_markup: dict) -> dict:
        url = self.BASE_URL.format(token=self.token, method="editMessageReplyMarkup")
        payload = {"chat_id": chat_id, "message_id": message_id, "reply_markup": reply_markup}
        response = self.session.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    def answer_callback_query(self, callback_query_id: str, text: str | None = None) -> dict:
        url = self.BASE_URL.format(token=self.token, method="answerCallbackQuery")
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        response = self.session.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_updates(self, offset: int | None = None, timeout: int = 30) -> dict:
        url = self.BASE_URL.format(token=self.token, method="getUpdates")
        params = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset
        response = self.session.get(url, params=params, timeout=timeout + 10)
        response.raise_for_status()
        return response.json()