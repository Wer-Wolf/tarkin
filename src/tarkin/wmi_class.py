#!/usr/bin/python3

"""WMI class parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final
from construct import Struct, Container, Adapter, Const, Int32ul, FixedSized, Prefixed, \
    PrefixedArray, Rebuild, len_, this
from .wmi_class_data import BMOF_WMI_CLASS_DATA, WmiClassData
from .wmi_method import BMOF_WMI_METHOD, WmiMethod
from .wmi_qualifier import BMOF_WMI_QUALIFIER, WmiQualifier


@dataclass(frozen=True, slots=True)
class WmiClass:
    """WMI class"""

    qualifiers: list[WmiQualifier]

    data: WmiClassData

    methods: list[WmiMethod]

    @classmethod
    def from_container(cls, container: Container) -> WmiClass:
        """Parse WMI class from container"""
        return cls(
            qualifiers=container["data"]["qualifiers"],
            data=container["data"]["class_data"],
            methods=container["methods"]
        )


class WmiClassAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into a WMI class"""
    def _decode(self, obj: Container, context: Container, path: str) -> WmiClass:
        """Decode container to WMI class"""
        return WmiClass.from_container(obj)

    def _encode(self, obj: WmiClass, context: Container, path: str) -> Container:
        """Encode WMI class to container"""
        return Container(
            data=Container(
                qualifiers=obj.qualifiers,
                class_data=obj.data
            )
        )


BMOF_WMI_CLASS: Final = WmiClassAdapter(
    Prefixed(
        Int32ul,
        Struct(
            "unknown" / Const(0, Int32ul),
            "qualifiers_length" / Rebuild(Int32ul, len_(this.data.qualifiers)),
            "length" / Rebuild(Int32ul, len_(this.data)),
            "type" / Const(0, Int32ul),     # TODO Instance (0x1) support
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
                    "class_data" / BMOF_WMI_CLASS_DATA
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
