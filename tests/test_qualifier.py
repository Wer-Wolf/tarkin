#!/usr/bin/python3

""""Tests for qualifier parsing"""

from __future__ import annotations
from unittest import TestCase
from tarkin.type import DataType
from tarkin.qualifier import Qualifier
from .data import load_test_data


class QualifierTest(TestCase):
    """Tests for qualifier parsing"""

    def test_bool(self) -> None:
        """Test parsing of an boolean qualifier"""
        qualifier = Qualifier.from_buffer(
            load_test_data("qualifier/bool.bin"),
            0xABCD
        )

        self.assertEqual(qualifier.name, "WMI")
        self.assertEqual(qualifier.data_type.basic_type, DataType.BOOLEAN)
        self.assertEqual(qualifier.data_type.is_array, False)
        self.assertEqual(qualifier.value, True)
        self.assertEqual(qualifier.offset, 0xABCD)

    def test_invalid_length(self) -> None:
        """Test parsing of an qualifier with an invalid length"""
        with self.assertRaises(ValueError):
            Qualifier.from_buffer(
                load_test_data("qualifier/invalid_length.bin"),
                0xABCD
            )

    def test_invalid_name(self) -> None:
        """Test parsing of an qualifier with an invalid name"""
        with self.assertRaises(ValueError):
            Qualifier.from_buffer(
                load_test_data("qualifier/invalid_name.bin"),
                0xABCD
            )
