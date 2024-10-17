import pathlib
import re
from typing import Optional, Tuple

import requests
from pydantic import ValidationError

from ..logger import log
from .models.github_api import GitHubResponse


def get_rustc_commit(target: pathlib.Path) -> Optional[str]:
    data = open(target, "rb").read()
    res = re.search(b"rustc/([a-z0-9]{40})", data)

    if res is None:
        return None

    return res.group(0)[len("rustc/") :].decode()


def _get_version_from_commit(commit: str):
    url = f"https://github.com/rust-lang/rust/branch_commits/{commit}"
    res = requests.get(url, timeout=20).text
    regex = re.compile(r'href="/rust-lang/rust/releases/tag/([0-9\.]+)"')

    if not regex.findall(res):
        return None

    return regex.findall(res)[-1]


def _get_latest_rustc_version():
    url = "https://github.com/rust-lang/rust/tags"
    res = requests.get(url, timeout=20).text
    regex = re.compile(r"/rust-lang/rust/releases/tag/([0-9\.]+)")
    return regex.findall(res)[0]


def _get_nightly_version_from_commit(commit: str) -> Optional[str]:
    url = f"https://api.github.com/search/issues?q={commit}+repo:rust-lang/rust"
    try:
        res = GitHubResponse.model_validate((requests.get(url, timeout=20).json()))
    except ValidationError as e:
        log.error(f"Validation error while processing GitHub response: {e}")
        return None

    if res.items and res.items[0].milestone and res.items[0].milestone.title:
        milestone_title = res.items[0].milestone.title
        return f"{milestone_title}-nightly"
    
    return None


def get_rustc_version(target: pathlib.Path) -> Tuple[Optional[str], Optional[str]]:
    """Get rustc version used in target executable.

    Args:
        target (pathlib.Path)

    Returns:
        Tuple[str, str]: Returns Tuple(commit, version). If search failed, returns Tuple(None, None) instead.
    """
    commit = get_rustc_commit(target)
    if commit is None:
        return (None, None)

    log.debug(f"Found commit {commit}")
    version = _get_version_from_commit(commit)
    if version is None:
        log.debug("No tag matching this commit, getting milestone version")
        version = _get_nightly_version_from_commit(commit)
        if version is None:
            log.debug("No milestone matching this commit, getting latest version")
            return (commit, _get_latest_rustc_version())

    log.debug(f"Found tag/milestone {version}")
    return (commit, version)
