[![pypi package](https://badge.fury.io/py/rustbininfo.svg)](https://pypi.org/project/rustbininfo)
[![GitHub](https://img.shields.io/github/license/N0fix/rustbininfo.svg)](https://github.com/N0fix/rustbininfo/blob/master/LICENSE)

Get information about a stripped rust executable.

This tool is mentioned in [this](https://nofix.re/posts/2024-11-02-rust-symbs/) and [this](https://nofix.re/posts/2024-08-03-arti-rust/) blogposts.

## Example

```
> rbi ~/Downloads/crackme.exe
TargetRustInfo(
    rustc_version='1.65.0',
    rustc_commit_hash='9c20b2a8cc7588decb6de25ac6a7912dcef24d65',
    dependencies=[
        Crate(name='crc-any', version='2.4.3', features=[], repository=None),
        Crate(name='rand', version='0.8.5', features=[], repository=None),
        Crate(name='rand_chacha', version='0.3.1', features=[], repository=None),
        Crate(name='short-crypt', version='1.0.26', features=[], repository=None)
    ],
    rust_dependencies_imphash='cd7358d2cd75458edda70d567f1555fa',
    guessed_toolchain='windows-msvc'
)
```

## Usage
```
rbi
usage: rbi [-h] [-f] [-d] target

Get information about stripped rust executable, and download its dependencies.

positional arguments:
  target

options:
  -h, --help          show this help message and exit
  -f, --full
  -d, --project-date  Tries to guess date latest depdnency got added to the project, based on dependencies version

Usage examples:

 rbi 'challenge.exe'
 rbi -f 'challenge.exe'
 rbi -d 'challenge.exe'
```

## Tests

Tests requieres git-lfs to retrive the test executable.

Then, execute the following command:

```
git lfs fetch
git lfs pull
pytest -s
```