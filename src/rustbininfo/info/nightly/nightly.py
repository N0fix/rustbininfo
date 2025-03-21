import datetime

import requests

from rustbininfo.info.models.github_api import GithubSpecificTagInfo, GithubTagResponse


class NightlyGetter:
    def get_nightly_toolchain_for_rustc_version(self, rustc_version) -> str | None:
        URI = "https://api.github.com/repos/rust-lang/rust/tags?per_page=100"
        tags = GithubTagResponse.model_validate(requests.get(URI, timeout=20).json()).root
        for tag in tags:
            if tag.name == rustc_version:
                response = GithubSpecificTagInfo.model_validate(requests.get(tag.commit.url, timeout=20).json())
                return datetime.datetime.fromisoformat(response.commit.committer.date).strftime("%Y-%m-%d")

        return None
