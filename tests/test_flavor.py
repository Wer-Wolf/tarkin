#!/usr/bin/python3

""""Tests for qualifier flavor parsing"""

from __future__ import annotations
from unittest import TestCase
from typing import Final
from tarkin.flavor import QualifierFlavor, flavors_from_buffer
from .data import load_test_data


TEST_FLAVORS: Final = [
    QualifierFlavor(
        offset=0x18c,
        to_instance=True,
        to_subclass=True,
        disable_override=False,
        amended=False
    ),
    QualifierFlavor(
        offset=0x208,
        to_instance=True,
        to_subclass=True,
        disable_override=False,
        amended=False
    ),
    QualifierFlavor(
        offset=0x374,
        to_instance=True,
        to_subclass=False,
        disable_override=True,
        amended=False
    ),
    QualifierFlavor(
        offset=0x390,
        to_instance=True,
        to_subclass=True,
        disable_override=False,
        amended=False
    ),
]


class QualifierFlavorTest(TestCase):
    """Tests for qualifier flavor parsing"""

    def test_single(self) -> None:
        """Test parsing of an single qualifier flavor"""
        flavor = QualifierFlavor.from_buffer(load_test_data("flavor/single.bin"))

        self.assertEqual(flavor.offset, 0x18c)
        self.assertEqual(flavor.to_instance, True)
        self.assertEqual(flavor.to_subclass, True)
        self.assertEqual(flavor.disable_override, False)
        self.assertEqual(flavor.amended, False)

    def test_single_invalid_offset(self) -> None:
        """Test parsing of an qualifier flavor with an invalid offset"""
        with self.assertRaises(ValueError):
            QualifierFlavor.from_buffer(load_test_data("flavor/single_invalid_offset.bin"))

    def test_single_invalid_flags(self) -> None:
        """Test parsing of an qualifier flavor with invalid flags"""
        with self.assertRaises(ValueError):
            QualifierFlavor.from_buffer(load_test_data("flavor/single_invalid_flags.bin"))

    def test_buffer(self) -> None:
        """Test parsing of an qualifier flavor buffer"""
        flavors = list(flavors_from_buffer(load_test_data("flavor/buffer.bin")))

        self.assertEqual(flavors, TEST_FLAVORS)

    def test_buffer_invalid(self) -> None:
        """Test parsing of an invalid qualifier flavor buffer"""
        with self.assertRaises(ValueError):
            list(flavors_from_buffer(load_test_data("flavor/buffer_invalid.bin")))
