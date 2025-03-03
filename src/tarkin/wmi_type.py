#!/usr/bin/python3

"""WMI data type parser"""

from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum, unique, STRICT
from typing import Final
from construct import Adapter, Container, Int32ul


ARRAY_FLAG: Final = 0x2000


@unique
class WmiDataType(IntEnum, boundary=STRICT):
    """WMI data types"""
    BOOLEAN = 11
    UINT8 = 17
    SINT8 = 16
    UINT16 = 18
    SINT16 = 2
    UINT32 = 19
    SINT32 = 3
    UINT64 = 21
    SINT64 = 20
    REAL32 = 4
    REAL64 = 5
    CHAR16 = 103
    STRING = 8
    OBJECT = 13
    DATETIME = 101
    REFERENCE = 102
    VOID = 0


@dataclass(frozen=True, slots=True)
class WmiType:
    """WMI type"""

    basic_type: WmiDataType

    is_array: bool

    @classmethod
    def from_data_type(cls, data_type: WmiDataType):
        """Create WMI type from a simple WMI data type"""
        return cls(
            basic_type=data_type,
            is_array=False
        )

    @classmethod
    def from_int(cls, value: int) -> WmiType:
        """Parse WMI type from integer"""
        return cls(
            basic_type=WmiDataType(value & ~ARRAY_FLAG),
            is_array=bool(value & ARRAY_FLAG)
        )

    def __int__(self) -> int:
        """Convert WMI type to an integer"""
        data_type = int(self.basic_type)

        if self.is_array:
            data_type |= ARRAY_FLAG

        return data_type

    def __eq__(self, other: object) -> bool:
        """Compare WMI type"""
        if isinstance(other, WmiDataType):
            if self.is_array:
                return False

            return self.basic_type == other

        if isinstance(other, WmiType):
            return self.basic_type == other.basic_type and self.is_array == other.is_array

        return NotImplemented

    def __hash__(self) -> int:
        """Hash WMI type"""
        return int(self)


class WmiTypeAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an integer into an WMI type"""
    def _decode(self, obj: int, context: Container, path: str) -> WmiType:
        """Decode integer to Wmi type"""
        return WmiType.from_int(obj)

    def _encode(self, obj: WmiType, context: Container, path: str) -> int:
        """Encode Wmi type to integer"""
        return int(obj)


BMOF_WMI_TYPE: Final = WmiTypeAdapter(Int32ul)
"""
The BMOF data type structure.

The BMOF data type structure is a 32-bit little endian integer
specifying a WMI data type.
"""
