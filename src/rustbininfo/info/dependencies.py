import pathlib
import re
from typing import Set

from ..logger import log
from .models.crate import Crate


def _guess_dependencies(content: bytes) -> Set:
    regexes = [
        rb'index.crates.io.[^\\\/]+.([^\\\/]+)',
        rb'registry.src.[^\\\/]+.([^\\\/]+)'
    ]
    result = []
    for reg in regexes:
        res = re.findall(reg, content)
        if len(set(res)) > len(result):
            result = set(res)

    return result

def get_dependencies(target: pathlib.Path) -> Set[Crate]:
    result = []
    data = open(target, "rb").read()
    res = _guess_dependencies(data)
    for dep in set(res):
        try:
            dep = dep[: dep.index(b"\x00")]
        except: # noqa E722
            pass

        if dep == b"":
            continue
        log.debug(f"Found dependency : {dep}")
        c = Crate.from_depstring(dep.decode(), fast_load=False)
        if c.name != "rustc-demangle":
            result.append(c)
    return set(result)
