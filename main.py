
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
