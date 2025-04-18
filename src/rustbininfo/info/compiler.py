from __future__ import annotations

import datetime
import pathlib
import re

import requests
from pydantic import ValidationError

from ..logger import log
from .models.github_api import GitHubResponse, GithubSpecificTagInfo, GithubTagResponse


class CompilerInfo:
    def __init__(self, repo_path: pathlib.Path | None = None):
        if repo_path:
            from .rust_repo_handler import GitRepoProvider

            self.provider = GitRepoProvider(repo_path)

        else:
            self.provider = BasicProvider()

    def get_rustc_commit(self, target: pathlib.Path) -> str | None:
        commit = self.provider.get_rustc_commit(target)

        if commit is None:
            commit = self.provider.guess_commit_from_dates(target)

        return commit


class BasicProvider:
    def get_rustc_commit(self, target: pathlib.Path) -> str | None:
        """Find and returns rustc commit of a given rust executable file.

        Args:
            target (pathlib.Path): path to the target.

        Returns:
            str | None: None if no rustc commit could be found.

        """
        with pathlib.Path(target).open("rb") as f:
            data = f.read()
            res = re.search(b"rustc/([a-z0-9]{40})", data)

            if res is None:
                return None

            return res.group(1).decode()

    def get_version_from_comment(self, target: pathlib.Path) -> str | None:
        with pathlib.Path(target).open("rb") as f:
            data = f.read()
        # .comment section:
        # rustc version 1.85.0-nightly
        # rustc version 1.83.0
        res = re.search(b"rustc version ([a-zA-Z0-9._-]+)", data)

        if res is None:
            return None

        return res.group(1).decode()

    def rustc_version_from_commit(self, commit: str) -> str:
        url = f"https://api.github.com/search/issues?q={commit}+repo:rust-lang/rust"
        try:
            res = GitHubResponse.model_validate(requests.get(url, timeout=20).json())
            if res.items and res.items[0].milestone and res.items[0].milestone.title:
                milestone_title = res.items[0].milestone.title
                return str(milestone_title)

        except ValidationError:
            log.exception("Validation error while processing GitHub response")
            raise

        return self.get_commit_date(commit)

    def get_latest_rustc_version(self) -> str | None:
        url = "https://github.com/rust-lang/rust/tags"
        res = requests.get(url, timeout=20).text
        regex = re.compile(r"/rust-lang/rust/releases/tag/([0-9\.]+)")
        return regex.findall(res)[0]

    def get_rustc_version_date(self, rustc_version: str) -> str | None:
        URI = "https://api.github.com/repos/rust-lang/rust/tags?per_page=100"
        tags = GithubTagResponse.model_validate(requests.get(URI, timeout=20).json()).root
        for tag in tags:
            if tag.name == rustc_version:
                response = GithubSpecificTagInfo.model_validate(requests.get(tag.commit.url, timeout=20).json())
                return datetime.datetime.fromisoformat(response.commit.committer.date).strftime("%Y-%m-%d")

        return None

    def get_commit_date(self, commit: str) -> str:
        URI = "https://api.github.com/repos/rust-lang/rust/commits"
        response = GithubSpecificTagInfo.model_validate(
            requests.get(URI, params={"sha": commit, "per_page": "1"}).json()[0]
        )
        return datetime.datetime.fromisoformat(response.commit.committer.date).strftime("%Y-%m-%d")

    def guess_commit_from_dates(self, target: pathlib.Path):
        URI = "https://api.github.com/repos/rust-lang/rust/commits"
        from rustbininfo.info.dependencies import get_dependencies
        from rustbininfo.utils import get_min_max_update_time

        t = get_dependencies(target, fast_load=True)
        date_min, date_max = get_min_max_update_time(t)
        if date_min.timestamp() <= 10_000:
            return None

        tags = requests.get(
            URI, params={"since": date_min.isoformat(), "until": date_max.isoformat()}, timeout=20
        ).json()
        return tags[0]["sha"]

    def get_rustc_version(self, target: pathlib.Path) -> tuple[str | None, str | None]:
        """Get rustc version used in target executable.

        Args:
            target (pathlib.Path): file path.

        Returns:
            Tuple[str, str]: Returns Tuple(commit, version). If search failed, returns Tuple(None, None) instead.

        """
        commit = self.get_rustc_commit(target)

        version = self.get_version_from_comment(target)

        if commit is None:
            commit = self.guess_commit_from_dates(target)

        if commit is None and version is None:
            return (None, None)

        # version is not None, no need to continue and look it up via GitHub
        if version:
            log.debug(f"Found version {version} as a hardcoded string")
            return (commit, version)

        if commit is None:
            return (None, None)

        log.debug("Found commit %s", commit)
        version = self.rustc_version_from_commit(commit)
        if version is None:
            return (None, None)

        log.debug("Found tag/milestone %s", version)
        return (commit, version)
