from __future__ import annotations

import datetime
import pathlib
import re

import requests
from pydantic import ValidationError

from ..logger import log
from .models.github_api import GitHubResponse, GithubSpecificTagInfo, GithubTagResponse


def get_rustc_commit(target: pathlib.Path) -> str | None:
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


def _get_version_from_comment(target: pathlib.Path) -> str | None:
    with pathlib.Path(target).open("rb") as f:
        data = f.read()
    # .comment section:
    # rustc version 1.85.0-nightly
    # rustc version 1.83.0
    res = re.search(b"rustc version ([a-zA-Z0-9._-]+)", data)

    if res is None:
        return None

    return res.group(1).decode()


def _get_version_from_commit(commit: str) -> str:
    url = f"https://api.github.com/search/issues?q={commit}+repo:rust-lang/rust"
    try:
        res = GitHubResponse.model_validate(requests.get(url, timeout=20).json())
        if res.items and res.items[0].milestone and res.items[0].milestone.title:
            milestone_title = res.items[0].milestone.title
            return str(milestone_title)

    except ValidationError:
        log.exception("Validation error while processing GitHub response")
        raise

    return None

# rustup +1.70.0-x86_64-unknown-linux-musl component add rust-src rustc-dev llvm-tools-preview --target x86_64-unknown-linux-musl
def _get_latest_rustc_version() -> str | None:
    url = "https://github.com/rust-lang/rust/tags"
    res = requests.get(url, timeout=20).text
    regex = re.compile(r"/rust-lang/rust/releases/tag/([0-9\.]+)")
    return regex.findall(res)[0]

def get_rustc_version_date(rustc_version: str) -> str | None:
    URI = "https://api.github.com/repos/rust-lang/rust/tags?per_page=100"
    tags = GithubTagResponse.model_validate(requests.get(URI, timeout=20).json()).root
    for tag in tags:
        if tag.name == rustc_version:
            response = GithubSpecificTagInfo.model_validate(requests.get(tag.commit.url, timeout=20).json())
            return datetime.datetime.fromisoformat(response.commit.committer.date).strftime("%Y-%m-%d")

    return None

def get_rustc_version(target: pathlib.Path) -> tuple[str | None, str | None]:
    """Get rustc version used in target executable.

    Args:
        target (pathlib.Path): file path.

    Returns:
        Tuple[str, str]: Returns Tuple(commit, version). If search failed, returns Tuple(None, None) instead.

    """
    commit = get_rustc_commit(target)

    version = _get_version_from_comment(target)

    if commit is None and version is None:
        return (None, None)

    # version is not None, no need to continue and look it up via GitHub
    if version:
        log.debug(f"Found version {version} as a hardcoded string")
        return (commit, version)

    if commit is None:
        return (None, None)

    log.debug("Found commit %s", commit)
    version = _get_version_from_commit(commit)
    if version is None:
        return None

    log.debug("Found tag/milestone %s", version)
    return (commit, version)
