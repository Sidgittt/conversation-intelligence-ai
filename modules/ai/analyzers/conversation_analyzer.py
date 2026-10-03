from ..services.ai_service import AIService


class ConversationAnalyzer:

    def __init__(self):
        self.ai = AIService()

    def analyze(self, conversation):
        return self.ai.analyze(conversation)