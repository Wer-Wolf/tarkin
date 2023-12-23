#!/usr/bin/python3

"""Data type information"""

from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum, unique, STRICT
from typing import Final


ARRAY_FLAG: Final = 0x2000


@unique
class DataType(IntEnum, boundary=STRICT):
    """MOF data types"""
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


@dataclass(frozen=True, slots=True)
class Type:
    """MOF data type information"""

    basic_type: DataType

    is_array: bool

    @classmethod
    def from_int(cls, value: int) -> Type:
        """Parse type information from integer"""
        return cls(
            basic_type=DataType(value & ~ARRAY_FLAG),
            is_array=bool(value & ARRAY_FLAG)
        )
