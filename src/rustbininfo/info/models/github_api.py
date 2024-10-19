from typing import List, Optional
from pydantic import BaseModel


class Milestone(BaseModel):
    title: Optional[str]


class GitHubIssue(BaseModel):
    milestone: Optional[Milestone]


class GitHubResponse(BaseModel):
    items: List[GitHubIssue]
