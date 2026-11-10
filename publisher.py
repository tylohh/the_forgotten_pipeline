import logging
from pathlib import Path

logger = logging.getLogger("Pipeline")

def publish_youtube(video_path: Path, title: str, description: str, tags: list[str]) -> str:
    logger.info("YouTube publishing stub.")
    return "mock_yt_id"

def publish_webhook(video_path: Path, metadata: dict):
    logger.info("Webhook publishing stub.")
