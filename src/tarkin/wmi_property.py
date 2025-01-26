#!/usr/bin/python3

"""WMI property parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final, Optional
from construct import Struct, Container, Adapter, Prefixed, Int32ul, Tell, CString
from .constructs import BmofArray, BmofHeapReference
from .wmi_data import BMOF_WMI_DATA
from .wmi_qualifier import BMOF_WMI_QUALIFIER, WmiQualifier
from .wmi_type import BMOF_WMI_TYPE, WmiType


@dataclass(frozen=True, slots=True)
class WmiProperty:
    """WMI property"""

    data_type: WmiType

    name: Optional[str]

    value: Optional[bool | int | str]

    qualifiers: Optional[list[WmiQualifier]]

    @classmethod
    def from_container(cls, container: Container) -> WmiProperty:
        """Parse WMI property from container"""
        return cls(
            data_type=container["data_type"],
            name=container["heap"]["name"],
            value=container["heap"]["value"],
            qualifiers=container["heap"]["qualifiers"]
        )


class WmiPropertyAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into a WMI property"""
    def _decode(self, obj: Container, context: Container, path: str) -> WmiProperty:
        """Decode container to a WMI property"""
        return WmiProperty.from_container(obj)

    def _encode(self, obj: WmiProperty, context: Container, path: str) -> Container:
        """Encode WMI property to container"""
        raise NotImplementedError("Property encoding is not yet implemented")


BMOF_WMI_PROPERTY: Final = WmiPropertyAdapter(
    Prefixed(
        Int32ul,
        Struct(
            "data_type" / BMOF_WMI_TYPE,
            "name_offset" / Int32ul,
            "value_offset" / Int32ul,
            "qualifiers_offset" / Int32ul,
            "heap" / Struct(
                "offset" / Tell,
                "name" / BmofHeapReference(
                    lambda context: min(context._.name_offset + context.offset, 0xFFFFFFFF),
                    CString("utf_16_le")
                ),
                "value" / BmofHeapReference(
                    lambda context: min(context._.value_offset + context.offset, 0xFFFFFFFF),
                    BMOF_WMI_DATA(
                        lambda context: context._.data_type
                    )
                ),
                "qualifiers" / BmofHeapReference(
                    lambda context: min(context._.qualifiers_offset + context.offset, 0xFFFFFFFF),
                    BmofArray(
                        BMOF_WMI_QUALIFIER
                    )
                )
            )
        ),
        includelength=True
    )
)
