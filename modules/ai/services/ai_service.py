from ..pipeline import AIPipeline


class AIService:

    def __init__(self):

        self.pipeline = AIPipeline()

    def analyze(self, conversation):

        return self.pipeline.analyze(conversation)