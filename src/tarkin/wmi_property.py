#!/usr/bin/python3

"""WMI property parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final, Optional
from construct import Struct, Container, Adapter, Prefixed, Int32ul, Const, Rebuild, FixedSized, \
    GreedyString, If, IfThenElse
from .constructs import BmofArray
from .wmi_data import BMOF_WMI_DATA, NullStripAdapter
from .wmi_qualifier import BMOF_WMI_QUALIFIER, WmiQualifier
from .wmi_type import BMOF_WMI_TYPE, WmiType


@dataclass(frozen=True, slots=True)
class WmiProperty:
    """WMI property"""

    data_type: WmiType

    name: str

    value: Optional[bool | int | str]

    qualifiers: Optional[list[WmiQualifier]]

    @classmethod
    def from_container(cls, container: Container) -> WmiProperty:
        """Parse WMI property from container"""
        return cls(
            data_type=container["data_type"],
            name=container["name"],
            value=container["value"],
            qualifiers=container["qualifiers"]
        )


class WmiPropertyAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into a WMI property"""
    def _decode(self, obj: Container, context: Container, path: str) -> WmiProperty:
        """Decode container to a WMI property"""
        return WmiProperty.from_container(obj)

    def _encode(self, obj: WmiProperty, context: Container, path: str) -> Container:
        """Encode WMI property to container"""
        return Container(
            data_type=obj.data_type,
            name=obj.name,
            value=obj.value,
            qualifier=obj.qualifiers
        )


def get_value_offset(container: Container) -> int:
    """Returns the offset of the property value or a placeholder value"""
    if container["value"] is None:
        return 0xFFFFFFFF

    return len(container["name"])


def get_qualifiers_offset(container: Container) -> int:
    """Returns the offset of the property qualifiers or a placeholder value"""
    if container["qualifiers"] is None:
        return 0xFFFFFFFF

    if container["value"] is None:
        return len(container["name"])

    return len(container["name"]) + len(container["value"])


def has_name_length_limit(container: Container) -> bool:
    """Determines is the property name string has a length limit"""
    if container["value_offset"] != 0xFFFFFFFF:
        return True

    if container["qualifiers_offset"] != 0xFFFFFFFF:
        return True

    return False


def get_name_length_limit(container: Container) -> int:
    """Returns the length limit of the property name string"""
    if container["value_offset"] != 0xFFFFFFFF:
        return container["value_offset"]

    return container["qualifiers_offset"]


BMOF_WMI_PROPERTY: Final = WmiPropertyAdapter(
    Prefixed(
        Int32ul,
        Struct(
            "data_type" / BMOF_WMI_TYPE,
            "unknown" / Const(0, Int32ul),
            "value_offset" / Rebuild(
                Int32ul,
                get_value_offset
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
            "value" / If(
                lambda context: context.value_offset != 0xFFFFFFFF,
                IfThenElse(
                    lambda context: context.qualifiers_offset != 0xFFFFFFFF,
                    FixedSized(
                        lambda context: context.qualifiers_offset - context.value_offset,
                        BMOF_WMI_DATA(
                            lambda context: context.data_type
                        )
                    ),
                    BMOF_WMI_DATA(
                        lambda context: context.data_type
                    )
                )
            ),
            "qualifiers" / If(
                lambda context: context.qualifiers_offset != 0xFFFFFFFF,
                BmofArray(
                    BMOF_WMI_QUALIFIER
                )
            )
        ),
        includelength=True
    )
)
