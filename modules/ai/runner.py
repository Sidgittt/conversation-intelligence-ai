import json
from pathlib import Path

from .analyzers.conversation_analyzer import ConversationAnalyzer


class AIRunner:

    def __init__(self):

        self.analyzer = ConversationAnalyzer()

        self.output_folder = Path("output/ai_reports")

        self.output_folder.mkdir(exist_ok=True)

    def analyze(self, conversation_id, conversation_text):

        output_file = (
            self.output_folder /
            f"conversation_{conversation_id}.json"
        )

        if output_file.exists():

            print(f"✓ Conversation {conversation_id} already analyzed.")

            return

        print(f"Analyzing Conversation {conversation_id}...")

        result = self.analyzer.analyze(conversation_text)

        with open(output_file, "w", encoding="utf-8") as f:

            json.dump(
                result,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(f"Saved -> {output_file}")