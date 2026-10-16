# src/utils/state.py

from enum import Enum

class DialogueState(str, Enum):
    INIT = "init"
    MOOD = "mood"
    COMFORT = "comfort"
    MUSIC = "music"
    REFLECT = "reflect"
    ESCALATE = "escalate"


class MoodState(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    RELAXED = "relaxed"
    FOCUSED = "focused"
    STRESSED = "stressed"
    EXCITED = "excited"
