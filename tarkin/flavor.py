#!/usr/bin/python3

"""Qualifier flavor"""


from __future__ import annotations
from dataclasses import dataclass
from enum import IntFlag, unique, STRICT
from typing import Final
from construct import Struct, Const, Int32ul, PrefixedArray, Container, NoneOf, Adapter


@unique
class Flavors(IntFlag, boundary=STRICT):
    """Additional flavors for qualifiers"""
    TO_INSTANCE = 1 << 0
    TO_SUBCLASS = 1 << 1
    DISABLE_OVERRIDE = 1 << 4
    AMENDED = 1 << 7


@dataclass(frozen=True, slots=True)
class QualifierFlavor():
    """Qualifier flavor"""

    offset: int

    flavors: Flavors

    @classmethod
    def from_container(cls, container: Container) -> QualifierFlavor:
        """Parse qualifier flavor from container"""
        return cls(
            offset=container["offset"],
            flavors=Flavors(container["flavors"])
        )


class FlavorsAdpater(Adapter):
    """Adapter for converting an container into a list of qualifier flavors"""
    def _decode(self, obj: PrefixedArray, context: object, path: object) -> list[QualifierFlavor]:
        """Decode container to qualifier flavors"""
        return [QualifierFlavor.from_container(entry) for entry in obj["entries"]]

    def _encode(self, obj: list[QualifierFlavor], context: object, path: object) -> Struct:
        """Encode qualifier flavors in an object"""
        return dict(
            entries=[dict(offset=q.offset, flavors=int(q.flavors)) for q in obj]
        )


MOF_FLAVORS: Final = FlavorsAdpater(
    Struct(
        "magic" / Const(b"BMOFQUALFLAVOR11"),
        "entries" / PrefixedArray(
            Int32ul,
            Struct(
                "offset" / NoneOf(Int32ul, {0}),
                "flavors" / Int32ul,    # TODO Enum validator?
            )
        )
    )
)
