#!/usr/bin/python3

"""Test for WMI method parsing"""

from typing import Final, Optional
import pytest
from tarkin.wmi_method import WmiMethod
from tarkin.wmi_property import WmiProperty
from tarkin.wmi_qualifier import WmiQualifier
from tarkin.wmi_type import WmiType, WmiDataType

# Simple WMI properties without any duplications
SIMPLE_PROPERTIES: Final = [
    WmiProperty(
        data_type=WmiType(WmiDataType.BOOLEAN, False),
        name="INPUT",
        value=None,
        qualifiers=[
            WmiQualifier(
                data_type=WmiType(WmiDataType.BOOLEAN, False),
                name="IN",
                value=True,
                offset=0
            )
        ]
    ),
    WmiProperty(
        data_type=WmiType(WmiDataType.BOOLEAN, False),
        name="OUTPUT",
        value=None,
        qualifiers=[
            WmiQualifier(
                data_type=WmiType(WmiDataType.BOOLEAN, False),
                name="OUT",
                value=True,
                offset=0
            )
        ]
    )
]

# WMI properties without duplications
DUPLICATED_PROPERTIES: Final = [
    WmiProperty(
        data_type=WmiType(WmiDataType.BOOLEAN, False),
        name="TEST",
        value=None,
        qualifiers=[
            WmiQualifier(
                data_type=WmiType(WmiDataType.BOOLEAN, False),
                name="IN",
                value=True,
                offset=0
            )
        ]
    ),
    WmiProperty(
        data_type=WmiType(WmiDataType.BOOLEAN, False),
        name="TEST",
        value=None,
        qualifiers=[
            WmiQualifier(
                data_type=WmiType(WmiDataType.BOOLEAN, False),
                name="OUT",
                value=True,
                offset=0
            )
        ]
    )
]

# Parsing result of DUPLICATED_PROPERTIES
DUPLICATED_PROPERTIES_RESULT: Final = [
    WmiProperty(
        data_type=WmiType(WmiDataType.BOOLEAN, False),
        name="TEST",
        value=None,
        qualifiers=[
            WmiQualifier(
                data_type=WmiType(WmiDataType.BOOLEAN, False),
                name="IN",
                value=True,
                offset=0
            ),
            WmiQualifier(
                data_type=WmiType(WmiDataType.BOOLEAN, False),
                name="OUT",
                value=True,
                offset=0
            )
        ]
    )
]

# WMI properties determining the return type of the WMI method
SPECIAL_PROPERTIES: Final = [
    WmiProperty(
        data_type=WmiType(WmiDataType.STRING, False),
        name="ReturnValue",
        value=None,
        qualifiers=[
            WmiQualifier(
                data_type=WmiType(WmiDataType.BOOLEAN, False),
                name="PLACEHOLDER",
                value=True,
                offset=0
            )
        ]
    )
]

# WMI properties without a name
MISSING_NAME_PROPERTIES: Final = [
    WmiProperty(
        data_type=WmiType(WmiDataType.BOOLEAN, False),
        name=None,
        value=None,
        qualifiers=[
            WmiQualifier(
                data_type=WmiType(WmiDataType.BOOLEAN, False),
                name="TEST",
                value=None,
                offset=0
            )
        ]
    )
]

# WMI properties without qualifiers
MISSING_QUALIFIERS_PROPERTIES: Final = [
    WmiProperty(
        data_type=WmiType(WmiDataType.BOOLEAN, False),
        name="TEST",
        value=None,
        qualifiers=None
    )
]

# Duplicated WMI properties with conflicting types
CONFLICTING_TYPES_PROPERTIES: Final = [
    WmiProperty(
        data_type=WmiType(WmiDataType.BOOLEAN, False),
        name="TEST",
        value=None,
        qualifiers=[
            WmiQualifier(
                data_type=WmiType(WmiDataType.BOOLEAN, False),
                name="IN",
                value=True,
                offset=0
            )
        ]
    ),
    WmiProperty(
        data_type=WmiType(WmiDataType.STRING, False),
        name="TEST",
        value=None,
        qualifiers=[
            WmiQualifier(
                data_type=WmiType(WmiDataType.BOOLEAN, False),
                name="OUT",
                value=True,
                offset=0
            )
        ]
    )
]

# Duplicated WMI properties with conflicting values
CONFLICTING_VALUES_PROPERTIES: Final = [
    WmiProperty(
        data_type=WmiType(WmiDataType.BOOLEAN, False),
        name="TEST",
        value=True,
        qualifiers=[
            WmiQualifier(
                data_type=WmiType(WmiDataType.BOOLEAN, False),
                name="IN",
                value=True,
                offset=0
            )
        ]
    ),
    WmiProperty(
        data_type=WmiType(WmiDataType.STRING, False),
        name="TEST",
        value=False,
        qualifiers=[
            WmiQualifier(
                data_type=WmiType(WmiDataType.BOOLEAN, False),
                name="OUT",
                value=True,
                offset=0
            )
        ]
    )
]

# Simple WMI qualifiers
SIMPLE_QUALIFIERS: Final = [
    WmiQualifier(
        data_type=WmiType(WmiDataType.BOOLEAN, False),
        name="TEST",
        value=None,
        offset=0
    )
]


def test_parsing_name() -> None:
    """Test handling of the WMI method name during parsing"""

    assert WmiMethod.from_properties("Test", [], None).name == "Test"


@pytest.mark.parametrize(
    "properties,expected",
    [
        pytest.param(SIMPLE_PROPERTIES, SIMPLE_PROPERTIES, id="simple"),
        pytest.param(DUPLICATED_PROPERTIES, DUPLICATED_PROPERTIES_RESULT, id="duplicated")
    ]
)
def test_parsing_parameters(properties: list[WmiProperty], expected: list[WmiProperty]) -> None:
    """Test handling of WMI method parameters during parsing"""

    assert WmiMethod.from_properties("Test", properties, None).parameters == expected


@pytest.mark.parametrize(
    "properties,expected",
    [
        pytest.param(SIMPLE_PROPERTIES, WmiType(WmiDataType.VOID, False), id="void"),
        pytest.param(SPECIAL_PROPERTIES, WmiType(WmiDataType.STRING, False), id="non_void")
    ]
)
def test_parsing_return_value(properties: list[WmiProperty], expected: WmiType) -> None:
    """Test parsing of the return type of the WMI method"""

    assert WmiMethod.from_properties("Test", properties, None).return_type == expected


@pytest.mark.parametrize(
    "properties",
    [
        pytest.param(MISSING_NAME_PROPERTIES, id="missing_name"),
        pytest.param(MISSING_QUALIFIERS_PROPERTIES, id="missing_qualifiers"),
        pytest.param(CONFLICTING_TYPES_PROPERTIES, id="conflicting_types"),
        pytest.param(CONFLICTING_VALUES_PROPERTIES, id="conflicting_values")
    ]
)
def test_parsing_invalid_parameters(properties: list[WmiProperty]) -> None:
    """Test error handling when trying to parse malformed WMI method parameters"""

    with pytest.raises(RuntimeError):
        WmiMethod.from_properties("Test", properties, None)


@pytest.mark.parametrize(
    "qualifiers",
    [
        pytest.param(None, id="none"),
        pytest.param(SIMPLE_QUALIFIERS, id="some")
    ]
)
def test_parsing_qualifiers(qualifiers: Optional[list[WmiQualifier]]) -> None:
    """Test handling of WMI method qualifiers during parsing"""

    assert WmiMethod.from_properties("Test", [], qualifiers).qualifiers == qualifiers
