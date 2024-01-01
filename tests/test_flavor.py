#!/usr/bin/python3

""""Tests for qualifier flavor parsing"""

from __future__ import annotations
from unittest import TestCase
from typing import Final
from construct import ConstError, StreamError, ValidationError
from tarkin.flavor import Flavors, QualifierFlavor, MOF_FLAVORS
from .data import load_test_data


TEST_FLAVORS_SINGLE: Final = [
    QualifierFlavor(
        offset=0xdead,
        flavors=Flavors.TO_INSTANCE | Flavors.AMENDED
    )
]

TEST_FLAVORS_MULTIPLE: Final = [
    QualifierFlavor(
        offset=0x18c,
        flavors=Flavors.TO_INSTANCE | Flavors.TO_SUBCLASS
    ),
    QualifierFlavor(
        offset=0x208,
        flavors=Flavors.TO_INSTANCE | Flavors.TO_SUBCLASS
    ),
    QualifierFlavor(
        offset=0x374,
        flavors=Flavors.TO_INSTANCE | Flavors.DISABLE_OVERRIDE
    ),
    QualifierFlavor(
        offset=0x390,
        flavors=Flavors.TO_INSTANCE | Flavors.TO_SUBCLASS
    ),
]


class QualifierFlavorTest(TestCase):
    """Tests for qualifier flavor parsing"""

    def test_parse_single(self) -> None:
        """Test parsing of an buffer containing a single qualifier flavor"""
        flavors = MOF_FLAVORS.parse(load_test_data("flavor/single.bin"))

        self.assertEqual(flavors, TEST_FLAVORS_SINGLE)

    def test_parse_single_invalid_offset(self) -> None:
        """Test parsing of an qualifier flavor with an invalid offset"""
        with self.assertRaises(ValidationError):
            MOF_FLAVORS.parse(load_test_data("flavor/single_invalid_offset.bin"))

    def test_parse_single_invalid_flags(self) -> None:
        """Test parsing of an qualifier flavor with invalid flags"""
        with self.assertRaises(ValueError):
            MOF_FLAVORS.parse(load_test_data("flavor/single_invalid_flags.bin"))

    def test_parse_multiple(self) -> None:
        """Test parsing of an buffer containing multiple qualifier flavor"""
        flavors = MOF_FLAVORS.parse(load_test_data("flavor/multiple.bin"))

        self.assertEqual(flavors, TEST_FLAVORS_MULTIPLE)

    def test_parse_buffer_invalid_magic(self) -> None:
        """Test parsing of an qualifier buffer with an invalid magic header"""
        with self.assertRaises(ConstError):
            MOF_FLAVORS.parse(load_test_data("flavor/buffer_invalid_magic.bin"))

    def test_parse_buffer_invalid_count(self) -> None:
        """Test parsing of an qualifier buffer with its item count being too big"""
        with self.assertRaises(StreamError):
            MOF_FLAVORS.parse(load_test_data("flavor/buffer_invalid_count.bin"))

    def test_parse_buffer_invalid_length(self) -> None:
        """Test parsing of an qualifier buffer with its length being too small"""
        with self.assertRaises(StreamError):
            MOF_FLAVORS.parse(load_test_data("flavor/buffer_invalid_length.bin"))

    def test_build_single(self) -> None:
        """Test building of an buffer containing a single qualifier flavor"""
        buffer = MOF_FLAVORS.build(TEST_FLAVORS_SINGLE)

        self.assertEqual(buffer, load_test_data("flavor/single.bin"))

    def test_build_multiple(self) -> None:
        """Test building of an buffer containing multiple qualifier flavor"""
        buffer = MOF_FLAVORS.build(TEST_FLAVORS_MULTIPLE)

        self.assertEqual(buffer, load_test_data("flavor/multiple.bin"))
