from __future__ import annotations

import json
import pathlib
import tarfile
from pathlib import Path

import semver
from pydantic import BaseModel, Field

from ...exception import InvalidVersionError
from ...logger import log
from ...utils import get_writable_dir_in_tmp
from ..http_client import client
from .registry import get_registry_cfg


def _urljoin(base: str, *parts: str) -> str:
    for part in filter(None, parts):
        base = "{}/{}".format(base.rstrip("/"), part.lstrip("/"))
    return base


class ReducedRepresentation:
    def __repr_args__(self: BaseModel) -> ReprArgs:
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
        uri = _urljoin("https://crates.io", *["api", "v1", "crates", self.name])
        headers = {"User-Agent": "rustbinsign (https://github.com/N0fix/rustbinsign)"}
        res = client.get(uri, timeout=20, headers=headers)
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

    def _get_default_destination_dir(self) -> Path:
        return get_writable_dir_in_tmp()

    def download(self, destination_directory: Path | None = None) -> Path:
        log.info("Downloading crate %s", self.name)

        if destination_directory is None:
            destination_directory = self._get_default_destination_dir()

        uri = _urljoin(get_registry_cfg().dl, self.name, self.version, "download")
        headers = {"User-Agent": "rustbinsign (https://github.com/N0fix/rustbinsign)"}
        res = client.get(uri, timeout=20, headers=headers)
        assert res.status_code == 200

        result_file = destination_directory.joinpath(f"{self}.tar.gz")
        with pathlib.Path(result_file).open("wb+") as f:
            # Should ensure that the file is fully written to disk, unlink otherwise.
            try:
                f.write(res.content)

            except Exception as exc:
                pathlib.Path(result_file).unlink()
                raise exc

        return result_file

    def download_untar(self, destination_directory: Path | None = None, remove_tar: bool = False) -> Path:
        if not destination_directory:
            destination_directory = self._get_default_destination_dir()

        path = self.download(destination_directory)

        with tarfile.open(path) as tar:
            tar.extractall(destination_directory, filter="data")
            tar.close()

        if remove_tar:
            tar.unlink()

        return Path(f"{str(path).strip('.tar.gz')}")

    def __str__(self):
        return f"{self.name}-{self.version}"

    def __hash__(self):
        return hash((self.name, self.version))
