import hashlib
import pathlib
from typing import List, Optional, Set

from pydantic import BaseModel

from ..compiler import get_rustc_version
from ..dependencies import get_dependencies
from .crate import Crate

"""
def guess_is_debug(target: pathlib.Path) -> bool:
    needle = b"run with `RUST_BACKTRACE=1` environment variable to display a backtrace"
    data = open(target, "rb").read()
    return needle in data
    return False
"""


def guess_toolchain(target_content: bytes) -> Optional[str]:
    known_heuristics = {
        b"Mingw-w64 runtime failure": "Mingw-w64",
        b"_CxxThrowException": "windows-msvc",
        b".CRT$": "windows-msvc",
        b"/checkout/src/llvm-project/libunwind/src/DwarfInstructions.hpp": "linux-musl",
    }

    for item, value in known_heuristics.items():
        if item in target_content:
            return value

    return None


def imphash(dependencies: List[Crate]):
    md5 = hashlib.md5()
    sorted_list = sorted([str(d) for d in dependencies])
    for dep in sorted_list:
        md5.update(str(dep).encode())

    return md5.hexdigest()


class TargetRustInfo(BaseModel):
    rustc_version: str
    rustc_commit_hash: str
    dependencies: List[Crate]
    rust_dependencies_imphash: str
    guessed_toolchain: Optional[str] = None
    # guess_is_debug_build: bool

    @classmethod
    def from_target(cls, path: pathlib.Path):
        content = open(path, "rb").read()
        commit, version = get_rustc_version(path)
        dependencies: Set[Crate] = get_dependencies(path)
        dependencies = sorted(list(dependencies), key=lambda x: x.name)

        return TargetRustInfo(
            rustc_commit_hash=commit,
            rustc_version=version,
            dependencies=dependencies,
            rust_dependencies_imphash=imphash(dependencies),
            guessed_toolchain=guess_toolchain(content),
            # guess_is_debug_build=guess_is_debug(path),
        )
