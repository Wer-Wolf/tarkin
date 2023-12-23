#!/usr/bin/python3

"""Basic binary MOF structure"""


from __future__ import annotations
from dataclasses import dataclass
from struct import Struct
from typing import Final
from .decompress import ds_decompress
from .root import BmofRoot


CONTAINER_HEADER: Final = Struct('<4s3I')


@dataclass(frozen=True, slots=True)
class Bmof:
    """Basic binary MOF structure"""

    version: int

    root: BmofRoot

    @classmethod
    def from_buffer(cls, buffer: memoryview) -> Bmof:
        """Unpack binary MOF data"""
        magic, version, compressed, decompressed = CONTAINER_HEADER.unpack(buffer)
        if magic != b'BMOF':
            raise ValueError(f"File magic {magic} does not match")

        if len(buffer) - CONTAINER_HEADER.size != compressed:
            raise ValueError(f"Compressed size {compressed} does not match buffer size")

        data = bytearray(decompressed)
        ds_decompress(memoryview(buffer[CONTAINER_HEADER.size - 1:]), data)

        return cls(
            version=version,
            root=BmofRoot.from_buffer(data)
        )
