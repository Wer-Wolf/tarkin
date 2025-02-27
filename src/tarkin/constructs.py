#!/usr/bin/python3

"""Common BMOF constructs"""

from __future__ import annotations
from typing import Callable
from construct import Construct, Container, Int32ul, Prefixed, PrefixedArray, IfThenElse, \
    Pointer, Pass


class BmofArray(Prefixed):
    # pylint: disable=abstract-method
    """"
    BMOF array containing BMOF substructures.

    The array contains a header containing the following fields:
     - A 32-bit little endian length field specifying the length of the whole array
       (including the header) in bytes
     - A 32-bit little endian count field specifying the number of array entries
       following after the header

    Keyword arguments:
    subcon -- Subconstruct describing an array entry
    """
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
    """
    Heap reference to a substructure inside a heap.

    Various structures using by the BMOF format contain a so-called heap. This heap
    is an area inside the binary data buffer used to hold various substructures associated
    with the enclosing structure.
    A heap reference is used to refer to those substructures by using an offset pointing
    into the heap. The special value 0xFFFFFFFF is used to signal that the substructure
    associated with this heap reference does not exist.

    Keyword arguments:
    offset -- callable returning the offset of the substructure inside the heap
    subcon -- subconstruct describing the substructure inside the heap
    """
    def __init__(self, offset: Callable[[Container], int], subcon: Construct) -> None:
        super().__init__(
            lambda context: offset(context) != 0xFFFFFFFF,  # subcon does exist
            Pointer(
                offset,
                subcon
            ),
            Pass
        )
