#!/usr/bin/python3

"""Test for WMI data parsing and building"""

from typing import Final
from construct import ConstructError
import pytest
from tarkin.wmi_object import WmiObject, WmiObjectType  # Must come before tarkin.wmi_data!
from tarkin.wmi_data import BmofWmiData, WmiData
from tarkin.wmi_type import WmiDataType, WmiType

BOOLEAN: Final = bytes.fromhex(
    (
        "FF FF"
    )
)

BOOLEAN_RESULT: Final = True

UINT8: Final = bytes.fromhex(
    (
        "AB"
    )
)

UINT8_RESULT: Final = 0xab

SINT8: Final = bytes.fromhex(
    (
        "FE"
    )
)

SINT8_RESULT: Final = -2

UINT16: Final = bytes.fromhex(
    (
        "CD AB"     # Little-endian
    )
)

UINT16_RESULT: Final = 0xabcd

SINT16: Final = bytes.fromhex(
    (
        "FE FF"     # Little-endian
    )
)

SINT16_RESULT: Final = -2

UINT32: Final = bytes.fromhex(
    (
        "EF BE AD DE"   # Little-endian
    )
)

UINT32_RESULT: Final = 0xdeadbeef

SINT32: Final = bytes.fromhex(
    (
        "FE FF FF FF"   # Little-endian
    )
)

SINT32_RESULT: Final = -2

UINT64: Final = bytes.fromhex(
    (
        "EF BE AD DE EF BE AD DE"   # Little-endian
    )
)

UINT64_RESULT: Final = 0xdeadbeefdeadbeef

SINT64: Final = bytes.fromhex(
    (
        "FE FF FF FF FF FF FF FF"   # Little-endian
    )
)

SINT64_RESULT: Final = -2

STRING: Final = bytes.fromhex(
    (
        "54 00 45 00 53 00 54 00 00 00"     # Encoded as UTF-16LE
    )
)

STRING_RESULT: Final = "TEST"

OBJECT: Final = bytes.fromhex(
    (
        "14 00 00 00"   # Length of the whole structure (20 bytes)
        "FF FF FF FF"   # No qualifiers
        "FF FF FF FF"   # No properties
        "FF FF FF FF"   # No methods
        "00 00 00 00"   # object is a class definition
    )
)

OBJECT_RESULT: Final = WmiObject(
    object_type=WmiObjectType.CLASS,
    qualifiers=None,
    properties=None,
    methods=None
)

# Array containing two boolean values
BOOLEAN_ARRAY: Final = bytes.fromhex(
    (
        "14 00 00 00"   # Length of the whole structure (20 bytes)
        "01 00 00 00"   # Magic value
        "02 00 00 00"   # Value count (2)
        "08 00 00 00"   # Length of this header and values (8 bytes)
        "00 00"         # False
        "FF FF"         # True
    )
)

BOOLEAN_ARRAY_RESULT: Final = [False, True]

INVALID_BOOLEAN: Final = bytes.fromhex(
    "00 FF"
)

# Oversized array
OVERSIZED_ARRAY: Final = bytes.fromhex(
    "15 00 00 00"   # Length of the whole structure (20 bytes + 1 surplus byte)
    "01 00 00 00"   # Magic value
    "02 00 00 00"   # Value count (2)
    "08 00 00 00"   # Length of this header and values (8 bytes)
    "00 00"         # False
    "FF FF"         # True
)

# Undersized array
UNDERSIZED_ARRAY: Final = bytes.fromhex(
    "13 00 00 00"   # Length of the whole structure (19 bytes, one byte is missing)
    "01 00 00 00"   # Magic value
    "02 00 00 00"   # Value count (2)
    "08 00 00 00"   # Length of this header and values (8 bytes)
    "00 00"         # False
    "FF FF"         # True
)

# Array with an invalid magic value
INVALID_ARRAY: Final = bytes.fromhex(
    "14 00 00 00"   # Length of the whole structure (20 bytes)
    "00 00 00 00"   # Invalid magic value
    "02 00 00 00"   # Value count (2)
    "08 00 00 00"   # Length of this header and values (8 bytes)
    "00 00"         # False
    "FF FF"         # True
)

# Array with an oversized item count
OVERSIZED_ITEM_COUNT_ARRAY: Final = bytes.fromhex(
    "14 00 00 00"   # Length of the whole structure (20 bytes)
    "01 00 00 00"   # Magic value
    "03 00 00 00"   # Value count (2 + 1 surplus)
    "08 00 00 00"   # Length of this header and values (8 bytes)
    "00 00"         # False
    "FF FF"         # True
)

# Array with an undersized item count
UNDERSIZED_ITEM_COUNT_ARRAY: Final = bytes.fromhex(
    "14 00 00 00"   # Length of the whole structure (20 bytes)
    "01 00 00 00"   # Magic value
    "02 00 00 00"   # Value count (2, one is missing)
    "08 00 00 00"   # Length of this header and values (8 bytes)
    "00 00"         # False
    "FF FF"         # True
    "FF FF"         # True
)

# Array with an oversized values section
OVERSIZED_VALUES_ARRAY: Final = bytes.fromhex(
    "14 00 00 00"   # Length of the whole structure (20 bytes)
    "01 00 00 00"   # Magic value
    "02 00 00 00"   # Value count (2)
    "09 00 00 00"   # Length of this header and values (8 bytes + 1 byte surplus)
    "00 00"         # False
    "FF FF"         # True
)

