#!/usr/bin/python3

"""Test for Doublespace decompression"""

from pathlib import Path
from typing import Final
from unittest import TestCase
from construct import GreedyBytes
from tarkin.ds import CompressedDS

COMPRESSED_PATH: Final = Path("tests/compression/compressed.bin")
DECOMPRESSED_PATH: Final = Path("tests/compression/decompressed.bin")

class DsTest(TestCase):
    """Tests for doublespace decompression"""

    def test_decompression(self) -> None:
        """Test decompression of compressed data"""
        decompressed = DECOMPRESSED_PATH.read_bytes()

        ds = CompressedDS(GreedyBytes, len(decompressed))
        result = ds.parse_file(COMPRESSED_PATH)

        self.assertEqual(result, decompressed)

    def test_compression(self) -> None:
        """Test compression of binary data"""
        decompressed = DECOMPRESSED_PATH.read_bytes()
        ds = CompressedDS(GreedyBytes, 0)

        with self.assertRaises(NotImplementedError):
            ds.build(decompressed)

    def test_length_mismatch(self) -> None:
        """Test if a mismatched length causes an error"""
        length = DECOMPRESSED_PATH.stat().st_size

        ds = CompressedDS(GreedyBytes, length + 1)

        with self.assertRaises(RuntimeError):
            ds.parse_file(COMPRESSED_PATH)

    def test_os_error(self) -> None:
        """Test if a library error results in an OSError"""
        ds = CompressedDS(GreedyBytes, 0)
        data = bytes()

        with self.assertRaises(OSError):
            ds.parse(data)
