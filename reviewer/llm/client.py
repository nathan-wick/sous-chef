import asyncio
from abc import ABC, abstractmethod


class LlmClient(ABC):

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

    async def generate_batch(self, prompts: list[str]) -> list[str]:
        return await asyncio.gather(*[self.generate(prompt) for prompt in prompts])