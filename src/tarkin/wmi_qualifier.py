#!/usr/bin/python3

"""WMI qualifier parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Final, Optional
from construct import Struct, Container, Adapter, Int32ul, Tell, Prefixed, CString
from .constructs import BmofHeapReference
from .wmi_data import BmofWmiData, WmiData
from .wmi_type import BMOF_WMI_TYPE, WmiType


@dataclass(frozen=True, slots=True)
class WmiQualifier:
    """WMI qualifier"""

    data_type: WmiType

    name: Optional[str]

    value: Optional[WmiData]

    offset: int

    @classmethod
    def from_container(cls, container: Container) -> WmiQualifier:
        """Parse WMI qualifier from container"""
        return cls(
            data_type=container["qualifier"]["data_type"],
            name=container["qualifier"]["heap"]["name"],
            value=container["qualifier"]["heap"]["value"],
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
        raise NotImplementedError("Qualifier encoding is not yet implemented")


BMOF_WMI_QUALIFIER: Final = WmiQualifierAdapter(
    Struct(
        "offset" / Tell,
        "qualifier" / Prefixed(
            Int32ul,
            Struct(
                "data_type" / BMOF_WMI_TYPE,
                "name_offset" / Int32ul,
                "value_offset" / Int32ul,
                "heap" / Struct(
                    "offset" / Tell,
                    "name" / BmofHeapReference(
                        lambda context: min(context._.name_offset + context.offset, 0xFFFFFFFF),
                        CString("utf_16_le")
                    ),
                    "value" / BmofHeapReference(
                        lambda context: min(context._.value_offset + context.offset, 0xFFFFFFFF),
                        BmofWmiData(
                            lambda context: context._.data_type
                        )
                    )
                )
            ),
            includelength=True
        )
    )
)
