from .providers.openai_provider import OpenAIProvider
from .providers.ollama_provider import OllamaProvider


class LLM:

    def __init__(self, provider="openai"):

        if provider == "openai":
            self.provider = OpenAIProvider()

        elif provider == "ollama":
            self.provider = OllamaProvider()

        else:
            raise ValueError("Unsupported AI provider.")

    def analyze(self, system_prompt, user_prompt):

        return self.provider.chat(
            system_prompt,
            user_prompt
        )