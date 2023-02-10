"""Increment the major.minor.patch version string in the provided file."""

import re
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

parser = ArgumentParser()
parser.add_argument("file", help="The file containing the version string", type=Path)
parser.add_argument(
    "version",
    type=str,
    help="The version to bump; 'infer' will try to infer the version from the last commit message",
    choices=["major", "minor", "patch", "infer"],
)
parser.add_argument("--verbose", "-v", action="store_true")

PATTERN = r"(?:^|\W+)version += +(\d+\.\d+\.\d+)(?:$|\W+)"


def get_last_commit_message() -> str:
    """Get the last commit message.

    Returns
    -------
    str
        The last commit message.
    """
    return (
        subprocess.run(
            ["git", "log", "-1", "--format=%B"], check=True, capture_output=True
        )
        .stdout.decode("utf-8")
        .strip()
    )


def infer_version_from_commit_message(msg: str) -> str:
    """Infer the semver version to increment based on a commit message.

    Parameters
    ----------
    msg : str
        A commit message

    Returns
    -------
    str
        One of 'major', 'minor', or 'patch'
    """
    if "feat!" in msg:
        return "major"
    elif "feat" in msg:
        return "minor"
    else:
        return "patch"


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

    if args.version == "infer":
        args.version = infer_version_from_commit_message(get_last_commit_message())

    if args.version == "major":
        major += 1
        minor = 0
        patch = 0
    elif args.version == "minor":
        minor += 1
        patch = 0
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
