from __future__ import annotations

import json
import pathlib
from pathlib import Path

import requests
import semver
from pydantic import BaseModel, Field

from ...exception import InvalidVersionError
from ...logger import log
from ...utils import get_writable_dir_in_tmp


def _urljoin(base: str, *parts: str) -> str:
    for part in filter(None, parts):
        base = "{}/{}".format(base.rstrip("/"), part.lstrip("/"))
    return base


class ReducedRepresentation:
    def __repr_args__(self: BaseModel) -> "ReprArgs":
        # Disable repr of field if "repr" attribute is not False and value isn't evaluated to False
        return [
            (key, value)
            for key, value in self.__dict__.items()
            if self.model_fields.get(key) and not self.model_fields[key].repr == False and value
        ]


class Crate(ReducedRepresentation, BaseModel):
    name: str
    version: str
    features: list[str] = Field(default=[])
    repository: str | None = Field(default=None)
    fast_load: bool | None = Field(init=True, repr=False)
    _available_versions: list[str] = []
    _api_base_url: str = "https://crates.io/"
    _version_info: dict = None

    @classmethod
    def from_depstring(cls, dep_str: str, fast_load=True) -> Crate:
        try:
            name, version = dep_str.rsplit("-", 1)

            obj = cls(
                name=name,
                version=str(semver.Version.parse(version)),
                fast_load=fast_load,
            )

        except:  # noqa E722
            # e.g: crate-name-0.1.0-pre.2
            name, version, patch = dep_str.rsplit("-", 2)
            version += f"-{patch}"
            obj = cls(
                name=name,
                version=str(semver.Version.parse(version)),
                fast_load=fast_load,
            )

        obj._fast_load = fast_load
        return obj

    def model_post_init(self, __context) -> None:
        if not self.fast_load:
            _ = self.metadata  # triggers getter

    @property
    def metadata(self):
        if getattr(self, "_metadata", None) is None:
            self._metadata = self._get_metadata()

        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    def _get_metadata(self) -> dict:
        log.debug("Downloading metadata for %s", self.name)
        uri = _urljoin(self._api_base_url, *["api", "v1", "crates", self.name])
        headers = {"User-Agent": "rustbinsign (https://github.com/N0fix/rustbinsign)"}
        res = requests.get(uri, timeout=20, headers=headers)
        result = json.loads(res.text)
        # self._metadata = result
        for version in result["versions"]:
            self._available_versions.append(version["num"])
            if version["num"] == self.version:
                self._version_info = version
                for feature in version["features"]:
                    self.features.append(feature)

        if self.version not in self._available_versions:
            raise InvalidVersionError

        self.repository = result["crate"]["repository"]

        assert self._version_info is not None

        return result

    def download(self, destination_directory: Path | None = None) -> Path:
        log.info("Downloading crate %s", self.name)

        if len(self._available_versions) == 0:
            self._get_metadata()

        if destination_directory is None:
            destination_directory = get_writable_dir_in_tmp()

        uri = _urljoin(self._api_base_url, *self._version_info["dl_path"].split("/"))
        headers = {"User-Agent": "rustbinsign (https://github.com/N0fix/rustbinsign)"}
        res = requests.get(uri, timeout=20, headers=headers)
        assert res.status_code == 200

        result_file = destination_directory.joinpath(f"{self}.tar.gz")
        with pathlib.Path(result_file).open("wb+") as f:
            f.write(res.content)

        return result_file

    def __str__(self):
        return f"{self.name}-{self.version}"

    def __hash__(self):
        return hash((self.name, self.version))
