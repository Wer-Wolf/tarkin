#!/usr/bin/python3

"""Doublespace decompression"""

from __future__ import annotations
from ctypes import CDLL, c_size_t, c_int, byref, POINTER, c_ubyte
from os import strerror
from typing import Final
from construct import Container, Tunnel, Construct, Path, evaluate


LIB: Final = CDLL("libdeds.so")
LIB.ds_decompress.argtypes = [
    POINTER(c_ubyte),
    c_size_t,
    POINTER(c_ubyte),
    c_size_t,
    POINTER(c_size_t)
]
LIB.ds_decompress.restype = c_int


class CompressedDS(Tunnel):
    """Adapter for converting an doublespace-compressed container"""
    def __init__(self, subcon: Construct, length: Path):
        super().__init__(subcon)
        self.subcon = subcon
        self.length = length

    def _decode(self, data: bytes, context: Container, path: str):
        """Doublespace decompression"""
        length: int = evaluate(self.length, context)
        buffer = bytearray(length)

        input_data = (c_ubyte * len(data)).from_buffer_copy(data)
        output_data = (c_ubyte * length).from_buffer(buffer)
        result_length = c_size_t()

        ret: int = LIB.ds_decompress(
            input_data,
            len(data),
            output_data,
            len(output_data),
            byref(result_length)
        )
        if ret < 0:
            raise OSError(-ret, strerror(-ret))

        if result_length.value != length:
            raise RuntimeError("Doublespace compression did not consume all data")

        return buffer

    def _encode(self, data: bytes, context: Container, path: str):
        """Doublespace compression"""
        raise NotImplementedError("Doublespace compression not implemented")
