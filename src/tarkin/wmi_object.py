#!/usr/bin/python3

"""WMI object parser"""

from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum, unique, STRICT
from typing import Final, Optional, Iterable
from construct import Struct, Container, Adapter, Int32ul, Prefixed, Tell
from .constructs import BmofArray, BmofHeapReference
from .wmi_type import WmiDataType
from .wmi_method import WmiMethod
from .wmi_property import BMOF_WMI_PROPERTY, WmiProperty
from .wmi_qualifier import BMOF_WMI_QUALIFIER, WmiQualifier


@unique
class WmiObjectType(IntEnum, boundary=STRICT):
    """WMI object types"""
    CLASS = 0
    INSTANCE = 1


def validate_parameter_object(obj: WmiObject):
    """Validate that a given object is a parameter object"""
    if obj.object_type != WmiObjectType.INSTANCE:
        raise RuntimeError("Parameter object is not an instance")

    if obj.name != "__PARAMETERS":
        raise RuntimeError(f"Parameter object has unknown name: {obj.name}")

    if obj.qualifiers is not None:
        if len(obj.qualifiers) != 0:
            raise RuntimeError("Parameter object contains qualifiers")

    if obj.methods is not None:
        if len(obj.methods) != 0:
            raise RuntimeError("Parameter object contains methods")


def parse_method(prop: WmiProperty) -> WmiMethod:
    """Parse a WMI method from a special WMI property"""
    if prop.data_type.basic_type != WmiDataType.OBJECT:
        raise RuntimeError("Method property does not contain objects")

    if not prop.data_type.is_array:
        raise RuntimeError("Method property does not contain multiple objects")

    if len(prop.value) != 2:
        raise RuntimeError(f"Method property contains a invalid number of objects: {prop.value}")

    input_params: WmiObject = prop.value[0]
    validate_parameter_object(input_params)

    output_params: WmiObject = prop.value[1]
    validate_parameter_object(output_params)

    return WmiMethod.from_properties(prop.name, input_params.variables, output_params.variables,
                                     prop.qualifiers)


@dataclass(frozen=True, slots=True)
class WmiObject:
    """WMI object"""

    object_type: WmiObjectType

    qualifiers: Optional[list[WmiQualifier]]

    properties: Optional[list[WmiProperty]]

    methods: Optional[list[WmiMethod]]

    @classmethod
    def from_container(cls, container: Container) -> WmiObject:
        """Parse WMI object from container"""

        methods: Optional[list] = None

        if container["heap"]["methods"] is not None:
            methods = []
            for method in container["heap"]["methods"]:
                methods.append(parse_method(method))

        return cls(
            object_type=WmiObjectType(int(container["object_type"])),
            qualifiers=container["heap"]["qualifiers"],
            properties=container["heap"]["properties"],
            methods=methods
        )

    @property
    def name(self) -> Optional[str]:
        """Retrieve the class name"""
        if self.properties is None:
            return None

        for prop in self.properties:
            if prop.name != "__CLASS":
                continue

            if prop.data_type != WmiDataType.STRING:
                continue

            return prop.value

        return None

    @property
    def namespace(self) -> Optional[str]:
        """Retrieve the class namespace"""
        if self.properties is None:
            return None

        for prop in self.properties:
            if prop.name != "__NAMESPACE":
                continue

            if prop.data_type != WmiDataType.STRING:
                continue

            return prop.value

        return None

    @property
    def superclass(self) -> Optional[str]:
        """Retrieve the class superclass"""
        if self.properties is None:
            return None

        for prop in self.properties:
            if prop.name != "__SUPERCLASS":
                continue

            if prop.data_type != WmiDataType.STRING:
                continue

            return prop.value

        return None

    @property
    def flags(self) -> Optional[int]:
        """Retrieve the class flags"""
        if self.properties is None:
            return None

        for prop in self.properties:
            if prop.name != "__CLASSFLAGS":
                continue

            if prop.data_type != WmiDataType.SINT32:
                continue

            return prop.value

        return None

    @property
    def variables(self) -> Iterable[WmiProperty]:
        """Retrieve the class variables"""
        if self.properties is None:
            return

        for prop in self.properties:
            match prop.name:
                case "__CLASS" | "__NAMESPACE" | "__SUPERCLASS" | "__CLASSFLAGS":
                    continue
                case _:
                    yield prop


class WmiObjectAdapter(Adapter):
    # pylint: disable=abstract-method
    """Adapter for converting an container into a WMI object"""
    def _decode(self, obj: Container, context: Container, path: str) -> WmiObject:
        """Decode container to WMI object"""
        return WmiObject.from_container(obj)

    def _encode(self, obj: WmiObject, context: Container, path: str) -> Container:
        """Encode WMI object to container"""
        raise NotImplementedError("Object encoding is not yet implemented")


BMOF_WMI_OBJECT: Final = WmiObjectAdapter(
    Prefixed(
        Int32ul,
        Struct(
            "qualifiers_offset" / Int32ul,
            "properties_offset" / Int32ul,
            "methods_offset" / Int32ul,
            "object_type" / Int32ul,
            "heap" / Struct(
                "offset" / Tell,
                "qualifiers" / BmofHeapReference(
                    lambda context: min(context._.qualifiers_offset + context.offset, 0xFFFFFFFF),
                    BmofArray(
                        BMOF_WMI_QUALIFIER
                    )
                ),
                "properties" / BmofHeapReference(
                    lambda context: min(context._.properties_offset + context.offset, 0xFFFFFFFF),
                    BmofArray(
                        BMOF_WMI_PROPERTY
                    )
                ),
                "methods" / BmofHeapReference(
                    lambda context: min(context._.methods_offset + context.offset, 0xFFFFFFFF),
                    BmofArray(
                        BMOF_WMI_PROPERTY
                    )
                )
            )
        ),
        includelength=True
    )
)
