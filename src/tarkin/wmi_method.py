#!/usr/bin/python3

"""WMI method parser"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .wmi_property import WmiProperty
from .wmi_qualifier import WmiQualifier
from .wmi_type import WmiType


@dataclass(frozen=True, slots=True)
class WmiMethod:
    """WMI method"""

    name: str

    parameters: Optional[list[WmiProperty]]

    qualifiers: Optional[list[WmiQualifier]]

    return_type: Optional[WmiType]

    @classmethod
    def from_properties(cls, name: str, input_params: list[WmiProperty],
                        output_params: list[WmiProperty], qualifiers: list[WmiQualifier]):
        """Create WMI method with input and output parameters"""
        params = {}
        return_type: Optional[WmiType] = None

        for prop in input_params:
            params[prop.name] = prop

        for prop in output_params:
            if prop.name == "ReturnValue":
                return_type = prop.data_type
            elif prop.name in params:
                param = params[prop.name]

                if param.data_type != prop.data_type:
                    raise RuntimeError(f"Parameter {param.name} contains different data types")

                if param.value != prop.value:
                    raise RuntimeError(f"Parameter {param.name} contains different values")

                if prop.qualifiers is None:
                    continue

                if param.qualifiers is None:
                    param.qualifiers = []

                for qualifier in prop.qualifiers:
                    if qualifier.name not in map(lambda p: p.name, param.qualifiers):
                        param.qualifiers.append(qualifier)
            else:
                params[prop.name] = prop

        return cls(
            name=name,
            parameters=params.values(),
            qualifiers=qualifiers,
            return_type=return_type
        )
