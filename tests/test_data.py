#!/usr/bin/python3

""""Tests for data parsing"""

from __future__ import annotations
from unittest import TestCase
from typing import Final
from construct import MappingError, StringError, ExplicitError
from tarkin.type import Type, DataType
from tarkin.data import MOF_DATA
from .data import load_test_data


TEST_BOOL: Final = True
TEST_SINT32: Final = 1398035268

TEST_TYPE_BOOL: Final = Type(
    basic_type=DataType.BOOLEAN,
    is_array=False
)
TEST_TYPE_SINT32: Final = Type(
    basic_type=DataType.SINT32,
    is_array=False
)
TEST_TYPE_STRING: Final = Type(
    basic_type=DataType.STRING,
    is_array=False
)
TEST_TYPE_OBJECT: Final = Type(
    basic_type=DataType.OBJECT,
    is_array=True
)


class DataTest(TestCase):
    """Tests for data parsing"""

    def test_parse_bool(self) -> None:
        """Test parsing of boolean data"""
        boolean = MOF_DATA(TEST_TYPE_BOOL).parse(load_test_data("data/bool.bin"))

        self.assertEqual(boolean, TEST_BOOL)

    def test_parse_sint32(self) -> None:
        """Test parsing of sint32 data"""
        sint32 = MOF_DATA(TEST_TYPE_SINT32).parse(load_test_data("data/sint32.bin"))

        self.assertEqual(sint32, TEST_SINT32)

    def test_parse_string(self) -> None:
        """Test parsing of string data"""
        string = MOF_DATA(TEST_TYPE_STRING).parse(load_test_data("data/string.bin"))

        self.assertEqual(string, "WMI")

    def test_parse_bool_invalid(self) -> None:
        """Test parsing of invalid boolean data"""
        with self.assertRaises(MappingError):
            MOF_DATA(TEST_TYPE_BOOL).parse(load_test_data("data/bool_invalid.bin"))

    def test_parse_string_invalid(self) -> None:
        """Test parsing of invalid string data"""
        with self.assertRaises(StringError):
            MOF_DATA(TEST_TYPE_STRING).parse(load_test_data("data/string_invalid.bin"))

    def test_parse_type_unknown(self) -> None:
        """Test parsing of data with an unknown type"""
        with self.assertRaises(ExplicitError):
            MOF_DATA(TEST_TYPE_OBJECT).parse(load_test_data("data/bool.bin"))

    def test_build_bool(self) -> None:
        """Test building of boolean data"""
        data = MOF_DATA(TEST_TYPE_BOOL).build(TEST_BOOL)

        self.assertEqual(data, bytes(load_test_data("data/bool.bin")))

    def test_build_sint32(self) -> None:
        """Test building of sint32 data"""
        data = MOF_DATA(TEST_TYPE_SINT32).build(TEST_SINT32)

        self.assertEqual(data, bytes(load_test_data("data/sint32.bin")))

    def test_build_string(self) -> None:
        """Test building of string data"""
        data = MOF_DATA(TEST_TYPE_STRING).build("WMI\x00")

        self.assertEqual(data, bytes(load_test_data("data/string.bin")))
