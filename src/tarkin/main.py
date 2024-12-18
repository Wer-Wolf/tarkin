#!/usr/bin/python3

"""CLI entry point utilities"""

from argparse import ArgumentParser, Namespace
from typing import Final
from .bmof import Bmof, BMOF
from . import __doc__ as description, __version__


__all__ = (
    "ARGUMENT_PARSER",
    "main",
    "main_cli"
)

ARGUMENT_PARSER: Final = ArgumentParser(
    prog="tarkin",
    description=f"{description}."
)
ARGUMENT_PARSER.add_argument(
    "-v",
    "--version",
    action="version",
    version=f"%(prog)s {__version__}"
)
ARGUMENT_PARSER.add_argument(
    "path",
    metavar="PATH",
)


def main(args: Namespace) -> int:
    """Entry point for the BMOF parsing tool"""
    bmof: Bmof = BMOF.parse_file(args.path)

    print(bmof)

    return 0


def main_cli() -> int:
    """CLI entry point"""
    return main(ARGUMENT_PARSER.parse_args())
