#!/usr/bin/python3

"""Tests for BMOF root parsing"""

from typing import Final
from construct import ConstructError
import pytest
from tarkin.root import BMOF_ROOT, Root
from tarkin.wmi_object import WmiObject, WmiObjectType

# BMOF root with no entries
SIMPLE_ROOT: Final = bytes.fromhex(
    (
        "46 4F 4D 42"   # Magic ("FOMB")
        "14 00 00 00"   # Length (20 bytes)
        "01 00 00 00"   # Unknown constant (1)
        "01 00 00 00"   # Unknown constant (1)
        "00 00 00 00"   # Number of entries (0)
    )
)

# Parsing result of SIMPLE_ROOT
SIMPLE_ROOT_RESULT: Final = Root(
    objects=[]
)

# BMOF root with entris
POPULATED_ROOT: Final = bytes.fromhex(
    (
        "46 4F 4D 42"   # Magic ("FOMB")
        "28 00 00 00"   # Length (40 bytes)
        "01 00 00 00"   # Unknown constant (1)
        "01 00 00 00"   # Unknown constant (1)
        "01 00 00 00"   # Number of entries (1)

        "14 00 00 00"   # Object length (20 bytes)
        "FF FF FF FF"   # Object qualifiers offset (placeholder)
        "FF FF FF FF"   # Object properties offset (placeholder)
        "FF FF FF FF"   # Object methods offset (placeholder)
        "00 00 00 00"   # Object type (class)
    )
)

# Parsing result of POPULATED_ROOT
POPULATED_ROOT_RESULT: Final = Root(
    objects=[
        WmiObject(
            object_type=WmiObjectType.CLASS,
            qualifiers=None,
            properties=None,
            methods=None
        )
    ]
)

# BMOF root with an invalid magic value
INVALID_MAGIC_ROOT: Final = bytes.fromhex(
    (
        "DE AD BE EF"   # Bogus magic
        "14 00 00 00"   # Length (20 bytes)
        "01 00 00 00"   # Unknown constant (1)
        "01 00 00 00"   # Unknown constant (1)
        "00 00 00 00"   # Number of entries (0)
    )
)

# Oversized BMOF root
OVERSIZED_ROOT: Final = bytes.fromhex(
    (
        "46 4F 4D 42"   # Magic ("FOMB")
        "15 00 00 00"   # Length (20 bytes + 1 byte)
        "01 00 00 00"   # Unknown constant (1)
        "01 00 00 00"   # Unknown constant (1)
        "00 00 00 00"   # Number of entries (0)
    )
)

# Undersized BMOF root
UNDERSIZED_ROOT: Final = bytes.fromhex(
    (
        "46 4F 4D 42"   # Magic ("FOMB")
        "13 00 00 00"   # Length (19 bytes, one byte is missing)
        "01 00 00 00"   # Unknown constant (1)
        "01 00 00 00"   # Unknown constant (1)
        "00 00 00 00"   # Number of entries (0)
    )
)

# BMOF root with an invalid first constant
INVALID_FIRST_CONSTANT_ROOT: Final = bytes.fromhex(
    (
        "46 4F 4D 42"   # Magic ("FOMB")
        "14 00 00 00"   # Length (20 bytes)
        "DE ED BE EF"   # Bogus constant
        "01 00 00 00"   # Unknown constant (1)
        "00 00 00 00"   # Number of entries (0)
    )
)

# BMOF root with an invalid second constant
INVALID_SECOND_CONSTANT_ROOT: Final = bytes.fromhex(
    (
        "46 4F 4D 42"   # Magic ("FOMB")
        "14 00 00 00"   # Length (20 bytes)
        "01 00 00 00"   # Unknown constant (1)
        "DE ED BE EF"   # Bogus constant
        "00 00 00 00"   # Number of entries (0)
    )
)

# BMOF root with an invalid entry count
INVALID_COUNT_ROOT: Final = bytes.fromhex(
    (
        "46 4F 4D 42"   # Magic ("FOMB")
        "14 00 00 00"   # Length (20 bytes)
        "01 00 00 00"   # Unknown constant (1)
        "01 00 00 00"   # Unknown constant (1)
        "FF 00 00 00"   # Number of entries (255, too large)
    )
)


@pytest.mark.parametrize(
    "data,expected",
    [
        pytest.param(SIMPLE_ROOT, SIMPLE_ROOT_RESULT, id="simple"),
        pytest.param(POPULATED_ROOT, POPULATED_ROOT_RESULT, id="populated"),
    ]
)
def test_parsing(data: bytes, expected: list[WmiObject]) -> None:
    """Test parsing of BMOF roots"""

    assert BMOF_ROOT.parse(data) == expected


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(INVALID_MAGIC_ROOT, id="invalid_magic"),
        pytest.param(OVERSIZED_ROOT, id="oversized"),
        pytest.param(UNDERSIZED_ROOT, id="undersized"),
        pytest.param(INVALID_FIRST_CONSTANT_ROOT, id="invalid_first_constant"),
        pytest.param(INVALID_SECOND_CONSTANT_ROOT, id="invalid_second_constant"),
        pytest.param(INVALID_COUNT_ROOT, id="invalid_count"),
    ]
)
def test_parsing_invalid(data: bytes) -> None:
    """Test error handling when trying to parse malformed BMOF roots"""

    with pytest.raises(ConstructError):
        BMOF_ROOT.parse(data)
