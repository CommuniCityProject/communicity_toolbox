from enum import Enum, unique


@unique
class Emotion(Enum):
    ANGER = "ANGER"
    DISGUST = "DISGUST"
    FEAR = "FEAR"
    HAPPINESS = "HAPPINESS"
    NEUTRAL = "NEUTRAL"
    SADNESS = "SADNESS"
    SURPRISE = "SURPRISE"

    def __str__(self):
        return self.name
