from dataclasses import dataclass
from typing import List


@dataclass
class FileChange:
    filename: str
    patch: str
    status: str


@dataclass
class PullRequestEvent:
    owner: str
    repo: str
    number: int
    files: List[FileChange]