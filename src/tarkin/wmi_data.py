#!/usr/bin/python3

"""WMI data parser"""


from __future__ import annotations
from typing import Callable
from construct import Switch, Mapping, Int8ul, Int8sl, Int16ul, Int16sl, Int32sl, Int32ul, \
    Int64ul, Int64sl, Float32l, Float64l, Error, CString, Prefixed, Container, IfThenElse, \
    FocusedSeq, Const, Array, Rebuild, LazyBound
from tarkin import wmi_object
from .wmi_type import WmiDataType, WmiType


type WmiData = bool \
    | int \
    | float \
    | str \
    | wmi_object.WmiObject \
    | list[bool] \
    | list[int] \
    | list[float] \
    | list[str] \
    | list[wmi_object.WmiObject]


class BmofWmiSingleData(Switch):
    # pylint: disable=abstract-method
    """Parse single WMI data item"""
    def __init__(self, data_type: Callable[[Container], WmiType]) -> None:
        super().__init__(
            lambda context: data_type(context).basic_type,
            {
                WmiDataType.BOOLEAN: Mapping(Int16ul, {False: 0x0, True: 0xffff}),
                WmiDataType.UINT8: Int8ul,
                WmiDataType.SINT8: Int8sl,
                WmiDataType.UINT16: Int16ul,
                WmiDataType.SINT16: Int16sl,
                WmiDataType.UINT32: Int32ul,
                WmiDataType.SINT32: Int32sl,
                WmiDataType.UINT64: Int64ul,
                WmiDataType.SINT64: Int64sl,
                WmiDataType.REAL32: Float32l,
                WmiDataType.REAL64: Float64l,
                WmiDataType.STRING: CString("utf_16_le"),
                # LazyBound is necessary because WMI data items are usually
                # already contained inside an object.
                WmiDataType.OBJECT: LazyBound(lambda: wmi_object.BMOF_WMI_OBJECT),
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
