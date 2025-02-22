#!/usr/bin/python3

"""WMI method parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Iterable
from .wmi_property import WmiProperty
from .wmi_qualifier import WmiQualifier
from .wmi_type import WmiType, WmiDataType


@dataclass(frozen=True, slots=True)
class WmiMethod:
    """WMI method"""

    name: str

    parameters: Optional[list[WmiProperty]]

    qualifiers: Optional[list[WmiQualifier]]

    return_type: WmiType

    @classmethod
    def from_properties(cls, name: str, params: Iterable[WmiProperty],
                        qualifiers: list[WmiQualifier]):
        """Create WMI method from a list of possibly duplicated parameters"""
        return_type = WmiType.from_data_type(WmiDataType.VOID)
        final_params = {}

        for param in params:
            if param.name == "ReturnValue":
                return_type = param.data_type
            elif param.name in final_params:
                final_param = final_params[param.name]

                if final_param.data_type != param.data_type:
                    raise RuntimeError(f"Parameter {param.name} contains different data types")

                if final_param.value != param.value:
                    raise RuntimeError(f"Parameter {param.name} contains different values")

                if param.qualifiers is None:
                    continue

                if final_param.qualifiers is None:
                    final_param.qualifiers = []

                for qualifier in param.qualifiers:
                    if qualifier.name not in map(lambda p: p.name, final_param.qualifiers):
                        final_param.qualifiers.append(qualifier)
            else:
                final_params[param.name] = param

        return cls(
            name=name,
            parameters=final_params.values(),
            qualifiers=qualifiers,
            return_type=return_type
        )
