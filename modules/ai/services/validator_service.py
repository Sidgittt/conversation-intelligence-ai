class ValidatorService:

    REQUIRED_FIELDS = [
        "summary",
        "primary_emotion",
        "secondary_emotion",
        "topics",
        "toxicity",
        "relationship_stage",
        "confidence"
    ]

    def validate(self, data):

        for field in self.REQUIRED_FIELDS:

            if field not in data:
                raise ValueError(f"Missing field: {field}")

        return data