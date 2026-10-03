import json

from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()


class LLMConversationAgent:

    def __init__(self):
        self.client = OpenAI()

    def ask(self, question, evidence):
        if not evidence:
            return "No relevant conversation evidence was found."

        context = json.dumps(
            evidence,
            ensure_ascii=False,
            default=str,
            indent=2,
        )

        prompt = f"""
You are an AI Conversation Intelligence Assistant.

Answer the user's question using ONLY the supplied conversation evidence.

The evidence can contain structured AI analysis and signals that matching
raw messages exist. It can also contain dates from multiple conversations.

For questions about change, trends, progression, earlier/later periods,
or the history of the conversation, compare the available timeline.

Rules:
1. Never invent facts, events, emotions, intentions or relationship changes.
2. Missing or null scores mean unavailable evidence, not zero.
3. Clearly state when evidence is insufficient.
4. Separate observed evidence from interpretation.
5. For longitudinal questions, compare earlier and later supported evidence.
6. Mention Conversation IDs and dates when useful.
7. A raw-message retrieval signal confirms matching messages existed, but
   the exact message text is unavailable unless explicitly supplied.
8. Do not assume one conversation represents the entire relationship.
9. If the retrieved evidence covers only a limited period, say so.
10. Keep the answer concise but meaningful.

Conversation Evidence:

{context}

User Question:

{question}
"""

        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You answer questions about analyzed conversations "
                        "using only supplied evidence."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            return "The AI did not return an answer."

        return content.strip()
