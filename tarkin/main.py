#!/usr/bin/python3

"""CLI entry point utilities"""

from argparse import ArgumentParser, Namespace
from typing import Final
from .bmof import Bmof
from . import __doc__ as description, __version__


__all__ = (
    "ARGUMENT_PARSER",
    "main",
    "main_cli"
)

ARGUMENT_PARSER: Final = ArgumentParser(
    prog="tarkin",
    description=description
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
    """Entry point for the MOF parsing tool"""
    with open(args.path, mode='rb') as fd:
        buffer = fd.read()

    bmof = Bmof.from_buffer(buffer)
    for obj in bmof.objects:
        print(obj.object_type)

    return 0


def main_cli() -> int:
    """CLI entry point"""
    return main(ARGUMENT_PARSER.parse_args())
