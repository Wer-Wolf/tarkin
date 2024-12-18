#!/usr/bin/python3

"""Binary MOF parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final
from construct import Struct, Int32ul, Const, this, Container, Adapter, Rebuild, len_, \
    Terminated, GreedyBytes, FixedSized
from .ds import CompressedDS


@dataclass(frozen=True, slots=True)
class Bmof:
    """Binary MOF"""

    data: bytes

    @classmethod
    def from_container(cls, container: Container) -> Bmof:
        """Parse BMOF from container"""
        return cls(
            data=bytes(container["data"]),
        )


class BmofAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into a Bmof class"""
    def _decode(self, obj: Container, context: Container, path: str) -> Bmof:
        """Decode container to BMOF class"""
        return Bmof.from_container(obj)

    def _encode(self, obj: Bmof, context: Container, path: str) -> Container:
        """Encode Bmof class to container"""
        return Container(
            final_length=len(obj.data),
            data=obj.data
        )


BMOF: Final = BmofAdapter(
    Struct(
        "magic" / Const(b"FOMB"),
        "version" / Const(1, Int32ul),
        "compressed_length" / Rebuild(Int32ul, len_(this.data)),
        "final_length" / Int32ul,
        "data" / FixedSized(
            this.compressed_length,
            CompressedDS(
                GreedyBytes,
                this.final_length
            )
        ),
        Terminated
    )
)
