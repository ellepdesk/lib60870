import logging
import ctypes
from ctypes import c_int, c_uint64, c_void_p, c_bool, c_uint8, c_char

from lib60870 import lib60870
from lib60870 import information_object
from lib60870.common import ConnectionParameters, default_connection_parameters
from lib60870.lib60870 import CauseOfTransmission, TypeID, QualityDescriptor

lib = lib60870.get_library()
logger = logging.getLogger(__name__)


class ASDU(ctypes.Structure):
    _fields_ = [
        ("stackCreated", c_bool),
        ("parameters", pConnectionParameters),
        ("asdu", ctypes.POINTER(c_uint8)),
        ("asduHeaderLength", c_int),
        ("payload", ctypes.POINTER(c_uint8)),
        ("payloadSize", c_int),
        ]

    def __init__(self):
        self.stackCreated = c_bool(True)
        self.parameters = pConnectionParameters(ConnectionParameters())
        self.asdu = ctypes.POINTER(c_uint8)(ctypes.create_string_buffer(256))
        self.asduHeaderLength = c_int(0)
        self.payload = self.asdu
        self.payloadSize = 0

    def __del__(self):
        pass

    def __str__(self):
        return "ASDU: {}({})".format(self.get_type_id().name, self.get_number_of_elements())

    def __repr__(self):
        output = "{}(".format(type(self).__name__)
        output += ", ".join(["{}={}".format(field[0],  getattr(self, field[0])) for field in self._fields_])
        return output + ")"

    def is_test(self):
        lib.ASDU_isTest.restype = c_bool
        return lib.ASDU_isTest(self.pointer)

    def set_test(self, value):
        lib.ASDU_setTest(self.pointer, c_bool(value))

    def is_negative(self):
        lib.ASDU_isNegative.restype = c_bool
        return lib.ASDU_isNegative(self.pointer)

    def set_negative(self, value):
        lib.ASDU_setNegative(self.pointer, c_bool(value))

    def get_oa(self):
        lib.ASDU_getOA.restype = c_int
        return lib.ASDU_getOA(self.pointer)

    def get_cot(self):
        lib.ASDU_getCOT.restype = c_int
        value = lib.ASDU_getCOT(self.pointer)
        return lib60870.CauseOfTransmission(value)

    def set_cot(self, cot):
        lib.ASDU_setCOT(self.pointer, cot.c_value)

    def get_ca(self):
        lib.ASDU_getCA.restype = c_int
        return lib.ASDU_getCA(self.pointer)

    def set_ca(self, value):
        lib.ASDU_setCA(self.pointer, c_int(value))

    def get_type_id(self):
        lib.ASDU_getTypeID.restype = c_int
        value = lib.ASDU_getTypeID(self.pointer)
        return lib60870.TypeID(value)

    def is_sequence(self):
        lib.ASDU_isSequence.restype = c_bool
        return lib.ASDU_isSequence(self.pointer)

    def get_number_of_elements(self):
        lib.ASDU_getNumberOfElements.restype = c_int
        return lib.ASDU_getNumberOfElements(self.pointer)

    def get_element(self, index):
        lib.ASDU_getElement.restype = information_object.pInformationObject
        p_element = lib.ASDU_getElement(self.pointer, c_int(index))
        if p_element:
            return p_element.contents

    def get_upcasted_element(self, index):
        io_type = information_object.GetIoTypeFromTypeId(self.get_type_id())
        lib.ASDU_getElement.restype = ctypes.POINTER(io_type)
        io = lib.ASDU_getElement(self.pointer, c_int(index))
        return io.contents

    def add_information_object(self, io):
        if(self.get_type_id() != io.get_type_id()):
            raise ValueError("Cannot add InformationObject of type ({}) to ASDU of type({})"
                             "".format(io.get_type_id(), self.get_type_id()))
        io_type = information_object.GetIoTypeFromTypeId(io.get_type_id())
        lib.ASDU_addInformationObject.restype = c_bool
        return lib.ASDU_addInformationObject(self.pointer, ctypes.POINTER(io_type)(io))

    def get_elements(self):
        return [self.get_upcasted_element(index) for index in range(0, self.get_number_of_elements())]

    def get_buffer(self):
        size = self.asduHeaderLength + self.payloadSize
        return ctypes.string_at(self.asdu, size=size)

    @property
    def elements(self):
        return self.get_elements()

    @property
    def pointer(self):
        return pASDU(self)

pASDU = ctypes.POINTER(ASDU)


def ASDU_create_from_buffer(parameters, msg, msgLength):
    assert isinstance(parameters, ConnectionParameters)
    lib.ASDU_createFromBuffer.restype = pASDU
    p_asdu = lib.ASDU_createFromBuffer(
        parameters.pointer,
        ctypes.cast(msg, ctypes.POINTER(c_uint8)),
        c_int(msgLength))
    return p_asdu.contents
