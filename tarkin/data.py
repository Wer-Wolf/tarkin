#!/usr/bin/python3

"""Data parsing functions"""


from __future__ import annotations
from struct import Struct
from typing import Final
from .type import Type, DataType


BOOLEAN: Final = Struct('<I')
SINT32: Final = Struct('<i')


def mof_parse_data(data_type: Type, buffer: memoryview) -> bool | int | str:
    """Parse data from buffer"""
    if data_type.is_array:
        raise NotImplementedError

    match data_type.basic_type:
        case DataType.BOOLEAN:
            return mof_parse_boolean(buffer)
        case DataType.SINT32:
            return mof_parse_sint32(buffer)
        case DataType.STRING:
            return mof_parse_string(buffer)
        case _:
            raise NotImplementedError


def mof_parse_boolean(buffer: memoryview) -> bool:
    """Parse boolean value"""
    if len(buffer) != BOOLEAN.size:
        return True     # TODO verify if this is correct

    value, = BOOLEAN.unpack(buffer)
    if value != 0x0 and value != 0xffff:
        raise ValueError(f"Invalid boolean value: {value}")

    return value == 0xffff


def mof_parse_string(buffer: memoryview) -> str:
    """Parse string value"""
    return str(buffer, 'utf-16-le', 'strict').rstrip('\x00')


def mof_parse_sint32(buffer: memoryview) -> int:
    """Parse sint32 value"""
    value, = SINT32.unpack(buffer)

    return value
