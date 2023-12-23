#!/usr/bin/python3

"""Qualifier flavor"""


from __future__ import annotations
from dataclasses import dataclass
from enum import IntFlag, unique, STRICT
from struct import Struct
from typing import Final, Iterable

FLAVOR_HEADER: Final = Struct('<16sI')
FLAVOR_DATA: Final = Struct('2I')


@unique
class Flavors(IntFlag, boundary=STRICT):
    """Additional flavors for qualifiers"""
    TO_INSTANCE = 1 << 0
    TO_SUBCLASS = 1 << 1
    DISABLE_OVERRIDE = 1 << 4
    AMENDED = 1 << 7


def flavors_from_buffer(buffer: memoryview) -> Iterable[QualifierFlavor]:
    """Parse qualifier flavors from buffer"""
    magic, count = FLAVOR_HEADER.unpack(buffer[:FLAVOR_HEADER.size])
    if magic != b"BMOFQUALFLAVOR11":
        raise ValueError(f"Invalid flavor magic header: {magic}")

    flavors = buffer[FLAVOR_HEADER.size:]
    if len(flavors) != count * FLAVOR_DATA.size:
        raise ValueError(f"Wrong flavor count: {count}")

    for i in range(count):
        offset = i * FLAVOR_DATA.size
        yield QualifierFlavor.from_buffer(
            flavors[offset:offset + FLAVOR_DATA.size]
        )


@dataclass(frozen=True, slots=True)
class QualifierFlavor:
    """Qualifier flavor"""

    offset: int

    to_instance: bool

    to_subclass: bool

    disable_override: bool

    amended: bool

    @classmethod
    def from_buffer(cls, buffer: memoryview) -> QualifierFlavor:
        """Parse single qualifier flavor"""
        offset, flags = FLAVOR_DATA.unpack(buffer)
        if offset == 0:
            raise ValueError(f"Invalid flavor offset {offset}")

        flavors = Flavors(flags)

        return cls(
            offset=offset,
            to_instance=bool(flavors & Flavors.TO_INSTANCE),
            to_subclass=bool(flavors & Flavors.TO_SUBCLASS),
            disable_override=bool(flavors & Flavors.DISABLE_OVERRIDE),
            amended=bool(flavors & Flavors.AMENDED)
        )
