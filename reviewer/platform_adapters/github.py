import hashlib
import hmac
import json
from typing import Optional

from aiohttp import web
from github import Github

from platform_adapters.models import PullRequestEvent, FileChange


class GitHubPlatform:

    def __init__(self, token: str, webhook_secret: str):
        self.client = Github(token)
        self.webhook_secret = webhook_secret

    async def validate_webhook(self, request: web.Request) -> None:
        signature = request.headers.get("X-Hub-Signature-256")
        if not signature:
            raise ValueError("Missing signature header")

        body = await request.read()
        
        expected_signature = "sha256=" + hmac.new(
            self.webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("Invalid signature")

    async def parse_pull_request(
        self, request: web.Request
    ) -> Optional[PullRequestEvent]:
        body = await request.read()
        payload = json.loads(body)

        action = payload.get("action")
        if action not in ("opened", "synchronize"):
            return None

        pull_request = payload.get("pull_request", {})
        repository = payload.get("repository", {})
        owner = repository.get("owner", {}).get("login")
        repo_name = repository.get("name")
        pull_request_number = pull_request.get("number")

        repository_object = self.client.get_repo(f"{owner}/{repo_name}")
        pull_request_object = repository_object.get_pull(pull_request_number)
        files = pull_request_object.get_files()

        file_changes = []
        for file in files:
            file_changes.append(FileChange( # type: ignore
                filename=file.filename,
                patch=file.patch or "",
                status=file.status
            ))

        return PullRequestEvent(
            owner=owner,
            repo=repo_name,
            number=pull_request_number,
            files=file_changes # type: ignore
        )

    async def post_comment(
        self, owner: str, repo: str, number: int, comment: str
    ) -> None:
        repository = self.client.get_repo(f"{owner}/{repo}")
        issue = repository.get_issue(number)
        issue.create_comment(comment)