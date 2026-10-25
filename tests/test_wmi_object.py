#!/usr/bin/python3

"""Tests for WMI object parsing"""

from typing import Final
from construct import ConstructError
import pytest
from tarkin.wmi_method import WmiMethod
from tarkin.wmi_object import BMOF_WMI_OBJECT, WmiObject, WmiObjectType, WmiClassFlags, \
    WmiInstanceFlags
from tarkin.wmi_property import WmiProperty
from tarkin.wmi_qualifier import WmiQualifier
from tarkin.wmi_type import WmiType, WmiDataType

# WMI object with no additional data
SIMPLE_OBJECT: Final = bytes.fromhex(
    (
        "14 00 00 00"   # Length (20 bytes)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
        "FF FF FF FF"   # Properties offset (placeholder)
        "FF FF FF FF"   # Methods offset (placeholder)
        "00 00 00 00"   # Object type (class)
    )
)

# Parsing result of SIMPLE_OBJECT
SIMPLE_OBJECT_RESULT: Final = WmiObject(
    object_type=WmiObjectType.CLASS,
    qualifiers=None,
    properties=None,
    methods=None
)

# WMI object with qualifiers
QUALIFIED_OBJECT: Final = bytes.fromhex(
    (
        "2C 00 00 00"   # Length (44 bytes)
        "00 00 00 00"   # Qualifiers offset (0)
        "FF FF FF FF"   # Properties offset (placeholder)
        "FF FF FF FF"   # Methods offset (placeholder)
        "01 00 00 00"   # Object type (instance)

        "18 00 00 00"   # 8 bytes for the header + 16 bytes for the items
        "01 00 00 00"   # One item inside array

        "10 00 00 00"   # Qualifier length (16 bytes)
        "08 00 00 00"   # Qualifier data type (string)
        "FF FF FF FF"   # Qualifier name offset (placeholder)
        "FF FF FF FF"   # Qualifier value offset (placeholder)
    )
)

# Parsing result of QUALIFIED_OBJECT
QUALIFIED_OBJECT_RESULT: Final = WmiObject(
    object_type=WmiObjectType.INSTANCE,
    qualifiers=[
        WmiQualifier(
            data_type=WmiType(WmiDataType.STRING, False),
            value=None,
            name=None,
            offset=28
        )
    ],
    properties=None,
    methods=None
)

# WMI object with properties
PROPERTIES_OBJECT: Final = bytes.fromhex(
    (
        "30 00 00 00"   # Length (48 bytes)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
        "00 00 00 00"   # Properties offset (0)
        "FF FF FF FF"   # Methods offset (placeholder)
        "00 00 00 00"   # Object type (class)

        "1C 00 00 00"   # 8 bytes for the header + 20 bytes for the items
        "01 00 00 00"   # One item inside array

        "14 00 00 00"   # Property length (20 bytes)
        "08 00 00 00"   # Property data type (string)
        "FF FF FF FF"   # Property name offset (placeholder)
        "FF FF FF FF"   # Property value offset (placeholder)
        "FF FF FF FF"   # Property qualifiers offset (placeholder)
    )
)

# Parsing result pf PROPERTIES_OBJECT
PROPERTIES_OBJECT_RESULT: Final = WmiObject(
    object_type=WmiObjectType.CLASS,
    qualifiers=None,
    properties=[
        WmiProperty(
            data_type=WmiType(WmiDataType.STRING, False),
            name=None,
            value=None,
            qualifiers=None
        )
    ],
    methods=None
)

# WMI object with methods
METHODS_OBJECT: Final = bytes.fromhex(
    (
        "3A 00 00 00"   # Length (58 bytes)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
        "FF FF FF FF"   # Properties offset (placeholder)
        "00 00 00 00"   # Methods offset (0)
        "01 00 00 00"   # Object type (instance)

        "26 00 00 00"   # 8 bytes for the header + 30 bytes for the items
        "01 00 00 00"   # One item inside array

        "1E 00 00 00"   # Property length (30 bytes)
        "00 00 00 00"   # Property data type (void)
        "00 00 00 00"   # Property name offset (0)
        "FF FF FF FF"   # Propert value offset (placeholder)
        "FF FF FF FF"   # Property qualifiers offset (placeholder)

        "54 00 45 00"   # Null-teminated name string ("TEST")
        "53 00 54 00"
        "00 00"
    )
)

