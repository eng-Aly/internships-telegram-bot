# bot/test_send.py
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"  # bot/ -> project root
load_dotenv(env_path)

from bot.telegram_client import TelegramClient


client = TelegramClient()



result = client.send_message(
    chat_id=int(os.environ["TELEGRAM_CHAT_ID"]),
    text="hello",
)
print(result)