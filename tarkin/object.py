#!/usr/bin/python3

"""Generic object definitions"""


from __future__ import annotations
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from struct import Struct
from typing import Final, Optional


CLASS_ARRAY_HEADER: Final = Struct('<III')
CLASS_ENTRY_HEADER: Final = Struct('<I')

CLASS_HEADER: Final = Struct('<IIII')


class WMIParameter:
    """Parameter of a WMI method"""

    variable: WMIVariable

    direction: WMIParameterDirection


class WMIMethod:
    """Method exposed by an WMI object"""

    name: str

    qualifiers: list[WMIQualifier]

    parameters: list[WMIParameter]

    return_value: WMIVariable


class WMIObjectType(Enum):
    """WMI object types"""
    CLASS = 0
    INSTANCE = 1


@dataclass(frozen=True)
class WMIObject:
    """WMI object"""

    name: str

    namespace: str

    superclass: str

    object_type: WMIObjectType

    flags: list[str]

    qualifiers: list[WMIQualifier]

    variables: list[WMIVariable]

    methods: list[WMIMethod]

    __slots__ = (
        "name",
        "namespace",
        "superclass",
        "object_type",
        "flags",
        "qualifiers",
        "variables",
        "methods"
    )

    @classmethod
    def iter_from_buffer(cls, buffer: memoryview, flavor_buffer: Optional[memoryview]) -> Iterator[WMIObject]:
        """Parse WMI object array from buffer"""
        unknown1, unknown2, count = CLASS_ARRAY_HEADER.unpack(buffer)
        if unknown1 != 0x1 or unknown2 != 0x1:
            raise ValueError("Unknown values are invalid")

        offset = CLASS_ARRAY_HEADER.size
        for _ in range(count):
            length = CLASS_ENTRY_HEADER.unpack_from(buffer, offset)
            if length > len(buffer) + offset:
                raise ValueError(f"Object size {length} too big")

            yield cls.from_buffer(buffer[offset:offset + length], flavor_buffer)
            offset += length

        if offset != len(buffer):
            raise ValueError("Object array not fully processed")

    @classmethod
    def from_buffer(cls, buffer: memoryview, flavor_buffer: Optional[memoryview]) -> WMIObject:
        """Parse WMI object from buffer"""
        unknown, length1, length2, object_type = CLASS_HEADER.unpack(buffer)
        if unknown != 0x0:
            raise ValueError(f"Unknown value has invalid value: {unknown}")

        if length1 + CLASS_HEADER.size != len(buffer):
            raise ValueError(f"Object siz 1 {length1} too big")

        if length2 > length1:
            raise ValueError(f"Object size 2 {length2} too big")

        raise NotImplementedError("TODO")
