# src/utils/loader.py

import json
from pathlib import Path

def load_mood_music_map():
    data_path = Path(__file__).parent.parent.parent / "data" / "mood_music_map.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)
