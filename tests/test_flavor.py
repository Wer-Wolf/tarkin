#!/usr/bin/python3

"""Test for qualifier flavor parsing and building"""

from typing import Final
from unittest import TestCase
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
        offset = 0xdeadbeef,
        flavors = Flavors.TO_INSTANCE | Flavors.TO_SUBCLASS
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
        offset = 0xdeadbeef,
        flavors = Flavors.TO_INSTANCE | Flavors.TO_SUBCLASS
    ),
    QualifierFlavor(
        offset = 0x00112233,
        flavors = 0
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

class FlavorTest(TestCase):
    """Tests for qualifier flavor parsing"""

    def test_parse_empty_section(self) -> None:
        """Test parsing of a section with no qualifier flavors"""

        result: list[QualifierFlavor] = BMOF_FLAVORS.parse(EMPTY_SECTION)

        self.assertEqual(len(result), 0)

    def test_build_empty_section(self) -> None:
        """Test building of a section with no qualifier flavors"""

        result: bytes = BMOF_FLAVORS.build([])

        self.assertEqual(result, EMPTY_SECTION)

    def test_parse_single_flavor(self) -> None:
        """Test parsing of a section with a single qualifier flavor"""

        result: list[QualifierFlavor] = BMOF_FLAVORS.parse(SINGLE_FLAVOR)

        self.assertEqual(result, SINGLE_FLAVOR_RESULT)

    def test_build_single_flavor(self) -> None:
        """Test building of a section with a single qualifier flavor"""

        result: bytes = BMOF_FLAVORS.build(SINGLE_FLAVOR_RESULT)

        self.assertEqual(result, SINGLE_FLAVOR)


    def test_parse_multiple_flavors(self) -> None:
        """Test parsing of a section with multiple qualifier flavors"""

        result: list[QualifierFlavor] = BMOF_FLAVORS.parse(MULTIPLE_FLAVORS)

        self.assertEqual(result, MULTIPLE_FLAVORS_RESULT)

    def test_build_multiple_flavors(self) -> None:
        """Test building of a section with multiple qualifier flavors"""

        result: bytes = BMOF_FLAVORS.build(MULTIPLE_FLAVORS_RESULT)

        self.assertEqual(result, MULTIPLE_FLAVORS)

    def test_parse_null_flavor(self) -> None:
        """Test parsing of a qualifier flavor with a zero offset"""

        with self.assertRaises(ValidationError):
            BMOF_FLAVORS.parse(NULL_FLAVOR)

    def test_parse_incomplete_flavor(self) -> None:
        """Test parsing of a incomplete qualifier flavor"""

        with self.assertRaises(StreamError):
            BMOF_FLAVORS.parse(INCOMPLETE_FLAVOR)

    def test_parse_mssing_flavor(self) -> None:
        """Test parsing of a missing qualifier flavor"""

        with self.assertRaises(StreamError):
            BMOF_FLAVORS.parse(MISSING_FLAVOR)

    def test_parse_invalid_magic(self) -> None:
        """Test parsing of a section with an invalid magic number"""

        with self.assertRaises(ConstError):
            BMOF_FLAVORS.parse(INVALID_MAGIC)
