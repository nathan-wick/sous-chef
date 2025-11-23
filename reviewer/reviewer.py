import asyncio
import logging

from configuration import Configuration
from llm.client import LlmClient
from platform_adapters.models import PullRequestEvent, FileChange

logger = logging.getLogger(__name__)


class Reviewer:

    def __init__(self, llm_client: LlmClient, configuration: Configuration):
        self.llm_client = llm_client
        self.configuration = configuration
        self.github_platform = None
        self.gitlab_platform = None

    def set_github_platform(self, platform): # type: ignore
        self.github_platform = platform # type: ignore

    def set_gitlab_platform(self, platform): # type: ignore
        self.gitlab_platform = platform # type: ignore

    async def post_comment(self, event: PullRequestEvent, message: str) -> None:
        try:
            if self.github_platform is not None: # type: ignore
                await self.github_platform.post_comment( # type: ignore
                    event.owner, event.repo, event.number, message
                )
            elif self.gitlab_platform is not None: # type: ignore
                await self.gitlab_platform.post_comment( # type: ignore
                    event.owner, event.number, message
                )
        except Exception as error:
            logger.error(f"Failed to post comment: {error}")

    def is_file_blocked(self, filename: str) -> bool:
        if not self.configuration.review.blocked_file_path_keywords:
            return False
        
        filename_lower = filename.lower()
        for keyword in self.configuration.review.blocked_file_path_keywords:
            if keyword.lower() in filename_lower:
                return True
        
        return False

    async def review_file(self, file: FileChange) -> str:
        prompt = (
            f"{self.configuration.review.review_prompt}\n\n"
            f"File: {file.filename}\n\n"
            f"Changes:\n```\n{file.patch}\n```"
        )
        
        response = await self.llm_client.generate(prompt)
        return response.strip()
    
    def is_rate_limit_error(self, error: Exception) -> bool:
        return "429" in str(error)
    
    async def review_file_with_retry(self, file: FileChange, reviewNumber: int, maximumRetries: int, currentRetry: int = 0) -> str:
        try:
            return await self.review_file(file)
        except Exception as error:
            if self.is_rate_limit_error(error) and currentRetry < maximumRetries:
                logger.warning(f"Rate limit hit for review #{reviewNumber}, retrying in 30 seconds...")
                await asyncio.sleep(30)
                currentRetry += 1
                return await self.review_file_with_retry(file, reviewNumber, maximumRetries, currentRetry)
            raise

    async def review_pull_request(self, event: PullRequestEvent) -> str:
        greeting_message = (
            "🤖 Hello! I'm reviewing your changes now. This may take a moment..."
        )
        await self.post_comment(event, greeting_message)

        reviews = [
            "# 🤖 Automated Review\n\n"
            "Please note that while I strive for accuracy, it's important to "
            "**verify all recommendations before implementing them**. This review "
            "is not meant to replace human review, but to accelerate it by "
            "catching common issues early."
        ]

        file_count = 0
        maximum_files = self.configuration.review.maximum_files

        for file in event.files:
            if file_count >= maximum_files:
                reviews.append(
                    f"🛑 Too many files to review. Only reviewed the first "
                    f"{maximum_files} files."
                )
                logger.info(f"Maximum file review limit reached for review #{event.number}")
                break

            if self.is_file_blocked(file.filename):
                reviews.append(
                    f"### ⏭️ 📄 {file.filename}\n\n"
                    f"Skipped review."
                )
                logger.info(f"Skipped reviewing {file.filename} for review #{event.number} because the file's name had a blocked keyword")
                continue

            patch_size = len(file.patch)
            maximum_size = self.configuration.review.maximum_file_size_characters
            
            if patch_size > maximum_size:
                reviews.append(
                    f"### 🐘 📄 {file.filename}\n\n"
                    f"File changes are too large to review."
                )
                logger.info(f"Skipped reviewing {file.filename} for review #{event.number} because the file's changes are too large")
                continue

            if file.status == "removed":
                logger.info(f"Skipped reviewing {file.filename} for review #{event.number} because the file was removed")
                continue

            try:
                review = await self.review_file_with_retry(file, event.number, 3)
                
                if not review or "no issues" in review.lower():
                    reviews.append(f"### ✅ 📄 {file.filename}\n\nNo issues detected.")
                else:
                    reviews.append(f"### ⚠️ 📄 {file.filename}\n\n{review}")
                
                file_count += 1

                logger.info(f"Finished reviewing {file.filename} for review #{event.number}")
            except Exception as error:
                reviews.append(
                    f"### 🌋 📄 {file.filename}\n\n"
                    f"Error reviewing: {error}"
                )
                logger.error(f"Errored while reviewing {file.filename} for review #{event.number}: {error}")

        if len(reviews) <= 1:
            reviews.append("No changes to review.")

        logger.info(f"Review #{event.number} is complete")

        return "\n\n---\n\n".join(reviews)