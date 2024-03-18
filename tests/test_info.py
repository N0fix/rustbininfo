from rustbininfo import TargetRustInfo


def test_info(target):
    t: TargetRustInfo = TargetRustInfo.from_target(target)
    assert t.rustc_version == "1.65.0"
    assert t.rustc_commit_hash == "9c20b2a8cc7588decb6de25ac6a7912dcef24d65"
    assert len(t.dependencies) == 4
    assert t.rust_dependencies_imphash == "cd7358d2cd75458edda70d567f1555fa"
    assert t.guessed_toolchain == "windows-msvc"
