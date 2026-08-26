#!/usr/bin/python3

"""Tests for WMI property parsing"""

from typing import Final
from construct import ConstructError
import pytest
from tarkin.wmi_property import BMOF_WMI_PROPERTY, WmiProperty
from tarkin.wmi_qualifier import WmiQualifier
from tarkin.wmi_type import WmiType, WmiDataType

# WMI property with no additional data
SIMPLE_PROPERTY: Final = bytes.fromhex(
    (
        "14 00 00 00"   # Length (20 bytes)
        "08 00 00 00"   # Data type (string)
        "FF FF FF FF"   # Name offset (placeholder)
        "FF FF FF FF"   # Value offset (placeholder)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
    )
)

# Parsing result of SIMPLE_PROPERTY
SIMPLE_PROPERTY_RESULT: Final = WmiProperty(
    data_type=WmiType(WmiDataType.STRING, False),
    name=None,
    value=None,
    qualifiers=None
)

# Named WMI property
NAMED_PROPERTY: Final = bytes.fromhex(
    (
        "1E 00 00 00"   # Length (30 bytes)
        "08 00 00 00"   # Data type (string)
        "00 00 00 00"   # Name offset (0)
        "FF FF FF FF"   # Name offset (placeholder)
        "FF FF FF FF"   # Value offset (placeholder)

        "54 00 45 00"   # Null-teminated name string ("TEST")
        "53 00 54 00"
        "00 00"
    )
)

# Parsing result of NAMED_PROPERTY
NAMED_PROPERTY_RESULT: Final = WmiProperty(
    data_type=WmiType(WmiDataType.STRING, False),
    name="TEST",
    value=None,
    qualifiers=None
)

# WMI property with a value
VALUE_PROPERTY: Final = bytes.fromhex(
    (
        "16 00 00 00"   # Length (22 bytes)
        "0B 00 00 00"   # Data type (boolean)
        "FF FF FF FF"   # Name offset (placeholder)
        "00 00 00 00"   # Value offset (0)
        "FF FF FF FF"   # Qualifiers offset (placeholder)

        "FF FF"         # Boolean value (True)
    )
)

# Parsing result of VALUE_PROPERTY
VALUE_PROPERTY_RESULT: Final = WmiProperty(
    data_type=WmiType(WmiDataType.BOOLEAN, False),
    name=None,
    value=True,
    qualifiers=None
)

# WMI property with a qualifier
QUALIFIED_PROPERTY: Final = bytes.fromhex(
    (
        "2C 00 00 00"   # Length (44 bytes)
        "08 00 00 00"   # Data type (string)
        "FF FF FF FF"   # Name offset (placeholder)
        "FF FF FF FF"   # Value offset (placeholder)
        "00 00 00 00"   # Qualifiers offset (0)

        "18 00 00 00"   # 8 bytes for the header + 16 bytes for the items
        "01 00 00 00"   # One item inside array

        "10 00 00 00"   # Qualifier length (16 bytes)
        "08 00 00 00"   # Qualifier data type (string)
        "FF FF FF FF"   # Qualifier name offset (placeholder)
        "FF FF FF FF"   # Qualifier value offset (placeholder)
    )
)

# Parsing result of QUALIFIED_PROPERTY
QUALIFIED_PROPERTY_RESULT: Final = WmiProperty(
    data_type=WmiType(WmiDataType.STRING, False),
    name=None,
    value=None,
    qualifiers=[
        WmiQualifier(
            data_type=WmiType(WmiDataType.STRING, False),
            value=None,
            name=None,
            offset=28
        )
    ]
)

# Named and qualified WMI property with a value
FULL_PROPERTY: Final = bytes.fromhex(
    (
        "38 00 00 00"   # Length (56 bytes)
        "0B 00 00 00"   # Data type (boolean)
        "00 00 00 00"   # Name offset (0)
        "0A 00 00 00"   # Value offset (10)
        "0C 00 00 00"   # Qualifiers offset (12)

        "54 00 45 00"   # Null-teminated name string ("TEST")
        "53 00 54 00"
        "00 00"

        "FF FF"         # Boolean value (True)

        "18 00 00 00"   # 8 bytes for the header + 16 bytes for the items
        "01 00 00 00"   # One item inside array

        "10 00 00 00"   # Qualifier length (16 bytes)
        "08 00 00 00"   # Qualifier data type (string)
        "FF FF FF FF"   # Qualifier name offset (placeholder)
        "FF FF FF FF"   # Qualifier value offset (placeholder)
    )
)

