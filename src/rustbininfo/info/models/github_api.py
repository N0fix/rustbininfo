from __future__ import annotations

from pydantic import BaseModel


class Milestone(BaseModel):
    title: str | None


class GitHubIssue(BaseModel):
    milestone: Milestone | None


class GitHubResponse(BaseModel):
    items: list[GitHubIssue]
