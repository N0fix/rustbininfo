import pathlib
import tempfile
from datetime import datetime

import pytz


def get_writable_dir_in_tmp(name: str = __package__) -> pathlib.Path:
    """Get a writable directory in temp directory.

    Args:
        name (str, optional): Name of the writable directory. Defaults to __package__.

    Returns:
        pathlib.Path: Path of the target directory.

    """
    destination_directory = pathlib.Path(tempfile.gettempdir()) / name
    destination_directory.mkdir(exist_ok=True)
    return destination_directory


def get_min_max_update_time(crates: list) -> tuple[datetime, datetime]:
    """Get a range of dates from which latest dependency got added to the project.

    Args:
        crates (List[Crate]): dependencies of the project

    Returns:
        Tuple[int, int]: min_date, max_data

    """
    utc = pytz.UTC
    min_date, max_date = (
        utc.localize(datetime.fromtimestamp(0)),  # noqa: DTZ006
        utc.localize(
            datetime.now(),  # noqa: DTZ005
        ),
    )

    for dep in crates:
        for i, version in enumerate(dep.metadata["versions"]):
            if version["num"] == dep.version:
                d = datetime.strptime(version["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
                min_date = max(d, min_date)
                break

    for dep in crates:
        for i, version in enumerate(dep.metadata["versions"]):
            if version["num"] == dep.version and i != 0:
                d = datetime.strptime(
                    dep.metadata["versions"][i - 1]["created_at"],
                    "%Y-%m-%dT%H:%M:%S.%f%z",
                )
                if d > min_date:
                    max_date = d
                break

    return min_date, max_date
