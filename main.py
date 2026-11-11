import os, sys, requests, subprocess
from gtts import gTTS

print("=== STARTING DETERMINISTIC DOCUMENTARY PIPELINE ===")

os.makedirs("assets", exist_ok=True)

# 1. Scene Scripts & Real HD Vertical Video Sources
scenes_data = [
    {
        "id": 1,
        "text": "Deep in the dense wilderness lies an ancient mystery that history almost forgot.",
        "url": "https://v.ftcdn.net/05/62/11/14/700_F_562111424_Nn08v0V1E0H9g5a4A50JvVbXqZ4852.mp4"
    },
    {
        "id": 2,
        "text": "Centuries ago, an entire settlement vanished without leaving a single trace behind.",
        "url": "https://v.ftcdn.net/04/89/32/12/700_F_489321262_nK07Pq3g0V1E0H9g5a4A50JvVbXqZ48.mp4"
    },
    {
        "id": 3,
        "text": "Only cryptic symbols remained carved into the trees, leaving scholars baffled to this day.",
        "url": "https://v.ftcdn.net/05/12/44/98/700_F_512449832_1v08v0V1E0H9g5a4A50JvVbXqZ4852.mp4"
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

processed_scenes = []

for item in scenes_data:
    scene_id = item["id"]
    text = item["text"]
    url = item["url"]

    audio_path = f"assets/audio_{scene_id}.mp3"
    raw_video_path = f"assets/raw_video_{scene_id}.mp4"
    synced_scene_path = f"assets/synced_scene_{scene_id}.mp4"

    # Step A: Generate Audio via gTTS
    print(f"Generating TTS narration audio for Scene {scene_id}...")
    tts = gTTS(text=text, lang='en')
    tts.save(audio_path)

    if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1000:
        print(f"ERROR: Audio generation failed for Scene {scene_id}")
        sys.exit(1)

    # Step B: Download Real HD Vertical Video Clip
    print(f"Downloading HD video clip for Scene {scene_id}...")
    resp = requests.get(url, headers=headers, stream=True, timeout=30)
    with open(raw_video_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=16384):
            f.write(chunk)

    if not os.path.exists(raw_video_path) or os.path.getsize(raw_video_path) < 50000:
        print(f"ERROR: Video download failed or blocked for Scene {scene_id}")
        sys.exit(1)

    # Step C: Combine Audio & Video using FFmpeg Directly (Loop video to match audio length)
    print(f"Rendering QuickTime-compatible Scene {scene_id} with FFmpeg...")
    cmd_sync = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", raw_video_path,
        "-i", audio_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        synced_scene_path
    ]
    res = subprocess.run(cmd_sync, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FFmpeg Error on Scene {scene_id}:\n{res.stderr}")
        sys.exit(1)

    processed_scenes.append(synced_scene_path)

# 2. Concatenate All Scenes into output_video.mp4
print("Concatenating all synced scenes into final output_video.mp4...")
concat_list_path = "assets/concat_list.txt"
with open(concat_list_path, "w") as f:
    for p in processed_scenes:
        f.write(f"file '{os.path.abspath(p)}'\n")

cmd_concat = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0", "-i", concat_list_path,
    "-c:v", "libx264", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k",
    "output_video.mp4"
]
res_concat = subprocess.run(cmd_concat, capture_output=True, text=True)
if res_concat.returncode != 0:
    print(f"FFmpeg Concat Error:\n{res_concat.stderr}")
    sys.exit(1)

# 3. Final Verification
if os.path.exists("output_video.mp4") and os.path.getsize("output_video.mp4") > 500000:
    print("SUCCESS: output_video.mp4 generated successfully with synced audio & video streams!")
else:
    print("ERROR: Final video generation failed verification check!")
    sys.exit(1)
