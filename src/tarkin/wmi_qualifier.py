#!/usr/bin/python3

"""WMI qualifier parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final
from construct import Struct, Container, Adapter, Const, Int32ul, PascalString, Tell
from .wmi_data import BMOF_WMI_DATA, NullStripAdapter
from .wmi_type import BMOF_WMI_TYPE, WmiType


@dataclass(frozen=True, slots=True)
class WmiQualifier:
    """WMI qualifier"""

    name: str

    data_type: WmiType

    value: bool | int | str

    offset: int

    @classmethod
    def from_container(cls, container: Container) -> WmiQualifier:
        """Parse WMI qualifier from container"""
        return cls(
            name=container["name"],
            data_type=container["data_type"],
            value=container["value"],
            offset=int(container["offset"])
        )


class WmiQualifierAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into a WMI qualifier"""
    def _decode(self, obj: Container, context: Container, path: str) -> WmiQualifier:
        """Decode container to a WMI qualifier"""
        return WmiQualifier.from_container(obj)

    def _encode(self, obj: WmiQualifier, context: Container, path: str) -> Container:
        """Encode WMI qualifier to container"""
        return Container(
            data_type=obj.data_type,
            name=obj.name,
            value=obj.value
        )


BMOF_WMI_QUALIFIER: Final = WmiQualifierAdapter(
    Struct(
        "offset" / Tell,    # TODO Needs to be before the length field
        "data_type" / BMOF_WMI_TYPE,
        "unknown" / Const(0, Int32ul),
        "name" / NullStripAdapter(
            PascalString(Int32ul, "utf-16-le")
        ),
        "value" / BMOF_WMI_DATA(
            lambda context: context.data_type
        )
    )
)
