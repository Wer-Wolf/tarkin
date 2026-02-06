#!/usr/bin/python3

"""Test for Doublespace decompression"""

from pathlib import Path
from typing import Final
import pytest
from construct import GreedyBytes
from tarkin.ds import CompressedDS

COMPRESSED_PATH: Final = Path("tests/compression/compressed.bin")
DECOMPRESSED_PATH: Final = Path("tests/compression/decompressed.bin")


def test_decompression() -> None:
    """Test decompression of compressed data"""
    decompressed = DECOMPRESSED_PATH.read_bytes()
    ds = CompressedDS(GreedyBytes, len(decompressed))

    assert ds.parse_file(COMPRESSED_PATH) == decompressed


def test_compression() -> None:
    """Test compression of binary data"""
    decompressed = DECOMPRESSED_PATH.read_bytes()
    ds = CompressedDS(GreedyBytes, 0)

    with pytest.raises(NotImplementedError):
        ds.build(decompressed)


def test_length_mismatch() -> None:
    """Test if a mismatched length causes an error"""
    length = DECOMPRESSED_PATH.stat().st_size
    ds = CompressedDS(GreedyBytes, length + 1)

    with pytest.raises(RuntimeError):
        ds.parse_file(COMPRESSED_PATH)


def test_os_error() -> None:
    """Test if a library error results in an OSError"""
    ds = CompressedDS(GreedyBytes, 0)
    data = bytes()

    with pytest.raises(OSError):
        ds.parse(data)
