#!/usr/bin/python3

""""Tests for data parsing"""

from __future__ import annotations
from unittest import TestCase
from tarkin.type import Type, DataType
from tarkin.data import mof_parse_data
from .data import load_test_data


class DataTest(TestCase):
    """Tests for data parsing"""

    def test_bool(self) -> None:
        """Test parsing of boolean data"""
        data_type = Type(
            basic_type=DataType.BOOLEAN,
            is_array=False
        )
        boolean = mof_parse_data(data_type, load_test_data("data/bool.bin"))

        self.assertEqual(boolean, True)

    def test_sint32(self) -> None:
        """Test parsing of sint32 data"""
        data_type = Type(
            basic_type=DataType.SINT32,
            is_array=False
        )
        sint32 = mof_parse_data(data_type, load_test_data("data/sint32.bin"))

        self.assertEqual(sint32, 1398035268)

    def test_string(self) -> None:
        """Test parsing of string data"""
        data_type = Type(
            basic_type=DataType.STRING,
            is_array=False
        )
        string = mof_parse_data(data_type, load_test_data("data/string.bin"))

        self.assertEqual(string, "WMI")

    def test_bool_invalid(self) -> None:
        """Test parsing of invalid boolean data"""
        data_type = Type(
            basic_type=DataType.BOOLEAN,
            is_array=False
        )

        with self.assertRaises(ValueError):
            mof_parse_data(data_type, load_test_data("data/bool_invalid.bin"))

    def test_string_invalid(self) -> None:
        """Test parsing of invalid string data"""
        data_type = Type(
            basic_type=DataType.STRING,
            is_array=False
        )

        with self.assertRaises(UnicodeDecodeError):
            mof_parse_data(data_type, load_test_data("data/string_invalid.bin"))
