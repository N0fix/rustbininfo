import datetime
import pathlib
import sys

from ..cache import cache
from ..logger import log
from .compiler import BasicProvider

try:
    import git

except ImportError:
    print(
        "`git` was not found, have you installed the 'gitpython' extra ? (pip install rustbininfo[gitpython])",
        file=sys.stderr,
    )
    sys.exit(1)


class GitRepoProvider(BasicProvider):
    def __init__(self, repo_path: pathlib.Path, update: bool = False):
        self.repo = git.Repo(repo_path)
        if update:
            self._ensure_repo_is_up_to_date()

    def _ensure_repo_is_up_to_date(self):
        try:
            o = self.repo.remotes.origin
            o.pull()

        except:
            log.warning("Could not pull latest change, results might be innacurate.")

    def rustc_version_from_commit(self, commit: str) -> str | None:
        if tag := self.repo.git.tag("--contains", commit):
            multiple_tags = "\n" in tag
            if multiple_tags:
                return tag.splitlines()[0]

            return tag

        return f"nightly-{self.get_commit_date(commit)}"

    def guess_commit_from_dates(self, target: pathlib.Path) -> str | None:
        from rustbininfo.info.dependencies import get_dependencies
        from rustbininfo.utils import get_min_max_update_time

        t = get_dependencies(target, fast_load=True)
        date_min, date_max = get_min_max_update_time(t)
        if date_min.timestamp() <= 10_000:
            return None

        return self.repo.git.log(
            f'--since="{date_min.isoformat()}',
            f"--until={date_max.isoformat()}",
            "-1",
            "--oneline",
            "--format=%H",
        )

    def get_latest_rustc_version(self) -> str:
        return sorted(self.repo.tags, key=lambda t: t.commit.committed_datetime)[-1].name

    def get_rustc_version_date(self, rustc_version: str) -> str | None:
        for tag in self.repo.tags:
            if tag.name == rustc_version:
                return datetime.datetime.fromisoformat(tag.commit.committed_datetime).strftime("%Y-%m-%d")

        return None

    def get_commit_date(self, commit: str):
        return self.repo.git.log("-1", "--no-patch", "--format=%cs", commit)
