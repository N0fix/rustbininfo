import os
import pathlib

import tomllib
from pydantic import BaseModel

from ..http_client import client


class RegistryCFG(BaseModel):
    registry_path: str
    dl: str
    api: str


def _get_registry(src: dict) -> RegistryCFG:
    if url := src.get("registry"):
        url = url.split("+")[-1]
        result = client.get(url + "/config.json").json()
        dl, api = result["dl"], result["api"]
        return RegistryCFG(registry_path=f"{url}", dl=dl, api=api)

    if file := src.get("local-registry"):
        raise NotImplementedError

    if directory := src.get("directory"):
        raise NotImplementedError


def _get_registry_cfg() -> RegistryCFG:
    env_to_fetch = "USERPROFILE" if os.name == "nt" else "HOME"

    cfg_path = pathlib.Path(os.environ.get("CARGO_HOME", pathlib.Path(os.environ.get(env_to_fetch)) / ".cargo"))
    potential_cfgs = [cfg_path / "config", cfg_path / "config.toml"]

    for cfg in potential_cfgs:
        if cfg.exists():
            config = tomllib.loads(cfg.read_text())
            if source := config.get("source"):
                current_src = source.get("crates-io")
                while True:
                    if s := current_src.get("replace-with"):
                        current_src = source.get(s)

                    else:
                        break

                return _get_registry(current_src)

            break

    return RegistryCFG(
        registry_path="https://index.crates.io/", dl="https://static.crates.io/crates", api="https://crates.io"
    )


def get_registry_cfg():
    if hasattr(get_registry_cfg, "cfg"):
        return get_registry_cfg.cfg

    get_registry_cfg.cfg = _get_registry_cfg()
    return get_registry_cfg.cfg
