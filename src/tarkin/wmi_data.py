#!/usr/bin/python3

"""WMI data parser"""


from __future__ import annotations
from typing import Final
from construct import Switch, Mapping, GreedyString, Int32sl, Int32ul, Error, Adapter, Container
from .wmi_type import WmiDataType


class NullStripAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for stripping null characters from strings"""
    def _decode(self, obj: str, context: Container, path: str) -> str:
        """Strip null characters"""
        return obj.rstrip('\x00')

    def _encode(self, obj: str, context: Container, path: str) -> str:
        """Do nothing"""
        return obj


BMOF_WMI_DATA: Final = lambda data_type: Switch(
    data_type,
    {
        WmiDataType.BOOLEAN: Mapping(Int32ul, {False: 0x0, True: 0xffff}),
        WmiDataType.SINT32: Int32sl,
        WmiDataType.STRING: NullStripAdapter(GreedyString("utf-16-le"))
    },
    default=Error
)