# Array with an undersized values section
UNDERSIZED_VALUES_ARRAY: Final = bytes.fromhex(
    "14 00 00 00"   # Length of the whole structure (20 bytes)
    "01 00 00 00"   # Magic value
    "02 00 00 00"   # Value count (2)
    "07 00 00 00"   # Length of this header and values (7 bytes, one byte is missing)
    "00 00"         # False
    "FF FF"         # True
)


@pytest.mark.parametrize(
    "data,wmi_type,expected",
    [
        pytest.param(BOOLEAN, WmiType(WmiDataType.BOOLEAN, False), BOOLEAN_RESULT, id="boolean"),
        pytest.param(UINT8, WmiType(WmiDataType.UINT8, False), UINT8_RESULT, id="uint8"),
        pytest.param(SINT8, WmiType(WmiDataType.SINT8, False), SINT8_RESULT, id="sint8"),
        pytest.param(UINT16, WmiType(WmiDataType.UINT16, False), UINT16_RESULT, id="uint16"),
        pytest.param(SINT16, WmiType(WmiDataType.SINT16, False), SINT16_RESULT, id="sint16"),
        pytest.param(UINT32, WmiType(WmiDataType.UINT32, False), UINT32_RESULT, id="uint32"),
        pytest.param(SINT32, WmiType(WmiDataType.SINT32, False), SINT32_RESULT, id="sint32"),
        pytest.param(UINT64, WmiType(WmiDataType.UINT64, False), UINT64_RESULT, id="uint64"),
        pytest.param(SINT64, WmiType(WmiDataType.SINT64, False), SINT64_RESULT, id="sint64"),
        pytest.param(STRING, WmiType(WmiDataType.STRING, False), STRING_RESULT, id="string"),
        pytest.param(OBJECT, WmiType(WmiDataType.OBJECT, False), OBJECT_RESULT, id="object"),
        pytest.param(
            BOOLEAN_ARRAY,
            WmiType(WmiDataType.BOOLEAN, True),
            BOOLEAN_ARRAY_RESULT,
            id="array"
        ),
        pytest.param(
            UNDERSIZED_ITEM_COUNT_ARRAY,
            WmiType(WmiDataType.BOOLEAN, True),
            BOOLEAN_ARRAY_RESULT,
            id="undersized_item_count_array"),
    ]
)
def test_parsing(data: bytes, wmi_type: WmiType, expected: WmiData) -> None:
    """Test parsing of WMI data types"""

    assert BmofWmiData(lambda _: wmi_type).parse(data) == expected


@pytest.mark.parametrize(
    "data,wmi_type",
    [
        pytest.param(INVALID_BOOLEAN, WmiType(WmiDataType.BOOLEAN, False), id="boolean"),
        pytest.param(OVERSIZED_ARRAY, WmiType(WmiDataType.BOOLEAN, True), id="oversized"),
        pytest.param(UNDERSIZED_ARRAY, WmiType(WmiDataType.BOOLEAN, True), id="undersized"),
        pytest.param(INVALID_ARRAY, WmiType(WmiDataType.BOOLEAN, True), id="invalid"),
        pytest.param(
            OVERSIZED_ITEM_COUNT_ARRAY,
            WmiType(WmiDataType.BOOLEAN, True),
            id="oversized_item_count"
        ),
        pytest.param(
            OVERSIZED_VALUES_ARRAY,
            WmiType(WmiDataType.BOOLEAN, True),
            id="oversized_values"
        ),
        pytest.param(
            UNDERSIZED_VALUES_ARRAY,
            WmiType(WmiDataType.BOOLEAN, True),
            id="undersized_values"
        ),
    ]
)
def test_parsing_missing_data(data: bytes, wmi_type: WmiType) -> None:
    """Test error handling when trying to parse malformed WMI data types"""

    with pytest.raises(ConstructError):
        BmofWmiData(lambda _: wmi_type).parse(data)


@pytest.mark.parametrize(
    "data,wmi_type,expected",
    [
        pytest.param(BOOLEAN_RESULT, WmiType(WmiDataType.BOOLEAN, False), BOOLEAN, id="boolean"),
        pytest.param(UINT8_RESULT, WmiType(WmiDataType.UINT8, False), UINT8, id="uint8"),
        pytest.param(SINT8_RESULT, WmiType(WmiDataType.SINT8, False), SINT8, id="sint8"),
        pytest.param(UINT16_RESULT, WmiType(WmiDataType.UINT16, False), UINT16, id="uint16"),
        pytest.param(SINT16_RESULT, WmiType(WmiDataType.SINT16, False), SINT16, id="sint16"),
        pytest.param(UINT32_RESULT, WmiType(WmiDataType.UINT32, False), UINT32, id="uint32"),
        pytest.param(SINT32_RESULT, WmiType(WmiDataType.SINT32, False), SINT32, id="sint32"),
        pytest.param(UINT64_RESULT, WmiType(WmiDataType.UINT64, False), UINT64, id="uint64"),
        pytest.param(SINT64_RESULT, WmiType(WmiDataType.SINT64, False), SINT64, id="sint64"),
        pytest.param(STRING_RESULT, WmiType(WmiDataType.STRING, False), STRING, id="string"),
        # TODO: We currently have no support for building WMI object types
        # pytest.param(OBJECT_RESULT, WmiType(WmiDataType.OBJECT, False), OBJECT, id="object"),
        pytest.param(
            BOOLEAN_ARRAY_RESULT,
            WmiType(WmiDataType.BOOLEAN, True),
            BOOLEAN_ARRAY,
            id="array"
        ),
    ]
)
def test_building(data: WmiData, wmi_type: WmiType, expected: bytes) -> None:
    """Test building of WMI data types"""

    assert BmofWmiData(lambda _: wmi_type).build(data) == expected
