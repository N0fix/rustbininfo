from __future__ import annotations

from pydantic import BaseModel, RootModel


class Milestone(BaseModel):
    title: str | None


class GitHubIssue(BaseModel):
    milestone: Milestone | None


class GitHubResponse(BaseModel):
    items: list[GitHubIssue]


class GithubTagsCommitter(BaseModel):
    date: str


class GithubSpecificTagCommit(BaseModel):
    committer: GithubTagsCommitter


class GithubSpecificTagInfo(BaseModel):
    commit: GithubSpecificTagCommit


class GithubTagsCommit(BaseModel):
    url: str


class GithubTags(BaseModel):
    name: str
    commit: GithubTagsCommit


class GithubTagResponse(RootModel[list[GithubTags]]):
    pass
