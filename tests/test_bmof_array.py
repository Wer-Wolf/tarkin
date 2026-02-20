#!/usr/bin/python3

"""Test for BMOF array parsing and building"""

from typing import Final
from construct import StreamError, Int32ul
import pytest
from tarkin.constructs import BmofArray


# BMOF array with zero items
EMPTY_ARRAY: Final = bytes.fromhex(
    (
        "08 00 00 00"   # 8 bytes for the header
        "00 00 00 00"   # Zero items inside array
    )
)

# BMOF array with a single entry
SINGLE_ARRAY: Final = bytes.fromhex(
    (
        "0C 00 00 00"   # 8 bytes for the header + 4 bytes for the item
        "01 00 00 00"   # Single item inside array
        "EF BE AD DE"   # 32-bit item (0xdeadbeef)
    )
)

# Parsing result of SINGLE_ARRAY
SINGLE_ARRAY_RESULT: Final = [
    0xdeadbeef
]

# BMOF array with multiple entries
MULTIPLE_ARRAY: Final = bytes.fromhex(
    (
        "10 00 00 00"   # 8 bytes for the header + 8 bytes for the items
        "02 00 00 00"   # Two items inside array
        "EF BE AD DE"   # 32-bit item (0xdeadbeef)
        "AB AB AB AB"   # 32-bit item (0xabababab)
    )
)

# Parsing result of SINGLE_ARRAY
MULTIPLE_ARRAY_RESULT: Final = [
    0xdeadbeef,
    0xabababab
]

# BMOF array with a missing item count
INCOMPLETE_ARRAY: Final = bytes.fromhex(
    (
        "04 00 00 00"   # 4 bytes for the header without the item count
    )
)

# BMOF array with a size of zero
ZERO_SIZED_ARRAY: Final = bytes.fromhex(
    (
        "00 00 00 00"
    )
)

# BMOF array with too many items
OVERSIZED_ARRAY: Final = bytes.fromhex(
    (
        "0C 00 00 00"   # 8 bytes for the header + 4 bytes for the first item
        "02 00 00 00"   # Two items inside array
        "EF BE AD DE"   # 32-bit item (0xdeadbeef)
        "AB AB AB AB"   # 32-bit item (0xabababab)
    )
)

# BMOF array with too few items
UNDERSIZED_ARRAY: Final = bytes.fromhex(
    (
        "10 00 00 00"   # 8 bytes for the header + 8 bytes for both items
        "01 00 00 00"   # Single item inside array
        "EF BE AD DE"   # 32-bit item (0xdeadbeef)
        "AB AB AB AB"   # 32-bit item (0xabababab)
    )
)


@pytest.mark.parametrize(
    "data,expected",
    [
        pytest.param(EMPTY_ARRAY, [], id="empty"),
        pytest.param(SINGLE_ARRAY, SINGLE_ARRAY_RESULT, id="single"),
        pytest.param(MULTIPLE_ARRAY, MULTIPLE_ARRAY_RESULT, id="multiple"),
        pytest.param(UNDERSIZED_ARRAY, SINGLE_ARRAY_RESULT, id="undersized")
    ]
)
def test_parsing(data: bytes, expected: list[int]) -> None:
    """Test parsing of BMOF arrays"""

    assert BmofArray(Int32ul).parse(data) == expected


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(INCOMPLETE_ARRAY, id="countless"),
        pytest.param(ZERO_SIZED_ARRAY, id="zero_sized"),
        pytest.param(bytes(), id="no_data"),
        pytest.param(OVERSIZED_ARRAY, id="oversized")
    ]
)
def test_parsing_missing_data(data: bytes) -> None:
    """Test error handling when trying to parse missing data"""

    with pytest.raises(StreamError):
        BmofArray(Int32ul).parse(data)


@pytest.mark.parametrize(
    "array,expected",
    [
        pytest.param([], EMPTY_ARRAY, id="empty"),
        pytest.param(SINGLE_ARRAY_RESULT, SINGLE_ARRAY, id="single"),
        pytest.param(MULTIPLE_ARRAY_RESULT, MULTIPLE_ARRAY, id="multiple")
    ]
)
def test_building(array: list[int], expected: bytes) -> None:
    """Test building of BMOF arrays"""
    assert BmofArray(Int32ul).build(array) == expected
