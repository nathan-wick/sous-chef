import asyncio
import time
from anthropic import AsyncAnthropic
from llm.client import LlmClient


class ClaudeClient(LlmClient):
    def __init__(self, api_key: str, model: str, temperature: float, timeout: int):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.client = AsyncAnthropic(api_key=api_key)
    
    async def generate(self, prompt: str) -> str:
        try:
            response = await asyncio.wait_for(
                self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=self.temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                ),
                timeout=self.timeout
            )
            
            text_content = []
            for block in response.content:
                if block.type == "text":
                    text_content.append(block.text) # type: ignore
            
            return "\n".join(text_content) # type: ignore
        
        except asyncio.TimeoutError:
            raise Exception(f"Claude generation timed out after {self.timeout} seconds")
        
        except Exception as error:
            raise Exception(f"Claude generation failed: {error}")
    
    async def generate_batch(self, prompts: list[str]) -> list[str]:
        try:
            batch_job = await asyncio.wait_for( # type: ignore
                self.client.batches.create( # type: ignore
                    requests=[
                        {
                            "custom_id": str(index),
                            "params": {
                                "model": self.model,
                                "max_tokens": 4096,
                                "temperature": self.temperature,
                                "messages": [
                                    {
                                        "role": "user",
                                        "content": prompt
                                    }
                                ]
                            }
                        }
                        for index, prompt in enumerate(prompts)
                    ]
                ),
                timeout=self.timeout
            )
            
            deadline = time.time() + self.timeout
            while batch_job.processing_status != "ended": # type: ignore
                if time.time() > deadline:
                    raise Exception(f"Claude batch generation timed out after {self.timeout} seconds")
                
                await asyncio.sleep(1)
                batch_job = await self.client.batches.retrieve(batch_job.id) # type: ignore
            
            if batch_job.results_url is None: # type: ignore
                raise Exception(f"Batch request failed: no results available")
            
            results_response = await self.client.batches.results(batch_job.id) # type: ignore
            
            results_dict = {}
            async for result in results_response: # type: ignore
                if result.result.type == "succeeded": # type: ignore
                    text_content = []
                    for block in result.result.message.content: # type: ignore
                        if block.type == "text": # type: ignore
                            text_content.append(block.text) # type: ignore
                    results_dict[int(result.custom_id)] = "\n".join(text_content) # type: ignore
                else:
                    results_dict[int(result.custom_id)] = "" # type: ignore
            
            return [results_dict[index] for index in range(len(prompts))]
        
        except asyncio.TimeoutError:
            raise Exception(f"Claude batch generation timed out after {self.timeout} seconds")
        
        except Exception as error:
            raise Exception(f"Claude batch generation failed: {error}")