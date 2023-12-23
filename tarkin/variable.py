#!/usr/bin/python3

"""WMI variables"""


from __future__ import annotations
from dataclasses import dataclass
from struct import Struct
from typing import Final, Optional, Iterable
from .data import mof_parse_data, mof_parse_string
from .qualifier import Qualifier
from .type import Type


VARIABLE_HEADER: Final = Struct("<II4xII")  # TODO Unknown values
QUALIFIER_BUFFER_HEADER: Final = Struct("<II")
QUALIFIER_HEADER: Final = Struct("<I")


VALUE_LENGTH_PLACEHOLDER: Final = 0xFFFFFFFF


def parse_qualifiers(buffer: memoryview, offset: int) -> Iterable[Qualifier]:
    """Parse variable qualifiers"""
    length, count = QUALIFIER_BUFFER_HEADER.unpack(
        buffer[:QUALIFIER_BUFFER_HEADER.size]
    )
    if len(buffer) != length:
        raise ValueError(f"Variable qualifiers length {length} does not match")

    info_buffer = buffer[QUALIFIER_BUFFER_HEADER.size:]
    info_offset = 0
    for _ in range(count):
        # The length is part of the qualifier itself, so we have
        # to pass the whole buffer including the length to
        # Qualifier.from_buffer()
        qualifier_length, = QUALIFIER_HEADER.unpack(
            info_buffer[info_offset:info_offset + QUALIFIER_HEADER.size]
        )
        yield Qualifier.from_buffer(
            info_buffer[info_offset:info_offset + qualifier_length],
            offset + QUALIFIER_BUFFER_HEADER.size + info_offset
        )
        info_offset += qualifier_length


@dataclass(frozen=True, slots=True)
class Variable:
    """WMI variable"""

    name: str

    data_type: Type

    value: Optional[bool | int | str]

    qualifiers: list[Qualifier]

    @classmethod
    def from_buffer(cls, buffer: memoryview, offset: int) -> Variable:
        """Parse variable from buffer"""
        length, data_type, value_length, info_length = VARIABLE_HEADER.unpack(
            buffer[:VARIABLE_HEADER.size]
        )
        if len(buffer) != length:
            raise ValueError(f"Variable length {length} does not match")

        if info_length > length:
            raise ValueError(f"Variable info length {info_length} too big")

        data_type = Type.from_int(data_type)
        info_buffer = buffer[VARIABLE_HEADER.size:VARIABLE_HEADER.size + info_length]
        if value_length == VALUE_LENGTH_PLACEHOLDER:
            data = None
        else:
            if value_length >= info_length:
                raise ValueError(f"Variable value length {value_length} too big")

            data = mof_parse_data(
                data_type,
                info_buffer[:value_length]
            )
            info_buffer = info_buffer[value_length:]

        name = mof_parse_string(info_buffer)
        qualifiers = list(parse_qualifiers(
            buffer[VARIABLE_HEADER.size + info_length:],
            offset + VARIABLE_HEADER.size + info_length
        ))

        return cls(
            name=name,
            data_type=data_type,
            value=data,
            qualifiers=qualifiers
        )
