#!/usr/bin/python3

"""Test for qualifier flavor parsing and building"""

from typing import Final
import pytest
from construct import ConstError, StreamError, ValidationError
from tarkin.flavor import BMOF_FLAVORS, QualifierFlavor, Flavors


# Section with no qualifier flavors
EMPTY_SECTION: Final = bytes.fromhex(
    (
        "42 4D 4F 46 51 55 41 4C 46 4C 41 56 4F 52 31 31"   # Magic number
        "00 00 00 00"   # No qualifiers
    )
)

# Section with a single qualifier
SINGLE_FLAVOR: Final = bytes.fromhex(
    (
        "42 4D 4F 46 51 55 41 4C 46 4C 41 56 4F 52 31 31"   # Magic number
        "01 00 00 00"   # One qualifier
        "EF BE AD DE"   # Offset 0xdeadbeef
        "03 00 00 00"   # Flags ToInstance and ToSubclass
    )
)

# Parsing result of SINGLE_FLAVOR
SINGLE_FLAVOR_RESULT: Final = [
    QualifierFlavor(
        offset=0xdeadbeef,
        flavors=Flavors.TO_INSTANCE | Flavors.TO_SUBCLASS
    )
]

# Section with two qualifier flavors
MULTIPLE_FLAVORS: Final = bytes.fromhex(
    (
        "42 4D 4F 46 51 55 41 4C 46 4C 41 56 4F 52 31 31"   # Magic number
        "02 00 00 00"   # Two qualifiers
        "EF BE AD DE"   # Offset 0xdeadbeef
        "03 00 00 00"   # Flags ToInstance and ToSubclass
        "33 22 11 00"   # Offset 0x00112233
        "00 00 00 00"   # No flags
    )
)

# Parsing result of MULTIPLE_FLAVOR
MULTIPLE_FLAVORS_RESULT: Final = [
    QualifierFlavor(
        offset=0xdeadbeef,
        flavors=Flavors.TO_INSTANCE | Flavors.TO_SUBCLASS
    ),
    QualifierFlavor(
        offset=0x00112233,
        flavors=0
    )
]

# Section with a invalid qualifier flavor
NULL_FLAVOR: Final = bytes.fromhex(
    (
        "42 4D 4F 46 51 55 41 4C 46 4C 41 56 4F 52 31 31"   # Magic number
        "01 00 00 00"   # One qualifier
        "00 00 00 00"   # Offset 0x00000000 (invalid)
        "03 00 00 00"   # Flags ToInstance and ToSubclass
    )
)

# Section with a incomplete qualifier flavor
INCOMPLETE_FLAVOR: Final = bytes.fromhex(
    (
        "42 4D 4F 46 51 55 41 4C 46 4C 41 56 4F 52 31 31"   # Magic number
        "01 00 00 00"   # One qualifier
        "EF BE AD DE"   # Offset 0xdeadbeef (flags missing)
    )
)

# Section with a missing qualifier flavor
MISSING_FLAVOR: Final = bytes.fromhex(
    (
        "42 4D 4F 46 51 55 41 4C 46 4C 41 56 4F 52 31 31"   # Magic number
        "01 00 00 00"   # One qualifier (missing)
    )
)

# Section with a invalid magic number
INVALID_MAGIC: Final = bytes.fromhex(
    (
        "42 4D 4F 46 51 55 41 4C 46 4C 41 56 4F 52 FF FF"   # Magic number (invalid)
        "01 00 00 00"   # No qualifiers
    )
)


@pytest.mark.parametrize(
    "data,expected",
    [
        pytest.param(EMPTY_SECTION, [], id="empty"),
        pytest.param(SINGLE_FLAVOR, SINGLE_FLAVOR_RESULT, id="single"),
        pytest.param(MULTIPLE_FLAVORS, MULTIPLE_FLAVORS_RESULT, id="multiple")
    ]
)
def test_parsing(data: bytes, expected: list[QualifierFlavor]) -> None:
    """Test parsing of qualifier flavors"""

    assert BMOF_FLAVORS.parse(data) == expected


def test_parse_null_flavor() -> None:
    """Test parsing of a qualifier flavor with a zero offset"""

    with pytest.raises(ValidationError):
        BMOF_FLAVORS.parse(NULL_FLAVOR)


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(INCOMPLETE_FLAVOR, id="incomplete"),
        pytest.param(MISSING_FLAVOR, id="missing")
    ]
)
def test_parsing_missing_data(data: bytes) -> None:
    """Test error handling when trying to parse missing data"""

    with pytest.raises(StreamError):
        BMOF_FLAVORS.parse(data)


def test_parse_invalid_magic() -> None:
    """Test parsing of a section with an invalid magic number"""

    with pytest.raises(ConstError):
        BMOF_FLAVORS.parse(INVALID_MAGIC)


@pytest.mark.parametrize(
    "flavors,expected",
    [
        pytest.param([], EMPTY_SECTION, id="empty"),
        pytest.param(SINGLE_FLAVOR_RESULT, SINGLE_FLAVOR, id="single"),
        pytest.param(MULTIPLE_FLAVORS_RESULT, MULTIPLE_FLAVORS, id="multiple")
    ]
)
def test_building(flavors: list[QualifierFlavor], expected: bytes) -> None:
    """Test building of qualifier flavors"""
    assert BMOF_FLAVORS.build(flavors) == expected
