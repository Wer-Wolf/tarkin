#!/usr/bin/python3

"""WMI data parser"""


from __future__ import annotations
from typing import Callable, TypeAlias
from construct import Switch, Mapping, Int32sl, Int32ul, Error, CString, RawCopy, Prefixed, \
    GreedyBytes, Container, ExprAdapter, IfThenElse, FocusedSeq, Const, Array, Rebuild
from .wmi_type import WmiDataType, WmiType


WmiData: TypeAlias = bool | int | str | bytes | list[bool] | list[int] | list[str] | list[bytes]


class BmofWmiSingleData(Switch):
    # pylint: disable=abstract-method
    """Parse single WMI data item"""
    def __init__(self, data_type: Callable[[Container], WmiType]) -> None:
        super().__init__(
            lambda context: data_type(context).basic_type,
            {
                WmiDataType.BOOLEAN: Mapping(Int32ul, {False: 0x0, True: 0xffff}),
                WmiDataType.UINT32: Int32ul,
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


class BmofWmiData(IfThenElse):
    # pylint: disable=abstract-method
    """Parse WMI data item"""
    def __init__(self, data_type: Callable[[Container], WmiType]) -> None:
        super().__init__(
            lambda context: data_type(context).is_array,
            Prefixed(
                Int32ul,
                FocusedSeq(
                    "items",
                    "unknown" / Const(0x1, Int32ul),
                    "count" / Rebuild(
                        Int32ul,
                        lambda context: len(context.items)
                    ),
                    "items" / Prefixed(
                        Int32ul,
                        Array(
                            lambda context: context.count,
                            BmofWmiSingleData(
                                lambda context: data_type(context._)
                            )
                        ),
                        includelength=True
                    )
                ),
                includelength=True
            ),
            BmofWmiSingleData(
                data_type
            )
        )
