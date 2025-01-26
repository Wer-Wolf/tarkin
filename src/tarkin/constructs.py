#!/usr/bin/python3

"""Common BMOF constructs"""

from __future__ import annotations
from typing import Callable
from construct import Construct, Container, Int32ul, Prefixed, PrefixedArray, IfThenElse, \
    Pointer, Pass


class BmofArray(Prefixed):
    # pylint: disable=abstract-method
    """Array prefixed with both 32-bit length and count fields"""
    def __init__(self, subcon: Construct) -> None:
        super().__init__(
            Int32ul,
            PrefixedArray(
                Int32ul,
                subcon
            ),
            includelength=True
        )


class BmofHeapReference(IfThenElse):
    # pylint: disable=abstract-method
    """Optional pointer reference to a heap subconstruct"""
    def __init__(self, offset: Callable[[Container], int], subcon: Construct) -> None:
        super().__init__(
            lambda context: offset(context) != 0xFFFFFFFF,  # subcon does exist
            Pointer(
                offset,
                subcon
            ),
            Pass
        )
