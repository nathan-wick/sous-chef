import asyncio
from google import genai
from google.genai import types

from llm.client import LlmClient


class GeminiClient(LlmClient):

    def __init__(self, api_key: str, model: str, temperature: float, timeout: int):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.client = genai.Client(api_key=api_key)

    async def generate(self, prompt: str) -> str:
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.client.models.generate_content( # type: ignore
                        model=self.model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=self.temperature
                        )
                    )
                ),
                timeout=self.timeout
            )
            
            return response.text or ""
        
        except asyncio.TimeoutError:
            raise Exception(f"Gemini generation timed out after {self.timeout} seconds")
        
        except Exception as error:
            raise Exception(f"Gemini generation failed: {error}")
        
    async def generate_batch(self, prompts: list[str]) -> list[str]:
        loop = asyncio.get_event_loop()
        default_batch_job_name: str = "review-job"

        # TODO Delete logs
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"API key type before batch: {type(self.api_key)}")

        batch_job = await loop.run_in_executor(
            None,
            lambda: self.client.batches.create(
                model=self.model,
                src=[
                    {
                        "contents": [{
                            "parts": [{"text": prompt}],
                            "role": "user"
                        }]
                    }
                    for prompt in prompts
                ],
                # TODO Update configuration to use the user-defined temperature
                config={"display_name": default_batch_job_name},
            )
        )
        job_name = batch_job.name if batch_job.name is not None else default_batch_job_name

        import time
        deadline = time.time() + self.timeout
        status = batch_job.state.name # type: ignore

        # TODO Delete
        logger.info(f"Got past batch: {status}")

        while status not in ("JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED", "JOB_STATE_PARTIALLY_SUCCEEDED"):
            if time.time() > deadline:
                raise Exception("Gemini batch generation timed out after {self.timeout} seconds")
            await asyncio.sleep(1)

            batch_job = await loop.run_in_executor(
                None,
                lambda: self.client.batches.get(name=job_name)
            )
            status = batch_job.state

        if status != "JOB_STATE_SUCCEEDED":
            raise Exception(f"Batch request failed: {status}")

        results: list[str] = []
        for task in batch_job.tasks: # type: ignore
            output_text = ""
            for part in task.response.contents[0].parts: # type: ignore
                if hasattr(part, "text"): # type: ignore
                    output_text += part.text # type: ignore
            results.append(output_text.strip()) # type: ignore

        return results