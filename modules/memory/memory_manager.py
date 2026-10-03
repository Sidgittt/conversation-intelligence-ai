import pandas as pd
from pathlib import Path


class MemoryManager:

    def __init__(self):

        self.file = Path("output") / "relationship_memory.csv"

    def load(self):

        if self.file.exists():

            return pd.read_csv(self.file)

        return pd.DataFrame()

    def save_memory(self, conversation_id, result):

        memory = self.load()

        row = {

            "Conversation_ID": conversation_id,

            "Trust": result.get(
                "relationship",
                {}
            ).get(
                "trust_score",
                0
            ),

            "Communication": result.get(
                "relationship",
                {}
            ).get(
                "communication_score",
                0
            ),

            "Romance": result.get(
                "relationship",
                {}
            ).get(
                "romance_score",
                0
            ),

            "Primary_Emotion":
                result.get(
                    "primary_emotion",
                    ""
                ),

            "Conversation_Type":
                result.get(
                    "conversation_type",
                    ""
                )

        }

        memory = pd.concat(
            [
                memory,
                pd.DataFrame([row])
            ],
            ignore_index=True
        )

        memory.to_csv(
            self.file,
            index=False
        )