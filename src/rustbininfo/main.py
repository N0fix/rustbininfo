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

 rbi info 'challenge.exe'
 rbi download hyper-0.14.27
 rbi guess_project_date 'challenge.exe'
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

    target = ArgumentParser(add_help=False)
    target.add_argument(
        type=str,
        dest="target",
    )

    # Subcommand parsers
    subparsers = parser.add_subparsers(dest="mode", title="mode", help="Mode to use")

    info_parser = subparsers.add_parser(
        "info", help="Get information about an executable", parents=[target]
    )
    info_parser.add_argument('-f', '--full', action='store_true', default=False)

    subparsers.add_parser(
        "guess_project_date",
        parents=[target],
        help="Tries to guess date latest depdnency got added to the project, based on dependencies version",  # noqa E501
    )

    download_parser = subparsers.add_parser(
        "download", help="Download a crate. Exemple: rand_chacha-0.3.1"
    )

    download_parser.add_argument("crate")
    download_parser.add_argument("--directory", required=False, default=None)
    download_parser.add_argument(
        "-e", "--extract", required=False, default=None, action="store_true"
    )

    return parser


def main_cli():
    parser = parse_args()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.mode == "info":
        print(TargetRustInfo.from_target(args.target, not args.full))

    elif args.mode == "download":
        c = Crate.from_depstring(args.crate, fast_load=False)
        try:
            result = c.download(args.directory)

        except InvalidVersionError:
            print("Version of your crate does not exists on crates.io")
            exit(1)

        print(f"{c} downloaded to {result}")

        if args.extract:
            print(f"Extracted to {extract_tarfile(pathlib.Path(result))}")

    elif args.mode == "guess_project_date":
        t = TargetRustInfo.from_target(args.target)
        min_date, max_date = get_min_max_update_time(t.dependencies)
        print(f"Latest dependency was added between {min_date} and {max_date}")


if __name__ == "__main__":
    main_cli()
