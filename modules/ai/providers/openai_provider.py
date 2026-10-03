from .base_provider import BaseProvider


class OpenAIProvider(BaseProvider):

    def __init__(self):
        pass

    def chat(self, system_prompt, user_prompt):
        raise NotImplementedError("OpenAI integration coming next.")