#!/usr/bin/python3

""""Tests for qualifier parsing"""

from __future__ import annotations
from unittest import TestCase
from typing import Final
from construct import StreamError, StringError, TerminatedError
from tarkin.type import Type, DataType
from tarkin.qualifier import Qualifier, MOF_QUALIFIERS
from .data import load_test_data


TEST_QUALIFIERS_SINGLE: Final = [
    Qualifier(
        name="WMI",
        data_type=Type(
            basic_type=DataType.BOOLEAN,
            is_array=False
        ),
        value=True,
        offset=8
    )
]
TEST_QUALIFIERS_MULTIPLE: Final = [
    Qualifier(
        name="WMI",
        data_type=Type(
            basic_type=DataType.BOOLEAN,
            is_array=False
        ),
        value=True,
        offset=8
    ),
    Qualifier(
        name="TEST",
        data_type=Type(
            basic_type=DataType.SINT32,
            is_array=False
        ),
        value=0x04030201,
        offset=36
    )
]


class QualifierTest(TestCase):
    """Tests for qualifier parsing"""

    def test_parse_single(self) -> None:
        """Test parsing of an buffer containing a single qualifier"""
        qualifiers = MOF_QUALIFIERS.parse(load_test_data("qualifier/single.bin"))

        self.assertEqual(qualifiers, TEST_QUALIFIERS_SINGLE)

    def test_parse_invalid_length(self) -> None:
        """Test parsing of an buffer containing an invalid length"""
        with self.assertRaises(StreamError):
            MOF_QUALIFIERS.parse(
                load_test_data("qualifier/invalid_length.bin")
            )

    def test_parse_small_count(self) -> None:
        """Test parsing of an buffer containing a too small count"""
        with self.assertRaises(TerminatedError):
            MOF_QUALIFIERS.parse(
                load_test_data("qualifier/small_count.bin")
            )

    def test_parse_big_count(self) -> None:
        """Test parsing of an buffer containing a too big count"""
        with self.assertRaises(StreamError):
            MOF_QUALIFIERS.parse(
                load_test_data("qualifier/big_count.bin")
            )

    def test_parse_single_big_length(self) -> None:
        """Test parsing of an buffer containing a single qualifier with a too big length"""
        with self.assertRaises(TerminatedError):
            MOF_QUALIFIERS.parse(
                load_test_data("qualifier/single_big_length.bin")
            )

    def test_parse_single_invalid_name(self) -> None:
        """Test parsing of an buffer containing a single qualifier with an invalid name"""
        with self.assertRaises(StringError):
            MOF_QUALIFIERS.parse(
                load_test_data("qualifier/single_invalid_name.bin")
            )

    def test_parse_multiple(self) -> None:
        """Test parsing of an buffer containing multiple qualifiers"""
        qualifiers = MOF_QUALIFIERS.parse(load_test_data("qualifier/multiple.bin"))

        self.assertEqual(qualifiers, TEST_QUALIFIERS_MULTIPLE)
