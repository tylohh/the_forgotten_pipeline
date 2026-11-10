import os
import subprocess

def get_audio_duration(audio_path):
    cmd = ["/opt/homebrew/bin/ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 5.0

def download_scene_assets(scenes, audio_paths):
    os.makedirs("assets", exist_ok=True)
    scene_clip_paths = []
    
    for i, (scene, audio_path) in enumerate(zip(scenes, audio_paths), start=1):
        prompt = scene.get("visual_prompt", "dark mysterious cinematic background loop")
        narration = scene.get("narration", "")
        duration = get_audio_duration(audio_path)
        print(f"Processing scene {i} ({duration:.2f}s)...")
        
        final_clip = f"assets/synced_scene_{i}.mp4"
        temp_downloaded = f"assets/downloaded_raw_{i}.mp4"
        temp_processed_video = f"assets/processed_broll_{i}.mp4"
        
        search_query = f"ytsearch1:vertical gameplay background loop {prompt[:20]}"
        print(f"-> Downloading real viral video for: '{search_query}'")
        
        subprocess.run([
            "venv/bin/yt-dlp",
            search_query,
            "-o", temp_downloaded,
            "--no-check-certificates",
            "--quiet", "--no-warnings"
        ])
        
        if not os.path.exists(temp_downloaded) or os.path.getsize(temp_downloaded) < 20000:
            fallback_url = "https://assets.mixkit.co/videos/preview/mixkit-abstract-animation-of-futuristic-lights-42845-large.mp4"
            print(f"-> Using direct viral backup source...")
            subprocess.run(["curl", "-s", "-L", fallback_url, "-o", temp_downloaded])

        subprocess.run([
            "/opt/homebrew/bin/ffmpeg", "-y",
            "-stream_loop", "10",
            "-i", temp_downloaded,
            "-t", str(duration),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,format=yuv420p,fps=30",
            "-an",
            temp_processed_video
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        frames_dir = f"assets/broll_frames_{i}"
        os.makedirs(frames_dir, exist_ok=True)
        subprocess.run(["/opt/homebrew/bin/ffmpeg", "-y", "-i", temp_processed_video, f"{frames_dir}/fr_%03d.png"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        from PIL import Image, ImageDraw, ImageFont
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 46)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 30)
            caption_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 48)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            caption_font = ImageFont.load_default()
            
        for f_file in sorted(os.listdir(frames_dir)):
            if f_file.endswith(".png"):
                f_path = os.path.join(frames_dir, f_file)
                im = Image.open(f_path).convert("RGB")
                draw = ImageDraw.Draw(im)
                
                draw.text((80, 120), "THE FORGOTTEN", fill=(230, 40, 40), font=title_font)
                draw.text((80, 180), f"PART {i}", fill=(210, 215, 225), font=subtitle_font)
                
                margin = 80
                max_width = 920
                words = narration.split()
                lines = []
                current_line = []
                for word in words:
                    current_line.append(word)
                    bbox = draw.textbbox((0, 0), " ".join(current_line), font=caption_font)
                    if bbox[2] > max_width:
                        current_line.pop()
                        lines.append(" ".join(current_line))
                        current_line = [word]
                if current_line:
                    lines.append(" ".join(current_line))
                    
                box_top = 950
                box_height = (len(lines) * 65) + 50
                draw.rectangle([(60, box_top), (1020, box_top + box_height)], fill=(0, 0, 0), outline=(70, 70, 80), width=3)
                
                offset = box_top + 25
                for line in lines:
                    draw.text((margin + 2, offset + 2), line, fill=(0, 0, 0), font=caption_font)
                    draw.text((margin, offset), line, fill=(255, 255, 255), font=caption_font)
                    offset += 65
                    
                im.save(f_path)

        subprocess.run([
            "/opt/homebrew/bin/ffmpeg", "-y",
            "-framerate", "30",
            "-i", f"{frames_dir}/fr_%03d.png",
            "-i", audio_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-shortest",
            final_clip
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        scene_clip_paths.append(final_clip)
        
    return scene_clip_paths
