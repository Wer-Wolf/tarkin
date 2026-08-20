#!/usr/bin/python3

"""Test for BMOF heap reference parsing and building"""

from typing import Final
from construct import Int32ul
from tarkin.constructs import BmofHeapReference


# single item at offset 0x04
TEST_DATA: Final = bytes.fromhex(
    (
        "00 00 00 00"   # Bogus data
        "EF BE AD DE"   # 32-bit item (0xdeadbeef)
    )
)

# Parsing result of TEST_DATA
TEST_DATA_RESULT: Final = 0xdeadbeef


def test_parsing() -> None:
    """Test parsing of heap references"""
    assert BmofHeapReference(lambda _: 0x04, Int32ul).parse(TEST_DATA) == TEST_DATA_RESULT


def test_parsing_special_offset() -> None:
    """Test parsing of special 0xFFFFFFFF heap references"""
    assert BmofHeapReference(lambda _: 0xFFFFFFFF, Int32ul).parse(TEST_DATA) is None


def test_building() -> None:
    """Test building of heap references"""
    assert BmofHeapReference(lambda _: 0x04, Int32ul).build(TEST_DATA_RESULT) == TEST_DATA


def test_building_special_offset() -> None:
    """Test building of special 0xFFFFFFFF heap references"""
    assert BmofHeapReference(lambda _: 0xFFFFFFFF, Int32ul).build(TEST_DATA_RESULT) == b''
