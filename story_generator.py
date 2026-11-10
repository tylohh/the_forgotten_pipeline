import json
import os

History_FILE = "history.json"

class StoryDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        scenes = self.get("scenes", [])
        # FIX: Use space instead of newline to eliminate gTTS unnatural pauses between scenes
        self.narration_script = " ".join(scene.get("narration", "") for scene in scenes)
    def model_dump_json(self, indent=None, **kwargs):
        return json.dumps(self, indent=indent)
    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(f"'StoryDict' object has no attribute '{key}'")

def load_history():
    if os.path.exists(History_FILE):
        with open(History_FILE, "r") as f:
            return json.load(f)
    return {"last_topic": None, "part_number": 1}

def save_history(topic, part):
    with open(History_FILE, "w") as f:
        json.dump({"last_topic": topic, "part_number": part}, f)

def generate_story():
    history = load_history()
    topic = history.get("last_topic")
    part = history.get("part_number", 1)
    
    if not topic or part > 3:
        topic = "The Mysterious Disappearance of Roanoke Colony"
        part = 1
    else:
        part += 1

    print(f"Generating Cinematic Script: {topic} (Part {part})...")
    
    if part == 1:
        scenes = [
            {
                "scene_number": 1,
                "narration": "In 1587, over one hundred English colonists landed on a lonely island, completely unaware they were walking into a nightmare.",
                "visual_prompt": "A dark stormy coastline with an old wooden colonial ship anchored offshore."
            },
            {
                "scene_number": 2,
                "narration": "Three years later, supply ships returned to find the entire settlement abandoned. Not a single body, struggle, or sign of life remained.",
                "visual_prompt": "An eerie, overgrown abandoned wooden village in the deep foggy woods."
            },
            {
                "scene_number": 3,
                "narration": "The only clue left behind was a single word carved into a wooden post. Part two uncovers the dark secret. Like and subscribe to follow The Forgotten.",
                "visual_prompt": "A mysterious old wooden post with a carved word in the dark."
            }
        ]
    else:
        scenes = [
            {
                "scene_number": 1,
                "narration": f"Continuing {topic}: modern archaeologists discovered strange soil anomalies and hidden artifacts buried deep beneath the forest floor.",
                "visual_prompt": "A glowing archaeological dig site in the dark woods at midnight."
            },
            {
                "scene_number": 2,
                "narration": "Local Native American tribes spoke of a terrifying vanishing curse that claimed anyone who crossed the sacred boundary.",
                "visual_prompt": "An ancient tribal totem pole glowing under moonlight in thick fog."
            },
            {
                "scene_number": 3,
                "narration": "The final truth behind the lost colonists is revealed next. Like and subscribe to stay tuned to The Forgotten.",
                "visual_prompt": "Dark cinematic title card: Subscribe for Part 3."
            }
        ]
        
    save_history(topic, part)
    
    data = {
        "title": f"{topic} - Part {part}",
        "hook": f"True crime breakdown of {topic}.",
        "scenes": scenes
    }
    return StoryDict(data)
