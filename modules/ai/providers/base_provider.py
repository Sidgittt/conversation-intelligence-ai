from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str):
        pass