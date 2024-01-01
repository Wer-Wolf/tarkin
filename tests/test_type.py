#!/usr/bin/python3

""""Tests for data type parsing"""

from __future__ import annotations
from unittest import TestCase
from typing import Final
from construct import StreamError
from tarkin.type import Type, DataType, MOF_DATA_TYPE


TEST_SINT32_ARRAY: Final = b"\x03\x20\x00\x00"
TEST_OBJECT: Final = b"\x0d\x00\x00\x00"
TEST_STRING: Final = b"\x08\x00\x00\x00"
TEST_BOOL: Final = b"\x0b\x00\x00\x00"

TEST_INVALID_TYPE: Final = b"\xff\xff\x00\x00"
TEST_INVALID_LENGTH: Final = b"\xff\xff\x00"

TEST_TYPE_SINT32_ARRAY: Final = Type(
    basic_type=DataType.SINT32,
    is_array=True
)
TEST_TYPE_STRING: Final = Type(
    basic_type=DataType.STRING,
    is_array=False
)
TEST_TYPE_BOOL: Final = Type(
    basic_type=DataType.BOOLEAN,
    is_array=False
)
TEST_TYPE_OBJECT: Final = Type(
    basic_type=DataType.OBJECT,
    is_array=False
)


class TypeTest(TestCase):
    """Tests for data type parsing"""

    def test_parse_int32_array(self) -> None:
        """Test parsing of an sint32 array type"""
        self.assertEqual(MOF_DATA_TYPE.parse(TEST_SINT32_ARRAY), TEST_TYPE_SINT32_ARRAY)

    def test_parse_object(self) -> None:
        """Test parsing of an object type"""
        self.assertEqual(MOF_DATA_TYPE.parse(TEST_OBJECT), TEST_TYPE_OBJECT)

    def test_parse_string(self) -> None:
        """Test parsing of an string type"""
        self.assertEqual(MOF_DATA_TYPE.parse(TEST_STRING), TEST_TYPE_STRING)

    def test_parse_bool(self) -> None:
        """Test parsing of an boolean type"""
        self.assertEqual(MOF_DATA_TYPE.parse(TEST_BOOL), TEST_TYPE_BOOL)

    def test_parse_invalid_type(self) -> None:
        """Test parsing of an invalid type"""
        with self.assertRaises(ValueError):
            MOF_DATA_TYPE.parse(TEST_INVALID_TYPE)

    def test_parse_invalid_length(self) -> None:
        """Test parsing of an type with an invalid length"""
        with self.assertRaises(StreamError):
            MOF_DATA_TYPE.parse(TEST_INVALID_LENGTH)

    def test_build_int32_array(self) -> None:
        """Test building of an buffer containg an sint32 array type"""
        self.assertEqual(MOF_DATA_TYPE.build(TEST_TYPE_SINT32_ARRAY), TEST_SINT32_ARRAY)

    def test_build_object(self) -> None:
        """Test building of an buffer containg an object type"""
        self.assertEqual(MOF_DATA_TYPE.build(TEST_TYPE_OBJECT), TEST_OBJECT)

    def test_build_string(self) -> None:
        """Test building of an buffer containg an string type"""
        self.assertEqual(MOF_DATA_TYPE.build(TEST_TYPE_STRING), TEST_STRING)

    def test_build_bool(self) -> None:
        """Test building of an buffer containg an boolean type"""
        self.assertEqual(MOF_DATA_TYPE.build(TEST_TYPE_BOOL), TEST_BOOL)
