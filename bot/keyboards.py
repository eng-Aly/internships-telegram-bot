from bot.config import JOB_LEVELS, FIELDS


def _build_multiselect_keyboard(options: list[str], selected: list[str], prefix: str) -> dict:
    buttons = []
    for i, label in enumerate(options):
        mark = "✅" if label in selected else "⬜"
        buttons.append([{"text": f"{mark} {label}", "callback_data": f"{prefix}:{i}"}])
    buttons.append([{"text": "➡️ Done", "callback_data": f"{prefix}:done"}])
    return {"inline_keyboard": buttons}


def build_job_level_keyboard(selected: list[str]) -> dict:
    return _build_multiselect_keyboard(JOB_LEVELS, selected, "lvl")


def build_field_keyboard(selected: list[str]) -> dict:
    return _build_multiselect_keyboard(FIELDS, selected, "fld")