from pathlib import Path

from rustbininfo import TargetRustInfo, get_min_max_update_time


def test_dates():
    target: Path = Path(__file__).parent.joinpath("crackme.exe")
    assert target.exists()

    t: TargetRustInfo = TargetRustInfo.from_target(target)
    min_date, max_date = get_min_max_update_time(t.dependencies)
    assert str(min_date) == "2022-05-20 02:05:25.815861+00:00"
    assert str(max_date) == "2022-11-04 01:47:56.740655+00:00"
