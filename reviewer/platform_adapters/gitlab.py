"""GitLab platform adapter for webhook handling and API interactions."""

import hmac
import json
from typing import Optional

from aiohttp import web
import gitlab

from platform_adapters.models import PullRequestEvent, FileChange


class GitLabPlatform:
    """Handles GitLab webhook validation and API interactions."""

    def __init__(self, token: str, webhook_secret: str, url: str):
        self.client = gitlab.Gitlab(url, private_token=token) # type: ignore
        self.webhook_secret = webhook_secret

    async def validate_webhook(self, request: web.Request) -> None:
        """Validate the GitLab webhook token."""
        token = request.headers.get("X-Gitlab-Token")
        if not token:
            raise ValueError("Missing token header")

        if not hmac.compare_digest(token, self.webhook_secret):
            raise ValueError("Invalid token")

    async def parse_merge_request(
        self, request: web.Request
    ) -> Optional[PullRequestEvent]:
        body = await request.read()
        event = json.loads(body)

        object_attributes = event.get("object_attributes", {})
        action = object_attributes.get("action")
        
        if action not in ("open", "update"):
            return None

        project = event.get("project", {})
        project_id = project.get("id")
        merge_request_iid = object_attributes.get("iid")
        path_with_namespace = project.get("path_with_namespace")

        project_object = self.client.projects.get(project_id) # type: ignore
        merge_request = project_object.mergerequests.get(merge_request_iid) # type: ignore
        changes = merge_request.changes() # type: ignore

        file_changes = []
        for change in changes.get("changes", []): # type: ignore
            file_changes.append(FileChange( # type: ignore
                filename=change.get("new_path", ""), # type: ignore
                patch=change.get("diff", ""), # type: ignore
                status="modified"
            ))

        return PullRequestEvent(
            owner=str(project_id),
            repo=path_with_namespace,
            number=merge_request_iid,
            files=file_changes # type: ignore
        )

    async def post_comment(
        self, project_id: str, merge_request_iid: int, comment: str
    ) -> None:
        project = self.client.projects.get(project_id) # type: ignore
        merge_request = project.mergerequests.get(merge_request_iid) # type: ignore
        merge_request.notes.create({"body": comment}) # type: ignore