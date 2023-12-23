#!/usr/bin/python3

"""Decompress binary MOF data"""

from __future__ import annotations
from ctypes import CDLL, c_void_p, c_size_t
from typing import Final


LIB: Final = CDLL('libdeds.so')
FUNC: Final = LIB.ds_decompress
FUNC.argtypes = [c_void_p, c_size_t, c_void_p, c_size_t]


def ds_decompress(data: bytearray, buffer: bytearray) -> None:
    """Decompress BMOF data"""
    result: int = LIB.ds_decompress(data, len(data), buffer, len(buffer))
    if result < 0:
        raise OSError(-result, "Failed to decompress data")
