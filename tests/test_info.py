from pathlib import Path

from rustbininfo import TargetRustInfo


def test_info():
    target: Path = Path(__file__).parent.joinpath("crackme.exe")
    assert target.exists()
    t: TargetRustInfo = TargetRustInfo.from_target(target)
    assert t.rustc_version == "1.65.0"
    assert t.rustc_commit_hash == "9c20b2a8cc7588decb6de25ac6a7912dcef24d65"
    assert len(t.dependencies) == 4
    assert t.rust_dependencies_imphash == "cd7358d2cd75458edda70d567f1555fa"
    assert t.guessed_toolchain == "windows-msvc"

def test_info_archiver():
    target: Path = Path(__file__).parent.joinpath("archiver.exe")
    assert target.exists()
    t: TargetRustInfo = TargetRustInfo.from_target(target)
    assert t.rustc_version == "1.77.2"
    assert t.rustc_commit_hash == "3c85e56249b0b1942339a6a989a971bf6f1c9e0f"
    assert len(t.dependencies) == 22
    assert t.rust_dependencies_imphash == "b5386521b71aa121e153e8b45f9986e1"
    assert t.guessed_toolchain == "Mingw-w64"
