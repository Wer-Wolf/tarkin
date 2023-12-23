#!/usr/bin/python3

"""WMI Qualifier"""


from __future__ import annotations
from dataclasses import dataclass
from struct import Struct
from typing import Final
from .data import mof_parse_data, mof_parse_string
from .type import Type


QUALIFIER_HEADER: Final = Struct('<II4xI')     # TODO Unknown values


@dataclass(frozen=True, slots=True)
class Qualifier:
    """WMI qualifier"""

    name: str

    data_type: Type

    value: bool | int | str

    offset: int

    @classmethod
    def from_buffer(cls, buffer: memoryview, offset: int) -> Qualifier:
        """Parse qualifier from buffer"""
        length, qualifier_type, name_length = QUALIFIER_HEADER.unpack(
            buffer[:QUALIFIER_HEADER.size]
        )
        if len(buffer) != length:
            raise ValueError(f"Qualifier length {length} does not match")

        info_buffer = buffer[QUALIFIER_HEADER.size:]
        if len(info_buffer) < name_length:
            raise ValueError(f"Qualifier name length {name_length} too big")

        name = mof_parse_string(info_buffer[:name_length])
        data_type = Type.from_int(qualifier_type)

        return cls(
            name=name,
            data_type=data_type,
            value=mof_parse_data(data_type, info_buffer[name_length:]),
            offset=offset
        )
