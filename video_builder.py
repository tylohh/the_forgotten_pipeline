import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger("Pipeline")

def generate_subtitles(audio_path: Path, script_text: str, srt_path: Path):
    words = script_text.split()
    chunks = [" ".join(words[i:i+6]) for i in range(0, len(words), 6)]
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    duration = float(result.stdout.strip() or 30.0)
    time_per_chunk = duration / max(len(chunks), 1)
    
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            start_sec = i * time_per_chunk
            end_sec = (i + 1) * time_per_chunk
            def fmt(s):
                hrs = int(s // 3600)
                mins = int((s % 3600) // 60)
                secs = int(s % 60)
                millis = int((s - int(s)) * 1000)
                return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"
            f.write(f"{i+1}\n{fmt(start_sec)} --> {fmt(end_sec)}\n{chunk}\n\n")

def assemble_video(audio_path: Path, clips: list[Path], script_text: str, output_path: Path) -> Path:
    logger.info("Assembling video using FFmpeg...")
    episode_dir = output_path.parent
    srt_path = episode_dir / "captions.srt"
    generate_subtitles(audio_path, script_text, srt_path)

    inputs, filter_chains = [], []
    for idx, clip in enumerate(clips):
        inputs.extend(["-stream_loop", "-1", "-i", str(clip)])
        filter_chains.append(f"[{idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v{idx}];")

    num_clips = len(clips)
    concat_inputs = "".join([f"[v{i}]" for i in range(num_clips)])
    concat_filter = f"{''.join(filter_chains)}{concat_inputs}concat=n={num_clips}:v=1:a=0[vbase];"
    escaped_srt = str(srt_path).replace("\\", "/").replace(":", "\\:")
    subtitle_filter = f"[vbase]subtitles='{escaped_srt}':force_style='FontSize=22,FontName=Arial,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=250'[vfinal]"

    cmd = [
        "ffmpeg", "-y", *inputs, "-i", str(audio_path),
        "-filter_complex", concat_filter + subtitle_filter,
        "-map", "[vfinal]", "-map", f"{num_clips}:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(output_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg assembly failed: {res.stderr}")
    return output_path
