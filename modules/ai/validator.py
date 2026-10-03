class Validator:

    REQUIRED_FIELDS = [

        "summary",

        "primary_emotion",

        "secondary_emotion",

        "topics",

        "toxicity",

        "relationship_stage",

        "confidence"

    ]

    def validate(self, result):

        for field in self.REQUIRED_FIELDS:

            if field not in result:

                raise ValueError(f"{field} missing.")

        return result