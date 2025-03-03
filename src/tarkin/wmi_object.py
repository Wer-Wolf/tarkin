#!/usr/bin/python3

"""WMI object parser"""

from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum, IntFlag, unique, STRICT
from itertools import chain
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


@unique
class WmiClassFlags(IntFlag, boundary=STRICT):
    """WMI class flags"""
    UPDATEONLY = 1 << 0
    CREATEONLY = 1 << 1
    SAFEUPDATE = 1 << 5
    FORCEUPDATE = 1 << 6


@unique
class WmiInstanceFlags(IntFlag, boundary=STRICT):
    """WMI instance flags"""
    UPDATEONLY = 1 << 0
    CREATEONLY = 1 << 1


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
        return cls(
            object_type=WmiObjectType(int(container["object_type"])),
            qualifiers=container["heap"]["qualifiers"],
            properties=container["heap"]["properties"],
            methods=container["heap"]["methods"]
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
    def classflags(self) -> Optional[WmiClassFlags]:
        """Retrieve the class flags"""
        if self.properties is None:
            return None

        for prop in self.properties:
            if prop.name != "__CLASSFLAGS":
                continue

            if prop.data_type != WmiDataType.SINT32:
                continue

            return WmiClassFlags(prop.value)

        return None

    @property
    def instanceflags(self) -> Optional[WmiInstanceFlags]:
        """Retrieve the instance flags"""
        if self.properties is None:
            return None

        for prop in self.properties:
            if prop.name != "__INSTANCEFLAGS":
                continue

            if prop.data_type != WmiDataType.SINT32:
                continue

            return WmiInstanceFlags(prop.value)

        return None

    @property
    def variables(self) -> Iterable[WmiProperty]:
        """Retrieve the class variables"""
        if self.properties is None:
            return

        for prop in self.properties:
            match prop.name:
                case "__CLASS" | "__NAMESPACE" | "__SUPERCLASS" | "__CLASSFLAGS" \
                     | "__INSTANCEFLAGS":
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


class WmiMethodAdapter(Adapter):
    # pylint: disable=abstract-method
    """
    Adapter for converting an WMI property into a WMI method.

    A WMI method is encoded inside a WMI property. This property contains
    an array of WMI objects named "__PARAMETERS" holding the parameters of
    the WMI method. WMI method returning void and containing no additional
    parameters are instead encoded inside a WMI property having the void
    data type.
    """
    def _decode(self, obj: WmiProperty, context: Container, path: str) -> WmiMethod:
        """Decode container to WMI object"""
        if obj.data_type == WmiDataType.VOID:
            # void method with no arguments
            return WmiMethod.from_properties(obj.name, [], obj.qualifiers)

        if obj.data_type.basic_type != WmiDataType.OBJECT:
            raise RuntimeError("Method property does not contain objects")

        if not obj.data_type.is_array:
            raise RuntimeError("Method property is not an array")

        for param_obj in obj.value:
            if param_obj.object_type != WmiObjectType.INSTANCE:
                raise RuntimeError("Parameter object is not an instance")

            if param_obj.name != "__PARAMETERS":
                raise RuntimeError(f"Parameter object has unknown name: {param_obj.name}")

            if param_obj.qualifiers is not None:
                if len(param_obj.qualifiers) != 0:
                    raise RuntimeError("Parameter object contains qualifiers")

            if param_obj.methods is not None:
                if len(param_obj.methods) != 0:
                    raise RuntimeError("Parameter object contains methods")

        # The method property can contain up to two objects for input and output parameters
        params = chain.from_iterable(map(lambda o: o.variables, obj.value))

        return WmiMethod.from_properties(obj.name, params, obj.qualifiers)

    def _encode(self, obj: WmiMethod, context: Container, path: str) -> Container:
        """Encode WMI method to a WMI property"""
        raise NotImplementedError("Method encoding is not yet implemented")


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
                        WmiMethodAdapter(
                            BMOF_WMI_PROPERTY
                        )
                    )
                )
            )
        ),
        includelength=True
    )
)
"""
The BMOF object structure.

The BMOF object structure starts with a header containing the following fields:
 - A 32-bit little endian length value specifying the length of the whole object
   structure including the header in bytes
 - A 32-bit little endian heap reference to the qualifiers substructure
 - A 32-bit little endian heap reference to the properties substructure
 - A 32-bit little endian heap reference to the methods substructure
 - A 32-bit little endian field specfying the object type

The remaining bytes form the heap containing the qualifiers, properties and methods
substructures. Each substructure consists of a BMOF array containg the corresponding
qualifiers, properties and methods of the object encoded by the object strucutre.
Methods are encoded using special properties.
"""
