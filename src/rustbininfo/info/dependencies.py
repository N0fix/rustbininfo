import pathlib
import re
from typing import Set

from ..logger import log
from .models.crate import Crate


def get_dependencies(target: pathlib.Path) -> Set[Crate]:
    result = []
    data = open(target, "rb").read()
    res = re.findall(rb"registry.src.[^\\\/]+.([^\\\/]+)", data)
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
