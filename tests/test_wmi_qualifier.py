#!/usr/bin/python3

"""Tests for WMI qualifier parsing"""

from typing import Final
from construct import ConstructError
import pytest
from tarkin.wmi_qualifier import BMOF_WMI_QUALIFIER, WmiQualifier
from tarkin.wmi_type import WmiType, WmiDataType


# WMI qualifier with no additional data
SIMPLE_QUALIFIER: Final = bytes.fromhex(
    (
        "10 00 00 00"   # Length (16 bytes)
        "08 00 00 00"   # Data type (string)
        "FF FF FF FF"   # Name offset (placeholder)
        "FF FF FF FF"   # Value offset (placeholder)
    )
)

# Parsing result of SIMPLE_QUALIFIER
SIMPLE_QUALIFIER_RESULT: Final = WmiQualifier(
    data_type=WmiType(WmiDataType.STRING, False),
    name=None,
    value=None,
    offset=0
)

# Named WMI qualifier
NAMED_QUALIFIER: Final = bytes.fromhex(
    (
        "1A 00 00 00"   # Length (26 bytes)
        "08 00 00 00"   # Data type (string)
        "00 00 00 00"   # Name offset (0)
        "FF FF FF FF"   # Value offset (placeholder)
        "54 00 45 00"   # Null-teminated name string ("TEST")
        "53 00 54 00"
        "00 00"
    )
)

# Parsing result of NAMED_QUALIFIER
NAMED_QUALIFIER_RESULT: Final = WmiQualifier(
    data_type=WmiType(WmiDataType.STRING, False),
    name="TEST",
    value=None,
    offset=0
)

# WMI qualifier with a value
VALUE_QUALIFIER: Final = bytes.fromhex(
    (
        "12 00 00 00"   # Length (18 bytes)
        "0B 00 00 00"   # Data type (boolean)
        "FF FF FF FF"   # Name offset (placeholder)
        "00 00 00 00"   # Value offset (0)
        "FF FF"         # Boolean value (True)
    )
)

# Parsing result of VALUE_QUALIFIER
VALUE_QUALIFIER_RESULT: Final = WmiQualifier(
    data_type=WmiType(WmiDataType.BOOLEAN, False),
    name=None,
    value=True,
    offset=0
)

# Named WMI qualifier with a value
FULL_QUALIFIER: Final = bytes.fromhex(
    (
        "1C 00 00 00"   # Length (28 bytes)
        "0B 00 00 00"   # Data type (boolean)
        "00 00 00 00"   # Name offset (0)
        "0A 00 00 00"   # Value offset (10)
        "54 00 45 00"   # Null-teminated name string ("TEST")
        "53 00 54 00"
        "00 00"
        "FF FF"         # Boolean value (True)
    )
)

# Parsing result of FULL_QUALIFIER
FULL_QUALIFIER_RESULT: Final = WmiQualifier(
    data_type=WmiType(WmiDataType.BOOLEAN, False),
    name="TEST",
    value=True,
    offset=0
)

# Oversized WMI qualifier
OVERSIZED_QUALIFIER: Final = bytes.fromhex(
    (
        "11 00 00 00"   # Length (16 bytes + 1 byte)
        "08 00 00 00"   # Data type (string)
        "FF FF FF FF"   # Name offset (placeholder)
        "FF FF FF FF"   # Value offset (placeholder)
    )
)

# Undersized WMI
UNDERSIZED_QUALIFIER: Final = bytes.fromhex(
    (
        "0F 00 00 00"   # Length (15 bytes, one byte is missing)
        "08 00 00 00"   # Data type (string)
        "FF FF FF FF"   # Name offset (placeholder)
        "FF FF FF FF"   # Value offset (placeholder)
    )
)

# WMI qualifier with an invalid data type
INVALID_TYPE_QUALIFIER: Final = bytes.fromhex(
    (
        "10 00 00 00"   # Length (16 bytes)
        "DE AD BE EF"   # Bogus data type
        "FF FF FF FF"   # Name offset (placeholder)
        "FF FF FF FF"   # Value offset (placeholder)
    )
)

# WMI qualifier with an invalid name offset
INVALID_NAME_OFFSET_QUALIFIER: Final = bytes.fromhex(
    (
        "10 00 00 00"   # Length (16 bytes)
        "08 00 00 00"   # Data type (string)
        "FF 00 00 00"   # Name offset (255, too large)
        "FF FF FF FF"   # Value offset (placeholder)
    )
)

# WMI qualifier with an invalid value offset
INVALID_VALUE_OFFSET_QUALIFIER: Final = bytes.fromhex(
    (
        "10 00 00 00"   # Length (16 bytes)
        "08 00 00 00"   # Data type (string)
        "FF FF FF FF"   # Name offset (placeholder)
        "FF 00 00 00"   # Value offset (255, too large)
    )
)


@pytest.mark.parametrize(
    "data,expected",
    [
        pytest.param(SIMPLE_QUALIFIER, SIMPLE_QUALIFIER_RESULT, id="simple"),
        pytest.param(NAMED_QUALIFIER, NAMED_QUALIFIER_RESULT, id="named"),
        pytest.param(VALUE_QUALIFIER, VALUE_QUALIFIER_RESULT, id="value"),
        pytest.param(FULL_QUALIFIER, FULL_QUALIFIER_RESULT, id="full"),
    ]
)
def test_parsing(data: bytes, expected: WmiQualifier) -> None:
    """Test parsing of WMI qualifiers"""

    assert BMOF_WMI_QUALIFIER.parse(data) == expected


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(OVERSIZED_QUALIFIER, id="oversized"),
        pytest.param(UNDERSIZED_QUALIFIER, id="undersized"),
        pytest.param(INVALID_NAME_OFFSET_QUALIFIER, id="invalid_name_offset"),
        pytest.param(INVALID_VALUE_OFFSET_QUALIFIER, id="invalid_value_offset"),
    ]
)
def test_parsing_invalid(data: bytes) -> None:
    """Test error handling when trying to parse malformed WMI qualifiers"""

    with pytest.raises(ConstructError):
        BMOF_WMI_QUALIFIER.parse(data)


def test_parsing_invalid_data_type() -> None:
    """Test error handling when trying to parse a WMI qualifier with a invalid data type"""

    with pytest.raises(ValueError):
        BMOF_WMI_QUALIFIER.parse(INVALID_TYPE_QUALIFIER)
