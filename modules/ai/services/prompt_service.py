from ..prompts import SYSTEM_PROMPT


class PromptService:

    def build(self, conversation):

        return [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": conversation
            }
        ]