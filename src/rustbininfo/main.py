import pathlib
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from rich import print

from rustbininfo import TargetRustInfo, get_min_max_update_time
from rustbininfo.info.compiler import BasicProvider
from rustbininfo.info.nightly.nightly import NightlyGetter
from rustbininfo.info.rust_repo_handler import GitRepoProvider

DESCRIPTION = """Get information about stripped rust executable, and download its dependencies."""

example_text = r"""Usage examples:

 rbi 'challenge.exe'
 rbi -d 'challenge.exe'
"""


def parse_args() -> ArgumentParser:  # noqa: D103
    # Main parser
    parser = ArgumentParser(
        description=DESCRIPTION,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=example_text,
    )

    parser.add_argument("-f", "--full", action="store_true", default=False, required=False)

    parser.add_argument(
        "-d",
        "--project-date",
        help="Tries to guess date latest dependency got added to the project, based on dependencies version",
        required=False,
        action="store_true",
    )

    parser.add_argument(
        "--version",
        help="Get compiler version date",
        required=False,
        action="store_true",
    )

    parser.add_argument(
        "--nightly",
        "-n",
        help="Get compiler nightly version",
        required=False,
        action="store_true",
    )

    parser.add_argument(
        "--repo",
        "-r",
        help="Define rust local repository, in case you get rate limited by GitHub. This option requires rustbininfo[gitpython] to be installed.",
        required=False,
        dest="repo",
    )

    parser.add_argument(
        type=str,
        dest="target",
    )

    return parser


def get_provider(get_repo_provider: str):
    provider = BasicProvider()
    if get_repo_provider:
        from .info.rust_repo_handler import GitRepoProvider

        provider = GitRepoProvider(pathlib.Path(get_repo_provider))

    return provider


def main_cli() -> None:  # noqa: D103
    parser = parse_args()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    provider = get_provider(args.repo)

    if args.project_date or args.version or args.nightly:
        t = TargetRustInfo.from_target(args.target, provider=provider)

    if args.nightly:
        nightly_getter = NightlyGetter()
        date = nightly_getter.get_nightly_toolchain_for_rustc_version(t.rustc_version)
        print(f"Nightly version: nightly-{date}-<toolchain> (e.g nightly-{date}-x86_64-unknown-linux-gnu)")
        sys.exit(0)

    if args.project_date:
        min_date, max_date = get_min_max_update_time(t.dependencies)
        print(f"Latest dependency was added between {min_date} and {max_date}")
        sys.exit(0)

    if args.version:
        date = provider.get_rustc_version_date(t.rustc_version)
        print(date)
        sys.exit(0)

    print(TargetRustInfo.from_target(args.target, not args.full, provider=provider))


if __name__ == "__main__":
    main_cli()
