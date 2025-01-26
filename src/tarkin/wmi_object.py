#!/usr/bin/python3

"""WMI object parser"""

from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum, unique, STRICT
from typing import Final, Optional
from construct import Struct, Container, Adapter, Int32ul, Prefixed, Tell
from .constructs import BmofArray, BmofHeapReference
from .wmi_method import BMOF_WMI_METHOD, WmiMethod
from .wmi_property import BMOF_WMI_PROPERTY, WmiProperty
from .wmi_qualifier import BMOF_WMI_QUALIFIER, WmiQualifier


@unique
class WmiObjectType(IntEnum, boundary=STRICT):
    """WMI object types"""
    CLASS = 0
    INSTANCE = 1


@dataclass(frozen=True, slots=True)
class WmiObject:
    """WMI object"""

    object_type: WmiObjectType

    qualifiers: Optional[list[WmiQualifier]]

    properties: Optional[list[WmiProperty]]

    methods: Optional[list[WmiMethod]]

    @classmethod
    def from_container(cls, container: Container) -> WmiObject:
        """Parse WMI object from container"""
        return cls(
            object_type=WmiObjectType(int(container["object_type"])),
            qualifiers=container["heap"]["qualifiers"],
            properties=container["heap"]["properties"],
            methods=container["heap"]["methods"]
        )


class WmiObjectAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into a WMI object"""
    def _decode(self, obj: Container, context: Container, path: str) -> WmiObject:
        """Decode container to WMI object"""
        return WmiObject.from_container(obj)

    def _encode(self, obj: WmiObject, context: Container, path: str) -> Container:
        """Encode WMI object to container"""
        raise NotImplementedError("Object encoding is not yet implemented")


BMOF_WMI_OBJECT: Final = WmiObjectAdapter(
    Prefixed(
        Int32ul,
        Struct(
            "qualifiers_offset" / Int32ul,
            "properties_offset" / Int32ul,
            "methods_offset" / Int32ul,
            "object_type" / Int32ul,
            "heap" / Struct(
                "offset" / Tell,
                "qualifiers" / BmofHeapReference(
                    lambda context: min(context._.qualifiers_offset + context.offset, 0xFFFFFFFF),
                    BmofArray(
                        BMOF_WMI_QUALIFIER
                    )
                ),
                "properties" / BmofHeapReference(
                    lambda context: min(context._.properties_offset + context.offset, 0xFFFFFFFF),
                    BmofArray(
                        BMOF_WMI_PROPERTY
                    )
                ),
                "methods" / BmofHeapReference(
                    lambda context: min(context._.methods_offset + context.offset, 0xFFFFFFFF),
                    BmofArray(
                        BMOF_WMI_METHOD
                    )
                )
            )
        ),
        includelength=True
    )
)
