from dataclasses import dataclass


@dataclass
class AIResult:

    summary: str

    primary_emotion: str

    secondary_emotion: str

    topics: list

    toxicity: str

    relationship_stage: str

    confidence: float