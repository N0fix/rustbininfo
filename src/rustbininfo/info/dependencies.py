import pathlib
import re
from typing import Set

from ..logger import log
from .models.crate import Crate


def _guess_dependencies(content: bytes) -> Set:
    regexes = [
        # "/index.crates.io-6f17d22bba15001f/rayon-core-1.12.1/src/job.rs
        rb"index.crates.io.[^\\\/]+.([a-zA-Z0-9_-]+-[a-zA-Z0-9._-]+)",
        # \registry\src\github.com-1ecc6299db9ec823\aho-corasick-0.7.15\src\ahocorasick.rs
        rb"registry.src.[^\\\/]+.([a-zA-Z0-9_-]+-[a-zA-Z0-9._-]+)",
        # /rust/deps\indexmap-2.2.6\src\map\core.rs
        rb"rust.deps.([a-zA-Z0-9_-]+-[a-zA-Z0-9._-]+)",
        # crate-1.0.0\src\lib.rs
        rb"\x00([a-z0-9_-]+-[0-9.]+-[a-zA-Z0-9._-]+)[\\/][a-z]",
    ]
    result = set()
    for reg in regexes:
        res = re.findall(reg, content)
        result.update(res)

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
