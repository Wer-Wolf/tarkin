#!/usr/bin/python3

"""Test for WMI type parsing and building"""

from typing import Final
import pytest
from tarkin.wmi_type import BMOF_WMI_TYPE, WmiDataType, WmiType


BOOLEAN: Final = bytes.fromhex(
    (
        "0B 00 00 00"
    )
)

UINT8: Final = bytes.fromhex(
    (
        "11 00 00 00"
    )
)

SINT8: Final = bytes.fromhex(
    (
        "10 00 00 00"
    )
)

UINT16: Final = bytes.fromhex(
    (
        "12 00 00 00"
    )
)

SINT16: Final = bytes.fromhex(
    (
        "02 00 00 00"
    )
)

UINT32: Final = bytes.fromhex(
    (
        "13 00 00 00"
    )
)

SINT32: Final = bytes.fromhex(
    (
        "03 00 00 00"
    )
)

UINT64: Final = bytes.fromhex(
    (
        "15 00 00 00"
    )
)

SINT64: Final = bytes.fromhex(
    (
        "14 00 00 00"
    )
)

REAL32: Final = bytes.fromhex(
    (
        "04 00 00 00"
    )
)

REAL64: Final = bytes.fromhex(
    (
        "05 00 00 00"
    )
)

CHAR16: Final = bytes.fromhex(
    (
        "67 00 00  00"
    )
)

STRING: Final = bytes.fromhex(
    (
        "08 00 00 00"
    )
)

OBJECT: Final = bytes.fromhex(
    (
        "0D 00 00 00"
    )
)

DATETIME: Final = bytes.fromhex(
    (
        "65 00 00 00"
    )
)

REFERENCE: Final = bytes.fromhex(
    (
        "66 00 00 00"
    )
)

VOID: Final = bytes.fromhex(
    (
        "00 00 00 00"
    )
)

BOOLEAN_ARRAY: Final = bytes.fromhex(
    (
        "0B 20 00 00"
    )
)

INVALID_TYPE: Final = bytes.fromhex(
    (
        "FF FF FF FF"
    )
)


@pytest.mark.parametrize(
    "data,expected",
    [
        pytest.param(BOOLEAN, WmiType(WmiDataType.BOOLEAN, False), id="boolean"),
        pytest.param(UINT8, WmiType(WmiDataType.UINT8, False), id="uint8"),
        pytest.param(SINT8, WmiType(WmiDataType.SINT8, False), id="sint8"),
        pytest.param(UINT16, WmiType(WmiDataType.UINT16, False), id="uint16"),
        pytest.param(SINT16, WmiType(WmiDataType.SINT16, False), id="sint16"),
        pytest.param(UINT32, WmiType(WmiDataType.UINT32, False), id="uint32"),
        pytest.param(SINT32, WmiType(WmiDataType.SINT32, False), id="sint32"),
        pytest.param(UINT64, WmiType(WmiDataType.UINT64, False), id="uint64"),
        pytest.param(SINT64, WmiType(WmiDataType.SINT64, False), id="sint64"),
        pytest.param(REAL32, WmiType(WmiDataType.REAL32, False), id="real32"),
        pytest.param(REAL64, WmiType(WmiDataType.REAL64, False), id="real64"),
        pytest.param(CHAR16, WmiType(WmiDataType.CHAR16, False), id="char16"),
        pytest.param(STRING, WmiType(WmiDataType.STRING, False), id="string"),
        pytest.param(OBJECT, WmiType(WmiDataType.OBJECT, False), id="object"),
        pytest.param(DATETIME, WmiType(WmiDataType.DATETIME, False), id="datetime"),
        pytest.param(REFERENCE, WmiType(WmiDataType.REFERENCE, False), id="reference"),
        pytest.param(VOID, WmiType(WmiDataType.VOID, False), id="void"),
        pytest.param(BOOLEAN_ARRAY, WmiType(WmiDataType.BOOLEAN, True), id="array"),
    ]
)
def test_parsing(data: bytes, expected: WmiType) -> None:
    """Test parsing of WMI types"""

    assert BMOF_WMI_TYPE.parse(data) == expected


def test_parsing_invalid_type() -> None:
    """Test error handling when trying to parse an invalid WMI type"""

    with pytest.raises(ValueError):
        BMOF_WMI_TYPE.parse(INVALID_TYPE)


@pytest.mark.parametrize(
    "wmi_type,expected",
    [
        pytest.param(WmiType(WmiDataType.BOOLEAN, False), BOOLEAN, id="boolean"),
        pytest.param(WmiType(WmiDataType.UINT8, False), UINT8, id="uint8"),
        pytest.param(WmiType(WmiDataType.SINT8, False), SINT8, id="sint8"),
        pytest.param(WmiType(WmiDataType.UINT16, False), UINT16, id="uint16"),
        pytest.param(WmiType(WmiDataType.SINT16, False), SINT16, id="sint16"),
        pytest.param(WmiType(WmiDataType.UINT32, False), UINT32, id="uint32"),
        pytest.param(WmiType(WmiDataType.SINT32, False), SINT32, id="sint32"),
        pytest.param(WmiType(WmiDataType.UINT64, False), UINT64, id="uint64"),
        pytest.param(WmiType(WmiDataType.SINT64, False), SINT64, id="sint64"),
        pytest.param(WmiType(WmiDataType.REAL32, False), REAL32, id="real32"),
        pytest.param(WmiType(WmiDataType.REAL64, False), REAL64, id="real64"),
        pytest.param(WmiType(WmiDataType.CHAR16, False), CHAR16, id="char16"),
        pytest.param(WmiType(WmiDataType.STRING, False), STRING, id="string"),
        pytest.param(WmiType(WmiDataType.OBJECT, False), OBJECT, id="object"),
        pytest.param(WmiType(WmiDataType.DATETIME, False), DATETIME, id="datetime"),
        pytest.param(WmiType(WmiDataType.REFERENCE, False), REFERENCE, id="reference"),
        pytest.param(WmiType(WmiDataType.VOID, False), VOID, id="void"),
        pytest.param(WmiType(WmiDataType.BOOLEAN, True), BOOLEAN_ARRAY, id="array"),
    ]
)
def test_building(wmi_type: WmiType, expected: bytes) -> None:
    """Test building of WMI types"""

    assert BMOF_WMI_TYPE.build(wmi_type) == expected
