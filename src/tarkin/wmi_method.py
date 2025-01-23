#!/usr/bin/python3

"""WMI method parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final, Optional
from construct import Struct, Container, Adapter, Prefixed, Int32ul, Const, Rebuild, FixedSized, \
    GreedyString, PrefixedArray, If, IfThenElse, GreedyBytes
from .wmi_qualifier import BMOF_WMI_QUALIFIER, WmiQualifier
from .wmi_data import NullStripAdapter


@dataclass(frozen=True, slots=True)
class WmiMethod:
    """WMI method"""

    name: str

    parameters: Optional[bytes]

    qualifiers: Optional[list[WmiQualifier]]

    @classmethod
    def from_container(cls, container: Container) -> WmiMethod:
        """Parse WMI method from container"""
        return cls(
            name=container["name"],
            parameters=container["parameters"],
            qualifiers=container["qualifiers"]
        )


class WmiMethodAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into a WMI method"""
    def _decode(self, obj: Container, context: Container, path: str) -> WmiMethod:
        """Decode container to a WMI method"""
        return WmiMethod.from_container(obj)

    def _encode(self, obj: WmiMethod, context: Container, path: str) -> Container:
        """Encode WMI method to container"""
        return Container(
            name=obj.name,
            parameters=obj.parameters,
            qualifiers=obj.qualifiers
        )


def get_parameters_offset(container: Container) -> int:
    """Returns the offset of the method parameters or a placeholder value"""
    if container["parameters"] is None:
        return 0xFFFFFFFF

    return len(container["name"])


def get_qualifiers_offset(container: Container) -> int:
    """Returns the offset of the method qualifiers or a placeholder value"""
    if container["qualifiers"] is None:
        return 0xFFFFFFFF

    if container["parameters"] is None:
        return len(container["name"])

    return len(container["name"]) + len(container["parameters"])


def has_name_length_limit(container: Container) -> bool:
    """Determines is the method name string has a length limit"""
    if container["parameters_offset"] != 0xFFFFFFFF:
        return True

    if container["qualifiers_offset"] != 0xFFFFFFFF:
        return True

    return False


def get_name_length_limit(container: Container) -> int:
    """Returns the length limit of the method name string"""
    if container["parameters_offset"] != 0xFFFFFFFF:
        return container["parameters_offset"]

    return container["qualifiers_offset"]


BMOF_WMI_METHOD: Final = WmiMethodAdapter(
    Prefixed(
        Int32ul,
        Struct(
            "method_type" / Const(0x200D, Int32ul),     # TODO Can also be 0x0
            "unknown" / Const(0, Int32ul),
            "parameters_offset" / Rebuild(
                Int32ul,
                get_parameters_offset
            ),
            "qualifiers_offset" / Rebuild(
                Int32ul,
                get_qualifiers_offset
            ),
            "name" / IfThenElse(
                has_name_length_limit,
                FixedSized(
                    get_name_length_limit,
                    NullStripAdapter(
                        GreedyString("utf-16-le")
                    )
                ),
                NullStripAdapter(
                    GreedyString("utf-16-le")
                )
            ),
            "parameters" / If(
                lambda context: context.parameters_offset != 0xFFFFFFFF,
                IfThenElse(
                    lambda context: context.qualifiers_offset != 0xFFFFFFFF,
                    FixedSized(
                        lambda context: context.qualifiers_offset - context.parameters_offset,
                        GreedyBytes
                    ),
                    GreedyBytes
                )
            ),
            "qualifiers" / If(
                lambda context: context.qualifiers_offset != 0xFFFFFFFF,
                Prefixed(
                    Int32ul,
                    PrefixedArray(
                        Int32ul,
                        BMOF_WMI_QUALIFIER
                    ),
                    includelength=True
                )
            )
        ),
        includelength=True
    )
)
