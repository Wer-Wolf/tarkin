#!/usr/bin/python3

"""CLI entry point utilities"""

import sys
from argparse import ArgumentParser, Namespace
from typing import Final
from json import dump
from .bmof import Bmof, BMOF
from .flavor import Flavors
from .wmi_object import WmiObject
from .wmi_object import WmiMethod
from .wmi_property import WmiProperty
from .wmi_qualifier import WmiQualifier
from .wmi_type import WmiType
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


def encode_bmof(o: object, flavors: dict[int, Flavors]) -> dict[str, object]:
    """Handles encoding of BMOF data classes"""
    if isinstance(o, WmiObject):
        object_result: dict[str, object] = {
            "name": o.name,
            "object_type": o.object_type.name.lower(),
            "superclass": o.superclass,
            "namespace": o.namespace,
            "classflags": None,
            "instanceflags": None,
            "alias": o.alias,
            "qualifiers": o.qualifiers,
            "properties": list(o.variables),
            "methods": o.methods
        }

        classflags = o.classflags
        if classflags is not None and classflags.name is not None:
            object_result["classflags"] = classflags.name.lower()

        instanceflags = o.instanceflags
        if instanceflags is not None and instanceflags.name is not None:
            object_result["instanceflags"] = instanceflags.name.lower()

        return object_result

    if isinstance(o, WmiMethod):
        return {
            "name": o.name,
            "parameters": o.parameters,
            "qualifiers": o.qualifiers,
            "return_type": o.return_type
        }

    if isinstance(o, WmiProperty):
        return {
            "name": o.name,
            "data_type": o.data_type,
            "value": o.value,
            "qualifiers": o.qualifiers
        }

    if isinstance(o, WmiQualifier):
        qualifier_result: dict[str, object] = {
            "name": o.name,
            "data_type": o.data_type,
            "value": o.value,
            "flavors": None
        }

        flavor = flavors.get(o.offset)
        if flavor is not None and flavor.name is not None:
            qualifier_result["flavors"] = flavor.name.lower()

        return qualifier_result

    if isinstance(o, WmiType):
        return {
            "basic_type": o.basic_type.name.lower(),
            "is_array": o.is_array
        }

    raise TypeError(f"Unknown type in BMOF: {type(o)}")


def main(args: Namespace) -> int:
    """Entry point for the BMOF parsing tool"""
    bmof: Bmof = BMOF.parse_file(args.path)

    flavors = {}
    if bmof.flavors is not None:
        for flavor in bmof.flavors:
            flavors[flavor.offset] = flavor.flavors

    dump(bmof.root.objects, sys.stdout, default=lambda o: encode_bmof(o, flavors),
         ensure_ascii=False, indent=4)
    sys.stdout.write("\n")

    return 0


def main_cli() -> int:
    """CLI entry point"""
    return main(ARGUMENT_PARSER.parse_args())
