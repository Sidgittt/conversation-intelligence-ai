class PromptBuilder:

    def build(self, conversation):

        prompt = f"""
You are an expert relationship psychologist and communication analyst.

You understand:

- English
- Hindi
- Marathi
- Mixed-language conversations
- Emojis
- Slang
- Internet abbreviations

Analyse the ENTIRE conversation.

Do NOT analyse each message independently.

Understand the context.

Conversation:

{conversation}

Return ONLY valid JSON.
"""

        return prompt