# Parsing result of METHODS_OBJECT
METHODS_OBJECT_RESULT: Final = WmiObject(
    object_type=WmiObjectType.INSTANCE,
    qualifiers=None,
    properties=None,
    methods=[
        WmiMethod(
            name="TEST",
            parameters=[],
            qualifiers=None,
            return_type=WmiType(WmiDataType.VOID, False)
        )
    ]
)

# WMI object with qualifiers, properties and methods
FULL_OBJECT: Final = bytes.fromhex(
    (
        "6E 00 00 00"   # Length (110 bytes)
        "00 00 00 00"   # Qualifiers offset (0)
        "18 00 00 00"   # Properties offset (24)
        "34 00 00 00"   # Methods offset (52)
        "00 00 00 00"   # Object type (class)

        "18 00 00 00"   # 8 bytes for the header + 16 bytes for the items
        "01 00 00 00"   # One item inside array

        "10 00 00 00"   # Qualifier length (16 bytes)
        "08 00 00 00"   # Qualifier data type (string)
        "FF FF FF FF"   # Qualifier name offset (placeholder)
        "FF FF FF FF"   # Qualifier value offset (placeholder)

        "1C 00 00 00"   # 8 bytes for the header + 20 bytes for the items
        "01 00 00 00"   # One item inside array

        "14 00 00 00"   # Property length (20 bytes)
        "08 00 00 00"   # Property data type (string)
        "FF FF FF FF"   # Property name offset (placeholder)
        "FF FF FF FF"   # Property value offset (placeholder)
        "FF FF FF FF"   # Property qualifiers offset (placeholder)

        "26 00 00 00"   # 8 bytes for the header + 30 bytes for the items
        "01 00 00 00"   # One item inside array

        "1E 00 00 00"   # Property length (30 bytes)
        "00 00 00 00"   # Property data type (void)
        "00 00 00 00"   # Property name offset (0)
        "FF FF FF FF"   # Propert value offset (placeholder)
        "FF FF FF FF"   # Property qualifiers offset (placeholder)

        "54 00 45 00"   # Null-teminated name string ("TEST")
        "53 00 54 00"
        "00 00"
    )
)

# Parsing result of FULL_OBJECT
FULL_OBJECT_RESULT: Final = WmiObject(
    object_type=WmiObjectType.CLASS,
    qualifiers=[
        WmiQualifier(
            data_type=WmiType(WmiDataType.STRING, False),
            value=None,
            name=None,
            offset=28
        )
    ],
    properties=[
        WmiProperty(
            data_type=WmiType(WmiDataType.STRING, False),
            name=None,
            value=None,
            qualifiers=None
        )
    ],
    methods=[
        WmiMethod(
            name="TEST",
            parameters=[],
            qualifiers=None,
            return_type=WmiType(WmiDataType.VOID, False)
        )
    ]
)

# Oversized WMI object
OVERSIZED_OBJECT: Final = bytes.fromhex(
    (
        "15 00 00 00"   # Length (20 bytes + 1 bytes)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
        "FF FF FF FF"   # Properties offset (placeholder)
        "FF FF FF FF"   # Methods offset (placeholder)
        "00 00 00 00"   # Object type (class)
    )
)

# Undersized WMI object
UNDERSIZED_OBJECT: Final = bytes.fromhex(
    (
        "13 00 00 00"   # Length (19 bytes, one byte is missing)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
        "FF FF FF FF"   # Properties offset (placeholder)
        "FF FF FF FF"   # Methods offset (placeholder)
        "00 00 00 00"   # Object type (class)
    )
)

# WMI object with an invalid object type
INVALID_TYPE_OBJECT: Final = bytes.fromhex(
    (
        "14 00 00 00"   # Length (20 bytes)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
        "FF FF FF FF"   # Properties offset (placeholder)
        "FF FF FF FF"   # Methods offset (placeholder)
        "DE AD BE EF"   # Bogus object type
    )
)

# WMI object with an invalid qualifiers offset
INVALID_QUALIFIERS_OFFSET_OBJECT: Final = bytes.fromhex(
    (
        "14 00 00 00"   # Length (20 bytes)
        "FF 00 00 00"   # Qualifiers offset (255, too large)
        "FF FF FF FF"   # Properties offset (placeholder)
        "FF FF FF FF"   # Methods offset (placeholder)
        "00 00 00 00"   # Object type (class)
    )
)

