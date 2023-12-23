#!/usr/bin/python3

""""Tests for data type parsing"""

from __future__ import annotations
from unittest import TestCase
from typing import Final
from tarkin.type import Type, DataType


TEST_INT32_ARRAY: Final = 0x2003
TEST_OBJECT: Final = 0x000d
TEST_STRING: Final = 0x0008
TEST_BOOL: Final = 0x000b

TEST_INVALID: Final = 0x00ff


class TypeTest(TestCase):
    """Tests for data type parsing"""

    def test_int32_array(self) -> None:
        """Test parsing of an int32 array type"""
        array = Type.from_int(TEST_INT32_ARRAY)

        self.assertEqual(array.basic_type, DataType.SINT32)
        self.assertEqual(array.is_array, True)

    def test_object(self) -> None:
        """Test parsing of an object type"""
        array = Type.from_int(TEST_OBJECT)

        self.assertEqual(array.basic_type, DataType.OBJECT)
        self.assertEqual(array.is_array, False)

    def test_string(self) -> None:
        """Test parsing of an string type"""
        array = Type.from_int(TEST_STRING)

        self.assertEqual(array.basic_type, DataType.STRING)
        self.assertEqual(array.is_array, False)

    def test_bool(self) -> None:
        """Test parsing of an boolean type"""
        array = Type.from_int(TEST_BOOL)

        self.assertEqual(array.basic_type, DataType.BOOLEAN)
        self.assertEqual(array.is_array, False)

    def test_invalid(self) -> None:
        """Test parsing of an invalid type"""
        with self.assertRaises(ValueError):
            Type.from_int(TEST_INVALID)
