#!/usr/bin/python3

"""Binary MOF parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final, Optional as TOptional
from construct import Struct, Int32ul, Const, this, Container, Adapter, Rebuild, len_, \
    Terminated, FixedSized, Optional
from .ds import CompressedDS
from .flavor import BMOF_FLAVORS, QualifierFlavor
from .root import BMOF_ROOT, Root


@dataclass(frozen=True, slots=True)
class Bmof:
    """Binary MOF"""

    root: Root

    flavors: TOptional[list[QualifierFlavor]]

    @classmethod
    def from_container(cls, container: Container) -> Bmof:
        """Parse BMOF from container"""
        return cls(
            root=container["data"]["root"],
            flavors=container["data"]["flavors"]
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
            data=Container(
                root=obj.root,
                flavors=obj.flavors
            )
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
                Struct(
                    "root" / BMOF_ROOT,
                    "flavors" / Optional(BMOF_FLAVORS),
                    Terminated
                ),
                this.final_length
            )
        ),
        Terminated
    )
)
"""
The basic structure of a BMOF data buffer.

The BMOF data buffer starts with a fixed header containing the following fields:
 - A 4-byte magic constant ("FOMB")
 - A 32-bit little endian version field (currently only version 1 is supported)
 - A 32-bit little endian length field specifying the length of the compressed BMOF data in bytes
 - A 32-bit little endian length field specifying the length of the decompressed BMOF data in bytes

The BMOF data following the this header is compressed using the DoubleSpace compression algorithm
and contains the BMOF root structure and an optional flavors section.
"""
