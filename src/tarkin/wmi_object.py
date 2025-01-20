#!/usr/bin/python3

"""WMI object parser"""

from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum, unique, STRICT
from typing import Final
from construct import Struct, Container, Adapter, Const, Int32ul, FixedSized, Prefixed, \
    PrefixedArray, Rebuild, len_, this
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

    qualifiers: list[WmiQualifier]

    properties: list[WmiProperty]

    methods: list[WmiMethod]

    @classmethod
    def from_container(cls, container: Container) -> WmiObject:
        """Parse WMI object from container"""
        return cls(
            object_type=WmiObjectType(int(container["object_type"])),
            qualifiers=container["data"]["qualifiers"],
            properties=container["data"]["properties"],
            methods=container["methods"]
        )


class WmiObjectAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into a WMI object"""
    def _decode(self, obj: Container, context: Container, path: str) -> WmiObject:
        """Decode container to WMI object"""
        return WmiObject.from_container(obj)

    def _encode(self, obj: WmiObject, context: Container, path: str) -> Container:
        """Encode WMI object to container"""
        return Container(
            object_type=int(obj.object_type),
            data=Container(
                qualifiers=obj.qualifiers,
                properties=obj.properties
            ),
            methods=obj.methods
        )


BMOF_WMI_OBJECT: Final = WmiObjectAdapter(
    Prefixed(
        Int32ul,
        Struct(
            "unknown" / Const(0, Int32ul),
            "qualifiers_length" / Rebuild(Int32ul, len_(this.data.qualifiers)),
            "length" / Rebuild(Int32ul, len_(this.data)),
            "object_type" / Int32ul,
            "data" / FixedSized(
                lambda context: context.length,
                Struct(
                    "qualifiers" / FixedSized(
                        lambda context: context._.qualifiers_length,
                        Prefixed(
                            Int32ul,
                            PrefixedArray(
                                Int32ul,
                                BMOF_WMI_QUALIFIER
                            ),
                            includelength=True
                        )
                    ),
                    "properties" / Prefixed(
                        Int32ul,
                        PrefixedArray(
                            Int32ul,
                            BMOF_WMI_PROPERTY
                        ),
                        includelength=True
                    )
                )
            ),
            "methods" / Prefixed(
                Int32ul,
                PrefixedArray(
                    Int32ul,
                    BMOF_WMI_METHOD
                ),
                includelength=True
            )
        ),
        includelength=True
    )
)
