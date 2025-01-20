#!/usr/bin/python3

"""Root structure parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final
from construct import Struct, Int32ul, Const, Container, Adapter, FixedSized, Rebuild, this, \
    len_, PrefixedArray
from .wmi_object import BMOF_WMI_OBJECT, WmiObject


@dataclass(frozen=True, slots=True)
class Root:
    """Root structure"""

    objects: list[WmiObject]

    @classmethod
    def from_container(cls, container: Container) -> Root:
        """Parse root structure from container"""
        return cls(
            objects=container["data"]["objects"]
        )


class RootAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into a Root class"""
    def _decode(self, obj: Container, context: Container, path: str) -> Root:
        """Decode container to Root class"""
        return Root.from_container(obj)

    def _encode(self, obj: Root, context: Container, path: str) -> Container:
        """Encode Root class to container"""
        return Container(
            data=Container(
                objects=obj.objects
            )
        )


BMOF_ROOT: Final = RootAdapter(
    Struct(
        "magic" / Const(b"FOMB"),
        "length" / Rebuild(Int32ul, len_(this)),
        "data" / FixedSized(
            lambda this: this.length - 8,   # 8 is the length of the "magic" and "length" fields
            Struct(
                "unknown1" / Const(1, Int32ul),
                "unknown2" / Const(1, Int32ul),
                "objects" / PrefixedArray(
                    Int32ul,
                    BMOF_WMI_OBJECT
                )
            )
        )
    )
)
