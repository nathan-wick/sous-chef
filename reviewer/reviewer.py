import logging

from configuration import Configuration
from llm.client import LlmClient
from platform_adapters.github import GitHubPlatform
from platform_adapters.gitlab import GitLabPlatform
from platform_adapters.models import PullRequestEvent, FileChange

logger = logging.getLogger(__name__)


class Reviewer:

    def __init__(self, llm_client: LlmClient, configuration: Configuration):
        self.llm_client = llm_client
        self.configuration = configuration
        self.github_platform = None
        self.gitlab_platform = None

    def set_github_platform(self, platform: GitHubPlatform):
        self.github_platform = platform

    def set_gitlab_platform(self, platform: GitLabPlatform):
        self.gitlab_platform = platform

    async def post_comment(self, event: PullRequestEvent, message: str) -> None:
        try:
            if self.github_platform is not None:
                await self.github_platform.post_comment(
                    event.owner, event.repo, event.number, message
                )
            elif self.gitlab_platform is not None:
                await self.gitlab_platform.post_comment(
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

        file_prompts: list[str] = []
        file_list: list[FileChange] = []

        file_count = 0

        for file in event.files:
            if file_count >= self.configuration.review.maximum_files:
                reviews.append(
                    f"🛑 Too many files to review. Only reviewed the first "
                    f"{self.configuration.review.maximum_files} files."
                )
                break

            if file.status == "removed":
                continue

            if self.is_file_blocked(file.filename):
                reviews.append(
                    f"### ⏭️ 📄 {file.filename}\n\n"
                    f"Skipped review."
                )
                continue
            
            if len(file.patch) > self.configuration.review.maximum_file_size_characters:
                reviews.append(
                    f"### 🐘 📄 {file.filename}\n\n"
                    f"File changes are too large to review."
                )
                continue

            prompt: str = (
                f"{self.configuration.review.review_prompt}\n\n"
                f"File Name: {file.filename}\n\n"
                f"Changes:\n```\n{file.patch}\n```"
            )

            file_prompts.append(prompt)
            file_list.append(file)
            file_count += 1

        if not file_prompts:
            reviews.append("No changes to review.")

        logger.info(f"Sending #{len(file_prompts)} prompts to the LLM for review #{event.number}")

        llm_responses = await self.llm_client.generate_batch(file_prompts)

        for file, response in zip(file_list, llm_responses):
            if not response or "no issues" in response.lower():
                reviews.append(f"### ✅ 📄 {file.filename}\n\nNo issues detected.")
            else:
                reviews.append(f"### ⚠️ 📄 {file.filename}\n\n{response}")

        logger.info(f"Review #{event.number} is complete")

        return "\n\n---\n\n".join(reviews)