import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from bot.telegram_client import TelegramClient
from bot.storage import UserStore
from bot.config import JOB_LEVELS, FIELDS
from bot.keyboards import build_job_level_keyboard, build_field_keyboard

client = TelegramClient()
store = UserStore()


def handle_start(message: dict):
    chat_id = message["chat"]["id"]
    store.get_or_create(chat_id)
    store.set_stage(chat_id, "job_level")
    client.send_message(
        chat_id,
        "👋 Welcome! Let's set up your job alerts.\n\n"
        "Step 1/2: Select the job level(s) you're interested in, then tap Done.",
        reply_markup=build_job_level_keyboard(selected=[]),
    )


def handle_callback(callback_query: dict):
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    prefix, value = callback_query["data"].split(":", 1)
    client.answer_callback_query(callback_query["id"])

    if prefix == "lvl":
        if value == "done":
            store.set_stage(chat_id, "field")
            client.edit_message_text(
                chat_id, message_id,
                "Step 2/2: Now select the field(s) you're interested in, then tap Done.",
                reply_markup=build_field_keyboard(selected=[]),
            )
            return
        label = JOB_LEVELS[int(value)]
        selected = store.toggle_job_level(chat_id, label)
        client.edit_message_reply_markup(chat_id, message_id, build_job_level_keyboard(selected))

    elif prefix == "fld":
        if value == "done":
            row = store.get(chat_id)
            store.set_stage(chat_id, "done")
            levels = ", ".join(json.loads(row["job_levels"])) or "None"
            fields = ", ".join(json.loads(row["fields"])) or "None"
            client.edit_message_text(
                chat_id, message_id,
                f"✅ You're all set!\n\n<b>Levels:</b> {levels}\n<b>Fields:</b> {fields}\n\n"
                "Use /set_preferences anytime to change these.",
            )
            return
        label = FIELDS[int(value)]
        selected = store.toggle_field(chat_id, label)
        client.edit_message_reply_markup(chat_id, message_id, build_field_keyboard(selected))


def run():
    offset = None
    print("Bot listening... (Ctrl+C to stop)")
    while True:
        updates = client.get_updates(offset=offset, timeout=30)
        for update in updates.get("result", []):
            offset = update["update_id"] + 1
            if "message" in update:
                text = update["message"].get("text", "")
                if text.startswith("/start") or text.startswith("/set_preferences"):
                    handle_start(update["message"])
            elif "callback_query" in update:
                handle_callback(update["callback_query"])


if __name__ == "__main__":
    run()