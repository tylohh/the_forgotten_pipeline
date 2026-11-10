import os
import requests
import logging
from pathlib import Path
from elevenlabs.client import ElevenLabs
import config

logger = logging.getLogger("Pipeline")

def generate_narration(text: str, output_path: Path) -> Path:
    logger.info("Generating voiceover audio via ElevenLabs...")
    if not config.ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY is missing.")
    client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=config.ELEVENLABS_VOICE_ID,
        model_id="eleven_multilingual_v2"
    )
    with open(output_path, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)
    return output_path

def fetch_visual_assets(prompts: list[str], target_dir: Path) -> list[Path]:
    logger.info("Fetching royalty-free visual assets from Pexels...")
    downloaded_files = []
    headers = {"Authorization": config.PEXELS_API_KEY}
    for idx, prompt in enumerate(prompts):
        url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(prompt)}&per_page=3&orientation=portrait"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            data = res.json()
            videos = data.get("videos", [])
            if videos:
                video_files = videos[0].get("video_files", [])
                hd_file = next((vf for vf in video_files if vf.get("width") == 1080 and vf.get("height") == 1920), None)
                if not hd_file and video_files:
                    hd_file = video_files[0]
                v_url = hd_file.get("link")
                file_path = target_dir / f"clip_{idx}.mp4"
                v_res = requests.get(v_url, stream=True, timeout=15)
                with open(file_path, "wb") as f:
                    for chunk in v_res.iter_content(chunk_size=1024*1024):
                        f.write(chunk)
                downloaded_files.append(file_path)
        except Exception as e:
            logger.error(f"Error downloading asset for '{prompt}': {e}")

    if not downloaded_files:
        fallback_path = target_dir / "fallback.jpg"
        os.system(f"ffmpeg -y -f lavfi -i color=c=0x0f172a:s=1080x1920:d=5 -frames:v 1 {fallback_path}")
        downloaded_files.append(fallback_path)
    return downloaded_files
