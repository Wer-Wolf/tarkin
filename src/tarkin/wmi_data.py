#!/usr/bin/python3

"""WMI data parser"""


from __future__ import annotations
from typing import Callable
from construct import Switch, Mapping, Int32sl, Int32ul, Error, CString, RawCopy, Prefixed, \
    GreedyBytes, Container, ExprAdapter
from .wmi_type import WmiDataType


class BmofWmiData(Switch):
    # pylint: disable=abstract-method
    """Parse WMI data item"""
    def __init__(self, data_type: Callable[[Container], WmiDataType]) -> None:
        super().__init__(
            data_type,
            {
                WmiDataType.BOOLEAN: Mapping(Int32ul, {False: 0x0, True: 0xffff}),
                WmiDataType.SINT32: Int32sl,
                WmiDataType.STRING: CString("utf_16_le"),
                # We cannot directly use BMOF_WMI_OBJECT here due to cyclical imports :(
                WmiDataType.OBJECT: ExprAdapter(
                    RawCopy(
                        Prefixed(
                            Int32ul,
                            GreedyBytes,
                            includelength=True
                        )
                    ),
                    lambda obj, context: obj["data"],
                    lambda obj, context: obj
                )
            },
            default=Error
        )
