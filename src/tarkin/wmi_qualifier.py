#!/usr/bin/python3

"""WMI qualifier parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final
from construct import Struct, GreedyBytes, Container, Adapter


@dataclass(frozen=True, slots=True)
class WmiQualifier:
    """WMI qualifier"""

    data: bytes

    @classmethod
    def from_container(cls, container: Container) -> WmiQualifier:
        """Parse WMI qualifier from container"""
        return cls(
            data=bytes(container["data"])
        )


class WmiQualifierAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into a WMI qualifier"""
    def _decode(self, obj: Container, context: Container, path: str) -> WmiQualifier:
        """Decode container to a WMI qualifier"""
        return WmiQualifier.from_container(obj)

    def _encode(self, obj: WmiQualifier, context: Container, path: str) -> Container:
        """Encode WMI qualifier to container"""
        return Container(
            data=obj.data
        )


BMOF_WMI_QUALIFIER: Final = WmiQualifierAdapter(
    Struct(
        "data" / GreedyBytes
    )
)
