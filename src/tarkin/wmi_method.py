#!/usr/bin/python3

"""WMI method parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final
from construct import Struct, GreedyBytes, Container, Adapter


@dataclass(frozen=True, slots=True)
class WmiMethod:
    """WMI method"""

    data: bytes

    @classmethod
    def from_container(cls, container: Container) -> WmiMethod:
        """Parse WMI method from container"""
        return cls(
            data=bytes(container["data"])
        )


class WmiMethodAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into a WMI method"""
    def _decode(self, obj: Container, context: Container, path: str) -> WmiMethod:
        """Decode container to a WMI method"""
        return WmiMethod.from_container(obj)

    def _encode(self, obj: WmiMethod, context: Container, path: str) -> Container:
        """Encode WMI method to container"""
        return Container(
            data=obj.data
        )


BMOF_WMI_METHOD: Final = WmiMethodAdapter(
    Struct(
        "data" / GreedyBytes
    )
)