# WMI object with an invalid properties offset
INVALID_PROPERTIES_OFFSET_OBJECT: Final = bytes.fromhex(
    (
        "14 00 00 00"   # Length (20 bytes)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
        "FF 00 00 00"   # Properties offset (255, too large)
        "FF FF FF FF"   # Methods offset (placeholder)
        "00 00 00 00"   # Object type (class)
    )
)

# WMI object with an invalid methods offset
INVALID_METHODS_OFFSET_OBJECT: Final = bytes.fromhex(
    (
        "14 00 00 00"   # Length (20 bytes)
        "FF FF FF FF"   # Qualifiers offset (placeholder)
        "FF FF FF FF"   # Properties offset (placeholder)
        "FF 00 00 00"   # Methods offset (255, too large)
        "00 00 00 00"   # Object type (class)
    )
)


@pytest.mark.parametrize(
    "data,expected",
    [
        pytest.param(SIMPLE_OBJECT, SIMPLE_OBJECT_RESULT, id="simple"),
        pytest.param(QUALIFIED_OBJECT, QUALIFIED_OBJECT_RESULT, id="qualified"),
        pytest.param(PROPERTIES_OBJECT, PROPERTIES_OBJECT_RESULT, id="properties"),
        pytest.param(METHODS_OBJECT, METHODS_OBJECT_RESULT, id="methods"),
        pytest.param(FULL_OBJECT, FULL_OBJECT_RESULT, id="full"),
    ]
)
def test_parsing(data: bytes, expected: WmiObject) -> None:
    """Test parsing of WMI objects"""

    assert BMOF_WMI_OBJECT.parse(data) == expected


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(OVERSIZED_OBJECT, id="oversized"),
        pytest.param(UNDERSIZED_OBJECT, id="undersized"),
        pytest.param(INVALID_QUALIFIERS_OFFSET_OBJECT, id="invalid_qualifiers_offset"),
        pytest.param(INVALID_PROPERTIES_OFFSET_OBJECT, id="invalid_properties_offset"),
        pytest.param(INVALID_METHODS_OFFSET_OBJECT, id="invalid_methods_offset"),
    ]
)
def test_parsing_invalid(data: bytes) -> None:
    """Test error handling when trying to parse malformed WMI objects"""

    with pytest.raises(ConstructError):
        BMOF_WMI_OBJECT.parse(data)


def test_parsing_invalid_object_type() -> None:
    """Test error handling when trying to parse a WMI object with a invalid object type"""

    with pytest.raises(ValueError):
        BMOF_WMI_OBJECT.parse(INVALID_TYPE_OBJECT)


def test_parsing_special_proeprties() -> None:
    """Test parsing of special properties"""
    variable = WmiProperty(
        data_type=WmiType(WmiDataType.STRING, False),
        name="TestProperty",
        value="TEST",
        qualifiers=None
    )
    obj = WmiObject(
        object_type=WmiObjectType.INSTANCE,
        qualifiers=None,
        properties=[
            WmiProperty(
                data_type=WmiType(WmiDataType.STRING, False),
                name="__CLASS",
                value="TestClass",
                qualifiers=None
            ),
            WmiProperty(
                data_type=WmiType(WmiDataType.STRING, False),
                name="__NAMESPACE",
                value="TestNamespace",
                qualifiers=None
            ),
            WmiProperty(
                data_type=WmiType(WmiDataType.STRING, False),
                name="__SUPERCLASS",
                value="TestSuperclass",
                qualifiers=None
            ),
            WmiProperty(
                data_type=WmiType(WmiDataType.SINT32, False),
                name="__CLASSFLAGS",
                value=WmiClassFlags.SAFEUPDATE,
                qualifiers=None
            ),
            WmiProperty(
                data_type=WmiType(WmiDataType.SINT32, False),
                name="__INSTANCEFLAGS",
                value=WmiInstanceFlags.UPDATEONLY,
                qualifiers=None
            ),
            WmiProperty(
                data_type=WmiType(WmiDataType.STRING, False),
                name="__ALIAS",
                value="TestAlias",
                qualifiers=None
            ),
            variable
        ],
        methods=None
    )

    assert obj.name == "TestClass"
    assert obj.namespace == "TestNamespace"
    assert obj.superclass == "TestSuperclass"
    assert obj.classflags == WmiClassFlags.SAFEUPDATE
    assert obj.instanceflags == WmiInstanceFlags.UPDATEONLY
    assert obj.alias == "TestAlias"
    assert list(obj.variables) == [variable]
