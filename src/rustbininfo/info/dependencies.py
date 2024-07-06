import pathlib
import re
from typing import Set

from ..logger import log
from .models.crate import Crate


def _guess_dependencies(content: bytes) -> Set:
    regexes = [
        rb"index.crates.io.[^\\\/]+.([^\\\/]+)",
        rb"registry.src.[^\\\/]+.([^\\\/]+)",
        rb"rust.deps.([^\\\/]+)",
    ]
    result = []
    for reg in regexes:
        res = re.findall(reg, content)
        if len(set(res)) > len(result):
            result = set(res)

    return result


def get_dependencies(target: pathlib.Path, fast_load=False) -> Set[Crate]:
    reserved_names = ["rustc-demangle"]
    result = []
    data = open(target, "rb").read()
    res = _guess_dependencies(data)
    for dep in set(res):
        # Cleaning dependency name
        try:
            dep = dep[: dep.index(b"\x00")]
        except:  # noqa E722
            pass

        if dep == b"":
            continue
        # End of cleaning

        log.debug(f"Found dependency : {dep}")
        c = Crate.from_depstring(dep.decode(), fast_load)
        if c.name not in reserved_names:
            result.append(c)
    return set(result)
