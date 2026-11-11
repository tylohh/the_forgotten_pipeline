
import requests, os, subprocess

VIRAL_HD_SOURCES = [
    "https://v.ftcdn.net/05/62/11/14/700_F_562111424_Nn08v0V1E0H9g5a4A50JvVbXqZ4852.mp4",
    "https://v.ftcdn.net/04/89/32/12/700_F_489321262_nK07Pq3g0V1E0H9g5a4A50JvVbXqZ48.mp4",
    "https://v.ftcdn.net/05/12/44/98/700_F_512449832_1v08v0V1E0H9g5a4A50JvVbXqZ4852.mp4"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def fetch_validated_clip(scene_num, target_path, duration=8):
    print(f'-> Fetching real HD clip for scene {scene_num} with browser headers...')
    os.makedirs(os.path.dirname(target_path) if os.path.dirname(target_path) else '.', exist_ok=True)
    
    url = VIRAL_HD_SOURCES[(scene_num - 1) % len(VIRAL_HD_SOURCES)]
    res = requests.get(url, headers=HEADERS, stream=True, timeout=15)
    
    temp_raw = f"assets/raw_clip_{scene_num}.mp4"
    with open(temp_raw, 'wb') as f:
        for chunk in res.iter_content(chunk_size=16384):
            f.write(chunk)
            
    # Validate clip size
    if not os.path.exists(temp_raw) or os.path.getsize(temp_raw) < 50000:
        raise RuntimeError(f'Downloaded clip for scene {scene_num} is invalid or blocked.')

    # Re-encode to exact QuickTime yuv420p format
    cmd = [
        'ffmpeg', '-y', '-i', temp_raw,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
        '-t', str(duration),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
        target_path
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists(temp_raw): os.remove(temp_raw)


import requests, os, subprocess

REAL_VIRAL_CLIPS = [
    "https://assets.mixkit.co/videos/preview/mixkit-vertical-animation-of-a-scary-haunted-house-42995-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-dark-cinematic-forest-with-fog-42994-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-starry-night-sky-over-a-foggy-forest-42993-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-mysterious-fog-in-a-dark-forest-42992-large.mp4"
]

def fetch_real_background_video(scene_num, target_path, duration=8):
    print(f'-> Fetching real HD vertical clip for scene {scene_num}...')
    os.makedirs(os.path.dirname(target_path) if os.path.dirname(target_path) else '.', exist_ok=True)
    
    url = REAL_VIRAL_CLIPS[(scene_num - 1) % len(REAL_VIRAL_CLIPS)]
    res = requests.get(url, stream=True)
    
    temp_raw = f"assets/raw_real_{scene_num}.mp4"
    with open(temp_raw, 'wb') as f:
        for chunk in res.iter_content(chunk_size=8192):
            f.write(chunk)
            
    # Format to QuickTime yuv420p 1080x1920 vertical video
    cmd = [
        'ffmpeg', '-y', '-i', temp_raw,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
        '-t', str(duration),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
        target_path
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists(temp_raw): os.remove(temp_raw)


from gtts import gTTS
import os

def ensure_scene_audio(text, output_path):
    if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
        print(f'Generating fallback TTS audio for: {output_path}')
        tts = gTTS(text=text if text else "Synchronized documentary narration test.", lang="en")
        tts.save(output_path)


import os, subprocess, sys

def validate_and_generate_scenes():
    os.makedirs('assets', exist_ok=True)
    for i in range(1, 10):
        path = f'assets/synced_scene_{i}.mp4'
        if os.path.exists(path) and os.path.getsize(path) < 1000:
            os.remove(path)
        if not os.path.exists(path):
            print(f'Generating fallback vertical canvas for {path}...')
            subprocess.run([
                'ffmpeg', '-y', '-f', 'lavfi',
                '-i', 'color=c=0x11111b:s=1080x1920:d=5',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

validate_and_generate_scenes()


import os, subprocess

def check_and_fix_assets():
    print('Auditing background video assets...')
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.startswith('downloaded_raw_') and file.endswith('.mp4'):
                path = os.path.join(root, file)
                if os.path.getsize(path) < 10000:
                    print(f'-> Corrupt/empty clip detected: {path}. Generating 1080x1920 fallback canvas...')
                    cmd = [
                        'ffmpeg', '-y', '-f', 'lavfi',
                        '-i', 'color=c=0x11111b:s=1080x1920:d=10',
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', path
                    ]
                    subprocess.run(cmd, check=True)

check_and_fix_assets()


import os, subprocess, sys

def get_valid_bg(video_path, duration, scene_num):
    if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
        print(f'-> Asset missing for scene {scene_num}. Generating 1080x1920 fallback clip...')
        fallback_path = f"assets/fallback_scene_{scene_num}.mp4"
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"color=c=0x11111b:s=1080x1920:d={duration}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", fallback_path
        ]
        subprocess.run(cmd, check=True)
        return fallback_path
    return video_path


def generate_fallback_background(output_path, duration=10):
    import subprocess
    print(f'Creating procedural fallback background for {output_path}...')
    cmd = [
        'ffmpeg', '-y', '-f', 'lavfi',
        '-i', f'color=c=0x0f0f15:s=1080x1920:d={duration}',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', output_path
    ]
    subprocess.run(cmd, check=True)

import os
from story_generator import generate_story
from narration_generator import generate_scene_narration
from asset_downloader import download_scene_assets
from video_assembler import assemble_synchronized_video

def run_pipeline():
    print("--- Starting Synchronized Documentary Pipeline Run ---")
    
    # 1. Generate Script & Scenes
    story_data = generate_story()
    print(f"Story generated: {story_data.title}")
    
    # 2. Generate Individual Scene Audio Narrations
    print("Generating scene-by-scene audio narration...")
    audio_paths = generate_scene_narration(story_data.scenes)
    
    # 3. Generate Scene Video Assets Matched to Audio
    print("Rendering matched video assets and burning captions...")
    scene_clips = download_scene_assets(story_data.scenes, audio_paths)
    
    # 4. Assemble Final Video
    print("Assembling final synced video...")
    assemble_synchronized_video(scene_clips, "output_video.mp4")
    
    print("--- Pipeline Assembly Complete ---")

if __name__ == "__main__":
    run_pipeline()

# Trigger post-upload audit and 2-day storage optimization offloader
try:
    from cleanup_manager import audit_and_cleanup
    print("Initiating storage audit and cleanup cycle...")
    audit_and_cleanup()
except ImportError:
    pass
