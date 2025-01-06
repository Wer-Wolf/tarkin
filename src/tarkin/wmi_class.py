#!/usr/bin/python3

"""WMI class parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final
from construct import Struct, GreedyBytes, Container, Adapter


@dataclass(frozen=True, slots=True)
class WmiClass:
    """WMI class"""

    data: bytes

    @classmethod
    def from_container(cls, container: Container) -> WmiClass:
        """Parse WMI class from container"""
        return cls(
            data=bytes(container["data"]),
        )


class WmiClassAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into a WMI class"""
    def _decode(self, obj: Container, context: Container, path: str) -> WmiClass:
        """Decode container to Root class"""
        return WmiClass.from_container(obj)

    def _encode(self, obj: WmiClass, context: Container, path: str) -> Container:
        """Encode WMI class to container"""
        return Container(
            data=obj.data
        )


BMOF_WMI_CLASS: Final = WmiClassAdapter(
    Struct(
        "data" / GreedyBytes
    )
)
