#!/usr/bin/python3

""""Tests for variable parsing"""

from __future__ import annotations
from unittest import TestCase
from tarkin.type import Type, DataType
from tarkin.variable import Variable
from tarkin.qualifier import Qualifier
from .data import load_test_data


class VariableTest(TestCase):
    """Tests for variable parsing"""

    def test_instance_name(self) -> None:
        """Test parsing of an instance name variable"""
        test_qualifiers = [
            Qualifier(
                name="key",
                data_type=Type(
                    basic_type=DataType.BOOLEAN,
                    is_array=False
                ),
                value=True,
                offset=0x38
            ),
            Qualifier(
                name="read",
                data_type=Type(
                    basic_type=DataType.BOOLEAN,
                    is_array=False
                ),
                value=True,
                offset=0x54
            ),
            Qualifier(
                name="CIMTYPE",
                data_type=Type(
                    basic_type=DataType.STRING,
                    is_array=False
                ),
                value="string",
                offset=0x74
            )
        ]
        test_variable = Variable(
            name="InstanceName",
            data_type=Type(
                basic_type=DataType.STRING,
                is_array=False
            ),
            value=None,
            qualifiers=test_qualifiers
        )
        variable = Variable.from_buffer(
            load_test_data("variable/instance_name.bin"),
            0x00
        )

        self.assertEqual(variable, test_variable)
