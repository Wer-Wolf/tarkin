#!/usr/bin/python3

"""Doublespace decompression"""

from __future__ import annotations
from typing import override
from doublespace import decompress
from construct import Container, Tunnel, Construct, Path, evaluate


class CompressedDS(Tunnel):
    """
    Adapter for converting an doublespace-compressed container.

    See https://github.com/Wer-Wolf/libdeds for details.
    """
    def __init__(self, subcon: Construct, length: Path):
        super().__init__(subcon)
        self.subcon = subcon
        self.length = length

    @override
    def _decode(self, data: bytes, context: Container, _path: str) -> bytes:
        """Doublespace decompression"""
        length: int = evaluate(self.length, context)
        buffer = bytearray(length)

        decompress(data, buffer)

        return buffer

    @override
    def _encode(self, data: bytes, context: Container, _path: str) -> bytes:
        """Doublespace compression"""
        raise NotImplementedError("Doublespace compression not implemented")
