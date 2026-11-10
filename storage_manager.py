import json
import logging
from pathlib import Path
import config

logger = logging.getLogger("Pipeline")

def load_history() -> list:
    if not config.HISTORY_FILE.exists():
        return []
    try:
        with open(config.HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_episode_history(record: dict):
    history = load_history()
    history.append(record)
    with open(config.HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
