from enum import unique, Enum


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
