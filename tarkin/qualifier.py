#!/usr/bin/python3

"""WMI Qualifier"""


from __future__ import annotations
from dataclasses import dataclass
from typing import Final
from construct import Struct, Int32ul, Prefixed, PrefixedArray, this, Padding, PascalString, Adapter, Container, Tell, Terminated
from .data import NullStripAdapter, MOF_DATA
from .type import Type, MOF_DATA_TYPE


@dataclass(frozen=True, slots=True)
class Qualifier:
    """WMI qualifier"""

    name: str

    data_type: Type

    value: bool | int | str

    offset: int

    @classmethod
    def from_container(cls, container: Container) -> Qualifier:
        """Parse qualifier from container"""
        return cls(
            name=container["qualifier"]["name"],
            data_type=container["qualifier"]["data_type"],
            value=container["qualifier"]["value"],
            offset=int(container["offset"])
        )


class QualifiersAdapter(Adapter):
    """Adapter for converting an container into a list of qualifiers"""
    def _decode(self, obj: Container, context: object, path: object) -> list[Qualifier]:
        """Decode integer to MOF data type"""
        return [Qualifier.from_container(entry) for entry in obj["array"]]

    def _encode(self, obj: list[Qualifier], context: object, path: object) -> Container:
        """Encode MOF data type to integer"""
        return dict(
            entries=[dict(
                data_type=qualifier.data_type,
                name=qualifier.name,
                value=qualifier.value
            ) for qualifier in obj]
        )


MOF_QUALIFIERS: Final = QualifiersAdapter(
    Prefixed(
        Int32ul,
        Struct(
            "array" / PrefixedArray(
                Int32ul,
                Struct(
                    "offset" / Tell,
                    "qualifier" / Prefixed(
                        Int32ul,
                        Struct(
                            "data_type" / MOF_DATA_TYPE,
                            "unknown" / Padding(4),     # TODO: Unknown value
                            "name" / NullStripAdapter(PascalString(Int32ul, "utf-16-le")),
                            "value" / MOF_DATA(this.data_type),
                            Terminated
                        ),
                        includelength=True
                    )
                )
            ),
            Terminated
        ),
        includelength=True
    )
)
