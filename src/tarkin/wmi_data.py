#!/usr/bin/python3

"""WMI data parser"""


from __future__ import annotations
from typing import Final
from construct import Switch, Mapping, Int32sl, Int32ul, Error, CString
from .wmi_type import WmiDataType


BMOF_WMI_DATA: Final = lambda data_type: Switch(
    data_type,
    {
        WmiDataType.BOOLEAN: Mapping(Int32ul, {False: 0x0, True: 0xffff}),
        WmiDataType.SINT32: Int32sl,
        WmiDataType.STRING: CString("utf_16_le"),
    },
    default=Error
)
