import asyncio
import logging
import signal
import sys
from typing import Optional
from aiohttp import web
from configuration import load_configuration, Configuration
from llm.claude import ClaudeClient
from llm.gemini import GeminiClient
from llm.ollama import OllamaClient
from platform_adapters.github import GitHubPlatform
from platform_adapters.gitlab import GitLabPlatform
from platform_adapters.models import PullRequestEvent
from reviewer import Reviewer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
class AfcFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        return 'AFC' not in record.getMessage()
logging.getLogger().addFilter(AfcFilter())

class Service:

    def __init__(
            self,
            configuration: Configuration,
            reviewer_instance: Reviewer,
            github_platform: Optional[GitHubPlatform] = None,
            gitlab_platform: Optional[GitLabPlatform] = None):
        self.configuration = configuration
        self.reviewer_instance = reviewer_instance
        self.github_platform = github_platform
        self.gitlab_platform = gitlab_platform

    def detect_platform(self) -> str:
        url = self.configuration.platform.url.lower()
        
        if "github" in url:
            return "github"
        if "gitlab" in url:
            return "gitlab"
        
        token = self.configuration.platform.token
        
        github_prefixes = ("ghp_", "github_pat_", "gho_", "ghu_", "ghs_", "ghr_")
        if token.startswith(github_prefixes):
            return "github"
        
        gitlab_prefixes = ("glpat-", "gloas-", "glgat-", "gldt-", "glagent-")
        if token.startswith(gitlab_prefixes):
            return "gitlab"
        
        return ""

    async def handle_webhook(self, request: web.Request) -> web.Response:
        if request.method != "POST":
            return web.Response(text="Method not allowed", status=405)
        
        event = None

        try:
            if self.github_platform is not None:
                await self.github_platform.validate_webhook(request)
                event = await self.github_platform.parse_pull_request(request)

            if self.gitlab_platform is not None:
                await self.gitlab_platform.validate_webhook(request)
                event = await self.gitlab_platform.parse_merge_request(request)

        except Exception as error:
            logger.error(f"Webhook validation or parsing failed: {error}")
            return web.Response(text="Unauthorized or Bad Request", status=401)

        if event is None:
            return web.Response(text="OK", status=200)

        asyncio.create_task(self.process_review(event))
        return web.Response(text="OK", status=200)

    async def process_review(self, event: PullRequestEvent):
        logger.info(f"Processing review for {event.owner}/{event.repo} #{event.number}")
        
        try:
            review = await self.reviewer_instance.review_pull_request(event)
            
            if self.github_platform is not None:
                await self.github_platform.post_comment(
                    event.owner, event.repo, event.number, review
                )

            if self.gitlab_platform is not None:
                await self.gitlab_platform.post_comment(
                    event.owner, event.number, review
                )
            
            logger.info(f"Review completed for {event.owner}/{event.repo} #{event.number}")
        except Exception as error:
            logger.error(f"Review failed: {error}")

    async def handle_health(self, request: web.Request) -> web.Response:
        return web.Response(text="OK", status=200)


def create_llm_client(configuration: Configuration):
    model_name = configuration.llm.model.lower()
    
    if configuration.llm.api_key:
        if "gemini" in model_name:
            logger.info(f"Using Gemini client for model: {configuration.llm.model}")
            return GeminiClient(
                api_key=configuration.llm.api_key,
                model=configuration.llm.model,
                temperature=configuration.llm.temperature,
                timeout=configuration.llm.timeout
            )
        else:
            logger.info(f"Using Claude client for model: {configuration.llm.model}")
            return ClaudeClient(
                api_key=configuration.llm.api_key,
                model=configuration.llm.model,
                temperature=configuration.llm.temperature,
                timeout=configuration.llm.timeout
            )
    else:
        logger.info(f"Using Ollama client for model: {configuration.llm.model}")
        return OllamaClient(
            host="ollama:11434",
            model=configuration.llm.model,
            temperature=configuration.llm.temperature,
            timeout=configuration.llm.timeout
        )


async def create_application() -> web.Application:
    try:
        configuration = load_configuration()
    except Exception as error:
        logger.fatal(f"Failed to load configuration: {error}")
        sys.exit(1)
    
    llm_client = create_llm_client(configuration)
    
    reviewer_instance = Reviewer(llm_client, configuration)

    service = Service(configuration, reviewer_instance)

    detected_platform = service.detect_platform()
    
    if detected_platform == "github":
        service.github_platform = GitHubPlatform(
            configuration.platform.token,
            configuration.platform.webhook_secret
        )
        reviewer_instance.set_github_platform(service.github_platform)
    else:
        try:
            service.gitlab_platform = GitLabPlatform(
                configuration.platform.token,
                configuration.platform.webhook_secret,
                configuration.platform.url
            )
            reviewer_instance.set_gitlab_platform(service.gitlab_platform)
        except Exception as error:
            logger.fatal(f"Failed to initialize GitLab: {error}")
            sys.exit(1)

    application = web.Application()
    application.router.add_post("/webhook", service.handle_webhook)
    application.router.add_get("/health", service.handle_health)
    
    logger.info(f"Application created with the following configuration: {configuration}")
    return application


def main():
    application = asyncio.run(create_application())
    
    def signal_handler(sig, frame): # type: ignore
        logger.info("Shutting down server...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler) # type: ignore
    signal.signal(signal.SIGTERM, signal_handler) # type: ignore

    logger.info("Starting server on 0.0.0.0:8080")
    web.run_app(application, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()