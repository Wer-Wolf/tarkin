#!/usr/bin/python3

"""Data parsing functions"""


from __future__ import annotations
from typing import Final
from construct import Switch, Mapping, GreedyString, Int32sl, Int32ul, Error, Adapter
from .type import DataType


class NullStripAdapter(Adapter):
    """Adapter for stripping null characters from strings"""
    def _decode(self, obj: str, context: object, path: object) -> str:
        """Strip null characters"""
        return obj.rstrip('\x00')

    def _encode(self, obj: str, context: object, path: object) -> str:
        """Do nothing"""
        return obj


MOF_DATA: Final = lambda data_type: Switch(
    data_type,
    {
        DataType.BOOLEAN: Mapping(Int32ul, {False: 0x0, True: 0xffff}),
        DataType.SINT32: Int32sl,
        DataType.STRING: NullStripAdapter(GreedyString("utf-16-le"))
    },
    default=Error
)