# Parsing result of FULL_PROPERTY
FULL_PROPERTY_RESULT: Final = WmiProperty(
    data_type=WmiType(WmiDataType.BOOLEAN, False),
    name="TEST",
    value=True,
    qualifiers=[
        WmiQualifier(
            data_type=WmiType(WmiDataType.STRING, False),
            value=None,
            name=None,
            offset=40
        )
    ]
)

# Oversized WMI property
OVERSIZED_PROPERTY: Final = bytes.fromhex(
    (
        "15 00 00 00"   # Length (20 bytes + 1 byte)
        "08 00 00 00"   # Data type (string)
        "FF FF FF FF"   # Name offset (placeholder)
        "FF FF FF FF"   # Value offset (placeholder)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
    )
)

# Undersized WMI property
UNDERSIZED_PROPERTY: Final = bytes.fromhex(
    (
        "13 00 00 00"   # Length (19 bytes, one byte is missing)
        "08 00 00 00"   # Data type (string)
        "FF FF FF FF"   # Name offset (placeholder)
        "FF FF FF FF"   # Value offset (placeholder)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
    )
)

# WMI property with an invalid data type
INVALID_TYPE_PROPERTY: Final = bytes.fromhex(
    (
        "14 00 00 00"   # Length (20 bytes)
        "DE AD BE EF"   # Bogus data type
        "FF FF FF FF"   # Name offset (placeholder)
        "FF FF FF FF"   # Value offset (placeholder)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
    )
)

# WMI property with an invalid name offset
INVALID_NAME_OFFSET_PROPERTY: Final = bytes.fromhex(
    (
        "14 00 00 00"   # Length (20 bytes)
        "08 00 00 00"   # Data type (string)
        "FF 00 00 00"   # Name offset (255, too large)
        "FF FF FF FF"   # Value offset (placeholder)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
    )
)

# WMI property with an invalid value offset
INVALID_VALUE_OFFSET_PROPERTY: Final = bytes.fromhex(
    (
        "14 00 00 00"   # Length (20 bytes)
        "08 00 00 00"   # Data type (string)
        "FF FF FF FF"   # Name offset (placeholder)
        "FF 00 00 00"   # Value offset (255, too large)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
    )
)

# WMI property with an invalid qualifiers offset
INVALID_QUALIFIERS_OFFSET_PROPERTY: Final = bytes.fromhex(
    (
        "14 00 00 00"   # Length (20 bytes)
        "08 00 00 00"   # Data type (string)
        "FF FF FF FF"   # Name offset (placeholder)
        "FF FF FF FF"   # Value offset (placeholder)
        "FF 00 00 00"   # Qualifiers offset (255, too large)
    )
)


@pytest.mark.parametrize(
    "data,expected",
    [
        pytest.param(SIMPLE_PROPERTY, SIMPLE_PROPERTY_RESULT, id="simple"),
        pytest.param(NAMED_PROPERTY, NAMED_PROPERTY_RESULT, id="named"),
        pytest.param(VALUE_PROPERTY, VALUE_PROPERTY_RESULT, id="value"),
        pytest.param(QUALIFIED_PROPERTY, QUALIFIED_PROPERTY_RESULT, id="qualified"),
        pytest.param(FULL_PROPERTY, FULL_PROPERTY_RESULT, id="full"),
    ]
)
def test_parsing(data: bytes, expected: WmiProperty) -> None:
    """Test parsing of WMI properties"""

    assert BMOF_WMI_PROPERTY.parse(data) == expected


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(OVERSIZED_PROPERTY, id="oversized"),
        pytest.param(UNDERSIZED_PROPERTY, id="undersized"),
        pytest.param(INVALID_NAME_OFFSET_PROPERTY, id="invalid_name_offset"),
        pytest.param(INVALID_VALUE_OFFSET_PROPERTY, id="invalid_value_offset"),
        pytest.param(INVALID_QUALIFIERS_OFFSET_PROPERTY, id="invalid_qualifiers_offset"),
    ]
)
def test_parsing_invalid(data: bytes) -> None:
    """Test error handling when trying to parse malformed WMI properties"""

    with pytest.raises(ConstructError):
        BMOF_WMI_PROPERTY.parse(data)


def test_parsing_invalid_data_type() -> None:
    """Test error handling when trying to parse a WMI property with a invalid data type"""

    with pytest.raises(ValueError):
        BMOF_WMI_PROPERTY.parse(INVALID_TYPE_PROPERTY)
