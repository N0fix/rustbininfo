import hashlib
import pathlib
from typing import List, Optional, Set

import yara
from pydantic import BaseModel

from ..compiler import get_rustc_version
from ..dependencies import get_dependencies
from ..specifics.mingw import (RULE_MINGW_6_GCC_8_3_0, RULE_MINGW_7_GCC_9_3_0,
                               RULE_MINGW_8_GCC_10_3_0,
                               RULE_MINGW_10_GCC_12_2_0,
                               RULE_MINGW_11_GCC_13_1_0)
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
        lambda c: (
            yara.compile(source=RULE_MINGW_6_GCC_8_3_0).match(data=c)
        ): "Mingw-w64 (Mingw6-GCC_8.3.0)",
        lambda c: (
            yara.compile(source=RULE_MINGW_7_GCC_9_3_0).match(data=c)
        ): "Mingw-w64 (Mingw7-GCC_9.3.0)",
        lambda c: (
            yara.compile(source=RULE_MINGW_8_GCC_10_3_0).match(data=c)
        ): "Mingw-w64 (Mingw8-GCC_10.3.0)",
        lambda c: (
            yara.compile(source=RULE_MINGW_10_GCC_12_2_0).match(data=c)
        ): "Mingw-w64 (Mingw10-GCC_12.2.0)",
        lambda c: (
            yara.compile(source=RULE_MINGW_11_GCC_13_1_0).match(data=c)
        ): "Mingw-w64 (Mingw11-GCC_13.1.0)",
        lambda c: (
            b"Mingw-w64 runtime failure" in c
        ): "Mingw-w64 (Could not find mingw/gcc version)",
        lambda c: (b"_CxxThrowException" in c): "windows-msvc",
        lambda c: (b".CRT$" in c): "windows-msvc",
        lambda c: (
            b"/checkout/src/llvm-project/libunwind/src/DwarfInstructions.hpp" in c
        ): "linux-musl",
    }

    for item, value in known_heuristics.items():
        if item(target_content):
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
    def from_target(cls, path: pathlib.Path, fast_load: bool = True):
        content = open(path, "rb").read()
        commit, version = get_rustc_version(path)
        dependencies: Set[Crate] = get_dependencies(path, fast_load)
        dependencies = sorted(list(dependencies), key=lambda x: x.name)

        return TargetRustInfo(
            rustc_commit_hash=commit,
            rustc_version=version,
            dependencies=dependencies,
            rust_dependencies_imphash=imphash(dependencies),
            guessed_toolchain=guess_toolchain(content),
            # guess_is_debug_build=guess_is_debug(path),
        )
