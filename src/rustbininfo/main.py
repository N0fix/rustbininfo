import pathlib
import sys
import tarfile
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from rich import print

from rustbininfo import Crate, TargetRustInfo, get_min_max_update_time
from rustbininfo.exception import InvalidVersionError

DESCRIPTION = (
    """Get information about stripped rust executable, and download its dependencies."""
)

example_text = r"""Usage examples:

 rbi 'challenge.exe'
 rbi -d 'challenge.exe'
"""


def extract_tarfile(tar_path: pathlib.Path) -> pathlib.Path:
    """Extract given tarfile.

    Args:
        tar_path (pathlib.Path): Caller must ensure that file exists. Filename must have
        one of the following extensions: '.gz', '.tar', '.tgz'.

    Returns:
        pathlib.Path: directory where files got extracted.
    """
    assert tar_path.exists()

    tar = tarfile.open(tar_path)
    tar.extractall(path=tar_path.parent)
    tar.close()

    if ".gz" in tar_path.suffixes:
        tar_path = tar_path.with_suffix("")

    if ".tar" in tar_path.suffixes:
        tar_path = tar_path.with_suffix("")

    if ".tgz" in tar_path.suffixes:
        tar_path = tar_path.with_suffix("")

    return tar_path


def parse_args():
    # Main parser
    parser = ArgumentParser(
        description=DESCRIPTION,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=example_text,
    )

    parser.add_argument('-f', '--full', action='store_true', default=False, required=False)

    parser.add_argument(
        '-d',
        "--project-date",
        help="Tries to guess date latest depdnency got added to the project, based on dependencies version",  # noqa E501
        required=False,
        action='store_true'
    )

    parser.add_argument(
        type=str,
        dest="target",
    )

    return parser


def main_cli():
    parser = parse_args()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.project_date:
        t = TargetRustInfo.from_target(args.target)
        min_date, max_date = get_min_max_update_time(t.dependencies)
        print(f"Latest dependency was added between {min_date} and {max_date}")
        exit(1)

    # if args.mode == "info":
    print(TargetRustInfo.from_target(args.target, not args.full))

    # elif args.mode == "download":
    #     c = Crate.from_depstring(args.crate, fast_load=False)
    #     try:
    #         result = c.download(args.directory)

    #     except InvalidVersionError:
    #         print("Version of your crate does not exists on crates.io")
    #         exit(1)

    #     print(f"{c} downloaded to {result}")

    #     if args.extract:
    #         print(f"Extracted to {extract_tarfile(pathlib.Path(result))}")



if __name__ == "__main__":
    main_cli()
