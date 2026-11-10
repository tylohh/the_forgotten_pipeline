import subprocess
import json
import logging
from pathlib import Path

logger = logging.getLogger("Pipeline")

def validate_video_file(file_path: Path) -> bool:
    if not file_path.exists() or file_path.stat().st_size < 1_000_000:
        return False
    cmd = ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,duration:format=duration,size", "-of", "json", str(file_path)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        return False
    data = json.loads(res.stdout)
    streams = data.get("streams", [])
    has_video = any(s.get("codec_type") == "video" for s in streams)
    has_audio = any(s.get("codec_type") == "audio" for s in streams)
    if not (has_video and has_audio):
        return False
    video_stream = next(s for s in streams if s.get("codec_type") == "video")
    if int(video_stream.get("width", 0)) != 1080 or int(video_stream.get("height", 0)) != 1920:
        return False
    return True
