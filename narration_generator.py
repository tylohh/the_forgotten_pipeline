import os
import subprocess
from gtts import gTTS

def generate_scene_narration(scenes):
    os.makedirs("assets", exist_ok=True)
    audio_paths = []
    
    for i, scene in enumerate(scenes, 1):
        text = scene.get("narration", "")
        print(f"Generating synchronized narration for Scene {i}...")
        temp_raw = f"assets/temp_raw_{i}.mp3"
        out_audio = f"assets/scene_audio_{i}.mp3"
        
        clean_text = text.replace(",", "").replace(";", "").replace(" - ", " ").replace("—", " ")
        
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(temp_raw)
        
        # Speed up audio and remove silence
        cmd = [
            "/opt/homebrew/bin/ffmpeg", "-y",
            "-i", temp_raw,
            "-filter:a", "atempo=1.35,silenceremove=start_periods=1:start_duration=0:start_threshold=-40dB:stop_periods=-1:stop_duration=0.04:stop_threshold=-40dB",
            "-b:a", "192k",
            out_audio
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if os.path.exists(temp_raw):
            os.remove(temp_raw)
            
        audio_paths.append(out_audio)
        
    return audio_paths

if __name__ == "__main__":
    generate_scene_narration([{"narration": "Test synchronized narration audio."}])
