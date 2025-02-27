#!/usr/bin/python3

"""WMI property parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final, Optional
from construct import Struct, Container, Adapter, Prefixed, Int32ul, Tell, CString
from .constructs import BmofArray, BmofHeapReference
from .wmi_data import BmofWmiData, WmiData
from .wmi_qualifier import BMOF_WMI_QUALIFIER, WmiQualifier
from .wmi_type import BMOF_WMI_TYPE, WmiType


@dataclass(frozen=True, slots=True)
class WmiProperty:
    """WMI property"""

    data_type: WmiType

    name: Optional[str]

    value: Optional[WmiData]

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
                    BmofWmiData(
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
"""
The BMOF property structure.

The BMOF property structure starts with a header containing the following entries:
 - A 32-bit little-endian length value specifying the length of the whole property structure
   including the header in bytes
 - The data type of the value encoded inside the property structure
 - A 32-bit little endian heap reference to the name substructure
 - A 32-bit little endian heap reference to the value substructure
 - A 32-bit little endian heap reference to the qualifiers substructure

The remaining bytes form the heap containing the name, value and qualifiers
substructures. The name substructure consists of a single null-terminated utf-16-le string
specifying the name of the property encoded by the property structure, with the property value
being encoded by the value substructure. The qualifiers substructure on the other hand consists
of a BMOF array containing the qualifiers of the property encoded by the property structure.
"""
