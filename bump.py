"""Increment the major.minor.patch version string in the provided file."""

import re
import sys
from argparse import ArgumentParser
from pathlib import Path

parser = ArgumentParser()
parser.add_argument("file", help="The file containing the version string", type=Path)
parser.add_argument(
    "version", type=str, help="The version to bump", choices=["major", "minor", "patch"]
)
parser.add_argument("--verbose", "-v", action="store_true")

PATTERN = r"(?:^|\W+)version += +(\d+\.\d+\.\d+)(?:$|\W+)"


def print_and_exit(msg: str, exit_code: int = 1) -> None:
    """Print a message to stderr and exit with a non-zero exit code.

    Parameters
    ----------
    msg : str
        Message for stderr
    exit_code : int, optional
        Non-zero exit code, by default 1
    """
    if exit_code == 0:
        raise ValueError("Must provide non-zero exit code")
    print(msg, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    """Increment the major.minor.patch version string in the provided file."""
    args = parser.parse_args()

    with args.file.open("r") as f:
        setup_cfg = f.read()

    matches = re.findall(PATTERN, setup_cfg)
    if not matches:
        print_and_exit("No version strings found")
    if len(matches) > 1:
        print_and_exit("More than one matching version string found")

    version_string = matches[0]

    if args.verbose:
        print(f"Old version: {version_string}")

    major, minor, patch = tuple(map(int, version_string.split(".")))

    if sys.argv[1] == "major":
        major += 1
    elif sys.argv[1] == "minor":
        minor += 1
    else:
        patch += 1

    new_version_string = f"{major}.{minor}.{patch}"

    if args.verbose:
        print(f"New version: {new_version_string}")

    new_setup_cfg = re.sub(
        PATTERN,
        lambda match: match.group().replace(version_string, new_version_string),
        setup_cfg,
    )

    with args.file.open("w") as f:
        f.write(new_setup_cfg)


if __name__ == "__main__":
    main()
