import os
from pathlib import Path

from rustbininfo import Crate


def test_dates():
    c = Crate.from_depstring("rpecli-0.1.1")
    result = c.download()
    assert Path(result).exists()
    os.unlink(result)
