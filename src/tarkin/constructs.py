#!/usr/bin/python3

"""Common BMOF constructs"""

from __future__ import annotations
from construct import Construct, Int32ul, Prefixed, PrefixedArray


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
