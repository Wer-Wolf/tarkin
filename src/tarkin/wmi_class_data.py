#!/usr/bin/python3

"""WMI class data parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final
from construct import Struct, GreedyBytes, Container, Adapter


@dataclass(frozen=True, slots=True)
class WmiClassData:
    """WMI class data"""

    data: bytes

    @classmethod
    def from_container(cls, container: Container) -> WmiClassData:
        """Parse WMI class from container"""
        return cls(
            data=bytes(container["data"])
        )


class WmiClassDataAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into WMI class data"""
    def _decode(self, obj: Container, context: Container, path: str) -> WmiClassData:
        """Decode container to WMI class data"""
        return WmiClassData.from_container(obj)

    def _encode(self, obj: WmiClassData, context: Container, path: str) -> Container:
        """Encode WMI class data to container"""
        return Container(
            data=obj.data
        )


BMOF_WMI_CLASS_DATA: Final = WmiClassDataAdapter(
    Struct(
        "data" / GreedyBytes
    )
)
