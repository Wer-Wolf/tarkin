#!/usr/bin/python3

"""Binary MOF root structure"""


from __future__ import annotations
from dataclasses import dataclass
from struct import Struct
from typing import Final
from .flavor import QualifierFlavor, flavors_from_buffer
from .object import WMIObject


BMOF_HEADER: Final = Struct('<4sI')
FLAVOR_HEADER: Final = Struct('<16sI')


@dataclass(frozen=True, slots=True)
class BmofRoot:
    """Binary MOF root structure"""

    objects: list[WMIObject]

    flavors: dict[int, QualifierFlavor]

    @classmethod
    def from_buffer(cls, buffer: memoryview) -> BmofRoot:
        """Parse binary MOF data"""
        magic, length = BMOF_HEADER.unpack(buffer)
        flavors = {}

        if magic != b'BMOF':
            raise ValueError(f"File magic {magic} does not match")

        if length > len(buffer):
            raise ValueError(f"Record size {length} too big")

        if length < len(buffer):
            for flavor in flavors_from_buffer(buffer[length:]):
                if flavor.offset in flavors:
                    raise ValueError(f"Duplicate flavor offset {flavor.offset}")

                flavors[flavor.offset] = flavor

        object_buffer = buffer[BMOF_HEADER.size:length - BMOF_HEADER.size]

        return cls(
            objects=list(WMIObject.iter_from_buffer(object_buffer)),
            flavors=flavors
        )
