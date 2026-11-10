import subprocess
import os

def assemble_synchronized_video(scene_clip_paths, output_path="output_video.mp4"):
    print("Assembling final synchronized documentary video...")
    
    concat_list_path = "video_concat_list.txt"
    with open(concat_list_path, "w") as f:
        for clip in scene_clip_paths:
            f.write(f"file '{os.path.abspath(clip)}'\n")

    # Concatenate pre-synchronized video+audio clips cleanly
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        output_path
    ]
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print(f"SUCCESS: Perfectly synced documentary assembled at {output_path}")
    else:
        print("FFmpeg Error:", result.stderr.decode("utf-8"))

if __name__ == "__main__":
    assemble_synchronized_video([])
