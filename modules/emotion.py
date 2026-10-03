from dataclasses import dataclass


@dataclass
class EmotionResult:
    emotion: str
    confidence: float


class EmotionAnalyzer:

    def __init__(self):
        pass

    def predict(self, message: str) -> EmotionResult:

        return EmotionResult(
            emotion="Unknown",
            confidence=0.0
        )