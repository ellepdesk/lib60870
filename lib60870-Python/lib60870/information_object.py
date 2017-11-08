import logging
from lib60870 import lib60870
from lib60870.common import *
from lib60870.CP16Time2a import CP16Time2a, pCP16Time2a
from lib60870.CP24Time2a import CP24Time2a, pCP24Time2a
from lib60870.CP56Time2a import CP56Time2a, pCP56Time2a

import ctypes
from ctypes import c_int, c_uint16, c_uint32, c_uint64, c_void_p, c_bool, c_uint8, c_void_p, c_float

lib = lib60870.get_library()
logger = logging.getLogger(__name__)

# type aliases
c_enum = c_int
QualityDescriptor = c_uint8
QualityDescriptorP = c_uint8
TypeID = c_enum
DoublePointValue = c_enum
StartEvent = c_uint8
OutputCircuitInfo = c_uint8
QualifierOfRPC = c_uint8
QualifierOfParameterActivation = c_uint8
pInformationObjectVFT = ctypes.c_void_p


class IOBase():
    """
    Python base class for all InformationObject-derived types
    Contains convenience functions for printing and common
    functions to retrieve the typeID and object address
    """
    def __str__(self):
        return "{}: {}, {}".format(type(self).__name__, self.get_type_id().name, self.get_object_address())

    def __repr__(self):
        output = "{}(".format(type(self).__name__)
        output += ", ".join(["{}={}".format(field[0],  repr(getattr(self, field[0]))) for field in self._fields_])
        return output + ")"

    def __del__(self):
        pass

    def get_type_id(self):
        return lib60870.TypeID(self.type)

    def get_object_address(self):
        return self.objectAddress

    def get_pointer_type(self):
        return ctypes.POINTER(type(self))


class StatusAndStatusChangeDetection(ctypes.Structure):
    _fields_ = [
        ('encodedValue', ctypes.c_uint8 * 4)
        ]

    def get_stn(self):
        lib.StatusAndStatusChangeDetection_getSTn.restype = c_uint16
        return lib.StatusAndStatusChangeDetection_getSTn(pStatusAndStatusChangeDetection(self))

    def get_cdn(self):
        lib.StatusAndStatusChangeDetection_getCDn.restype = c_uint16
        return lib.StatusAndStatusChangeDetection_getCDn(pStatusAndStatusChangeDetection(self))

    def set_stn(self, value):
        lib.StatusAndStatusChangeDetection_setSTn(
            pStatusAndStatusChangeDetection(self),
            c_uint16(value))

    def get_st(self, index):
        lib.StatusAndStatusChangeDetection_getST.restype = c_bool
        return lib.StatusAndStatusChangeDetection_getST(
            pStatusAndStatusChangeDetection(self),
            c_int(index))

    def get_cd(self, index):
        lib.StatusAndStatusChangeDetection_getCD.restype = c_bool
        return lib.StatusAndStatusChangeDetection_getCD(
            pStatusAndStatusChangeDetection(self),
            c_int(index))

pStatusAndStatusChangeDetection = ctypes.POINTER(StatusAndStatusChangeDetection)


class SingleEvent(ctypes.c_uint8):
    def set_event_state(self, eventState):
        lib.SingleEvent_setEventState(
            pSingleEvent(self),
            pEventState(eventState))

    def get_event_state(self):
        lib.SingleEvent_getEventState.restype = pEventState
        return lib.SingleEvent_getEventState(pSingleEvent(self))

    def set_qdp(self, qdp):
        lib.SingleEvent_setQDP(
            pSingleEvent(self),
            QualityDescriptorP(qdp))

    def get_qdp(self):
        lib.SingleEvent_getQDP.restype = QualityDescriptorP
        return lib.SingleEvent_getQDP(pSingleEvent(self))

pSingleEvent = ctypes.POINTER(SingleEvent)


class InformationObject(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = c_void_p
        self.type = lib60870.TypeID.INVALID.c_enum

    def get_object_address(self):
        lib.InformationObject_getObjectAddress.restype = c_int
        return lib.InformationObject_getObjectAddress(pInformationObject(self))

    def set_object_address(self, ioa):
        lib.InformationObject_setObjectAddress(
            pInformationObject(self),
            c_int(ioa))

    def encode_base(self, frame, parameters, isSequence):
        lib.InformationObject_encodeBase(
            pInformationObject(self),
            pFrame(frame),
            pConnectionParameters(parameters),
            c_bool(isSequence))

    def parse_object_address(parameters, msg, startIndex):
        lib.InformationObject_ParseObjectAddress.restype = c_int
        return lib.InformationObject_ParseObjectAddress(
            pConnectionParameters(parameters),
            ctypes.POINTER(c_uint8)(msg),
            c_int(startIndex))

pInformationObject = ctypes.POINTER(InformationObject)


class SinglePointInformation(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', c_bool),
        ('quality', QualityDescriptor)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.singlePointInformationVFT, c_void_p)
        self.type = lib60870.TypeID.M_SP_NA_1.c_enum

    def get_value(self):
        lib.SinglePointInformation_getValue.restype = c_bool
        return lib.SinglePointInformation_getValue(pSinglePointInformation(self))

    def get_quality(self):
        lib.SinglePointInformation_getQuality.restype = QualityDescriptor
        return lib.SinglePointInformation_getQuality(pSinglePointInformation(self))

pSinglePointInformation = ctypes.POINTER(SinglePointInformation)


class SinglePointWithCP24Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', c_bool),
        ('quality', QualityDescriptor),
        ('timestamp', CP24Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.singlePointWithCP24Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_SP_TA_1.c_enum

    def get_timestamp(self):
        lib.SinglePointWithCP24Time2a_getTimestamp.restype = pCP24Time2a
        return lib.SinglePointWithCP24Time2a_getTimestamp(pSinglePointWithCP24Time2a(self))

pSinglePointWithCP24Time2a = ctypes.POINTER(SinglePointWithCP24Time2a)


class DoublePointInformation(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', DoublePointValue),
        ('quality', QualityDescriptor)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.doublePointInformationVFT, c_void_p)
        self.type = lib60870.TypeID.M_DP_NA_1.c_enum

    def get_value(self):
        lib.DoublePointInformation_getValue.restype = DoublePointValue
        return lib.DoublePointInformation_getValue(pDoublePointInformation(self))

    def get_quality(self):
        lib.DoublePointInformation_getQuality.restype = QualityDescriptor
        return lib.DoublePointInformation_getQuality(pDoublePointInformation(self))

pDoublePointInformation = ctypes.POINTER(DoublePointInformation)


class DoublePointWithCP24Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', DoublePointValue),
        ('quality', QualityDescriptor),
        ('timestamp', CP24Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.doublePointWithCP24Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_DP_TA_1.c_enum

    def get_timestamp(self):
        lib.DoublePointWithCP24Time2a_getTimestamp.restype = pCP24Time2a
        return lib.DoublePointWithCP24Time2a_getTimestamp(pDoublePointWithCP24Time2a(self))

pDoublePointWithCP24Time2a = ctypes.POINTER(DoublePointWithCP24Time2a)


class StepPositionInformation(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('vti', c_uint8),
        ('quality', QualityDescriptor)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.stepPositionInformationVFT, c_void_p)
        self.type = lib60870.TypeID.M_ST_NA_1.c_enum

    def get_object_address(self):
        lib.StepPositionInformation_getObjectAddress.restype = c_int
        return lib.StepPositionInformation_getObjectAddress(pStepPositionInformation(self))

    def get_value(self):
        lib.StepPositionInformation_getValue.restype = c_int
        return lib.StepPositionInformation_getValue(pStepPositionInformation(self))

    def is_transient(self):
        lib.StepPositionInformation_isTransient.restype = c_bool
        return lib.StepPositionInformation_isTransient(pStepPositionInformation(self))

    def get_quality(self):
        lib.StepPositionInformation_getQuality.restype = QualityDescriptor
        return lib.StepPositionInformation_getQuality(pStepPositionInformation(self))

pStepPositionInformation = ctypes.POINTER(StepPositionInformation)


class StepPositionWithCP24Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('vti', c_uint8),
        ('quality', QualityDescriptor),
        ('timestamp', CP24Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.stepPositionWithCP24Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_ST_TA_1.c_enum

    def get_timestamp(self):
        lib.StepPositionWithCP24Time2a_getTimestamp.restype = pCP24Time2a
        return lib.StepPositionWithCP24Time2a_getTimestamp(pStepPositionWithCP24Time2a(self))

pStepPositionWithCP24Time2a = ctypes.POINTER(StepPositionWithCP24Time2a)


class BitString32(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', c_uint32),
        ('quality', QualityDescriptor)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.bitString32VFT, c_void_p)
        self.type = lib60870.TypeID.M_BO_NA_1.c_enum

    def get_value(self):
        lib.BitString32_getValue.restype = c_uint32
        return lib.BitString32_getValue(pBitString32(self))

    def get_quality(self):
        lib.BitString32_getQuality.restype = QualityDescriptor
        return lib.BitString32_getQuality(pBitString32(self))

pBitString32 = ctypes.POINTER(BitString32)


class Bitstring32WithCP24Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', c_uint32),
        ('quality', QualityDescriptor),
        ('timestamp', CP24Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.bitstring32WithCP24Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_BO_TA_1.c_enum

    def get_timestamp(self):
        lib.Bitstring32WithCP24Time2a_getTimestamp.restype = pCP24Time2a
        return lib.Bitstring32WithCP24Time2a_getTimestamp(pBitstring32WithCP24Time2a(self))

pBitstring32WithCP24Time2a = ctypes.POINTER(Bitstring32WithCP24Time2a)


class MeasuredValueNormalized(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('encodedValue', ctypes.c_uint8 * 2),
        ('quality', QualityDescriptor)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.measuredValueNormalizedVFT, c_void_p)
        self.type = lib60870.TypeID.M_ME_NA_1.c_enum

    def get_value(self):
        lib.MeasuredValueNormalized_getValue.restype = c_float
        return lib.MeasuredValueNormalized_getValue(pMeasuredValueNormalized(self))

    def set_value(self, value):
        lib.MeasuredValueNormalized_setValue(
            pMeasuredValueNormalized(self),
            c_float(value))

    def get_quality(self):
        lib.MeasuredValueNormalized_getQuality.restype = QualityDescriptor
        return lib.MeasuredValueNormalized_getQuality(pMeasuredValueNormalized(self))

pMeasuredValueNormalized = ctypes.POINTER(MeasuredValueNormalized)


class MeasuredValueNormalizedWithCP24Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('encodedValue', ctypes.c_uint8 * 2),
        ('quality', QualityDescriptor),
        ('timestamp', CP24Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.measuredValueNormalizedWithCP24Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_ME_TA_1.c_enum

    def get_timestamp(self):
        lib.MeasuredValueNormalizedWithCP24Time2a_getTimestamp.restype = pCP24Time2a
        return lib.MeasuredValueNormalizedWithCP24Time2a_getTimestamp(pMeasuredValueNormalizedWithCP24Time2a(self))

    def set_timestamp(self, value):
        lib.MeasuredValueNormalizedWithCP24Time2a_setTimestamp(
            pMeasuredValueNormalizedWithCP24Time2a(self),
            pCP24Time2a(value))

pMeasuredValueNormalizedWithCP24Time2a = ctypes.POINTER(MeasuredValueNormalizedWithCP24Time2a)


class MeasuredValueScaled(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('encodedValue', ctypes.c_uint8 * 2),
        ('quality', QualityDescriptor)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.measuredValueScaledVFT, c_void_p)
        self.type = lib60870.TypeID.M_ME_NB_1.c_enum

    def get_value(self):
        lib.MeasuredValueScaled_getValue.restype = c_int
        return lib.MeasuredValueScaled_getValue(pMeasuredValueScaled(self))

    def set_value(self, value):
        lib.MeasuredValueScaled_setValue(
            pMeasuredValueScaled(self),
            c_int(value))

    def get_quality(self):
        lib.MeasuredValueScaled_getQuality.restype = QualityDescriptor
        return lib.MeasuredValueScaled_getQuality(pMeasuredValueScaled(self))

    def set_quality(self, quality):
        lib.MeasuredValueScaled_setQuality(
            pMeasuredValueScaled(self),
            QualityDescriptor(quality))

pMeasuredValueScaled = ctypes.POINTER(MeasuredValueScaled)


class MeasuredValueScaledWithCP24Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('encodedValue', ctypes.c_uint8 * 2),
        ('quality', QualityDescriptor),
        ('timestamp', CP24Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.measuredValueScaledWithCP24Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_ME_TB_1.c_enum

    def get_timestamp(self):
        lib.MeasuredValueScaledWithCP24Time2a_getTimestamp.restype = pCP24Time2a
        return lib.MeasuredValueScaledWithCP24Time2a_getTimestamp(pMeasuredValueScaledWithCP24Time2a(self))

    def set_timestamp(self, value):
        lib.MeasuredValueScaledWithCP24Time2a_setTimestamp(
            pMeasuredValueScaledWithCP24Time2a(self),
            pCP24Time2a(value))

pMeasuredValueScaledWithCP24Time2a = ctypes.POINTER(MeasuredValueScaledWithCP24Time2a)


class MeasuredValueShort(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', c_float),
        ('quality', QualityDescriptor)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.measuredValueShortVFT, c_void_p)
        self.type = lib60870.TypeID.M_ME_NC_1.c_enum

    def get_value(self):
        lib.MeasuredValueShort_getValue.restype = c_float
        return lib.MeasuredValueShort_getValue(pMeasuredValueShort(self))

    def set_value(self, value):
        lib.MeasuredValueShort_setValue(
            pMeasuredValueShort(self),
            c_float(value))

    def get_quality(self):
        lib.MeasuredValueShort_getQuality.restype = QualityDescriptor
        return lib.MeasuredValueShort_getQuality(pMeasuredValueShort(self))

pMeasuredValueShort = ctypes.POINTER(MeasuredValueShort)


class MeasuredValueShortWithCP24Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', c_float),
        ('quality', QualityDescriptor),
        ('timestamp', CP24Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.measuredValueShortWithCP24Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_ME_TC_1.c_enum

    def get_timestamp(self):
        lib.MeasuredValueShortWithCP24Time2a_getTimestamp.restype = pCP24Time2a
        return lib.MeasuredValueShortWithCP24Time2a_getTimestamp(pMeasuredValueShortWithCP24Time2a(self))

    def set_timestamp(self, value):
        lib.MeasuredValueShortWithCP24Time2a_setTimestamp(
            pMeasuredValueShortWithCP24Time2a(self),
            pCP24Time2a(value))

pMeasuredValueShortWithCP24Time2a = ctypes.POINTER(MeasuredValueShortWithCP24Time2a)


class IntegratedTotals(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('totals', BinaryCounterReading)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.integratedTotalsVFT, c_void_p)
        self.type = lib60870.TypeID.M_IT_NA_1.c_enum

    def get_bcr(self):
        lib.IntegratedTotals_getBCR.restype = pBinaryCounterReading
        return lib.IntegratedTotals_getBCR(pIntegratedTotals(self))

    def set_bcr(self, value):
        lib.IntegratedTotals_setBCR(
            pIntegratedTotals(self),
            pBinaryCounterReading(value))

pIntegratedTotals = ctypes.POINTER(IntegratedTotals)


class IntegratedTotalsWithCP24Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('totals', BinaryCounterReading),
        ('timestamp', CP24Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.integratedTotalsWithCP24Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_IT_TA_1.c_enum

    def get_timestamp(self):
        lib.IntegratedTotalsWithCP24Time2a_getTimestamp.restype = pCP24Time2a
        return lib.IntegratedTotalsWithCP24Time2a_getTimestamp(pIntegratedTotalsWithCP24Time2a(self))

    def set_timestamp(self, value):
        lib.IntegratedTotalsWithCP24Time2a_setTimestamp(
            pIntegratedTotalsWithCP24Time2a(self),
            pCP24Time2a(value))

pIntegratedTotalsWithCP24Time2a = ctypes.POINTER(IntegratedTotalsWithCP24Time2a)


class EventOfProtectionEquipment(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('event', SingleEvent),
        ('elapsedTime', CP16Time2a),
        ('timestamp', CP24Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.eventOfProtectionEquipmentVFT, c_void_p)
        self.type = lib60870.TypeID.M_EP_TA_1.c_enum

    def get_event(self):
        lib.EventOfProtectionEquipment_getEvent.restype = pSingleEvent
        return lib.EventOfProtectionEquipment_getEvent(pEventOfProtectionEquipment(self))

    def get_elapsed_time(self):
        lib.EventOfProtectionEquipment_getElapsedTime.restype = pCP16Time2a
        return lib.EventOfProtectionEquipment_getElapsedTime(pEventOfProtectionEquipment(self))

    def get_timestamp(self):
        lib.EventOfProtectionEquipment_getTimestamp.restype = pCP24Time2a
        return lib.EventOfProtectionEquipment_getTimestamp(pEventOfProtectionEquipment(self))

pEventOfProtectionEquipment = ctypes.POINTER(EventOfProtectionEquipment)


class PackedStartEventsOfProtectionEquipment(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('event', StartEvent),
        ('qdp', QualityDescriptorP),
        ('elapsedTime', CP16Time2a),
        ('timestamp', CP24Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.packedStartEventsOfProtectionEquipmentVFT, c_void_p)
        self.type = lib60870.TypeID.M_EP_TB_1.c_enum

    def get_event(self):
        lib.PackedStartEventsOfProtectionEquipment_getEvent.restype = StartEvent
        return lib.PackedStartEventsOfProtectionEquipment_getEvent(pPackedStartEventsOfProtectionEquipment(self))

    def get_quality(self):
        lib.PackedStartEventsOfProtectionEquipment_getQuality.restype = QualityDescriptorP
        return lib.PackedStartEventsOfProtectionEquipment_getQuality(pPackedStartEventsOfProtectionEquipment(self))

    def get_elapsed_time(self):
        lib.PackedStartEventsOfProtectionEquipment_getElapsedTime.restype = pCP16Time2a
        return lib.PackedStartEventsOfProtectionEquipment_getElapsedTime(pPackedStartEventsOfProtectionEquipment(self))

    def get_timestamp(self):
        lib.PackedStartEventsOfProtectionEquipment_getTimestamp.restype = pCP24Time2a
        return lib.PackedStartEventsOfProtectionEquipment_getTimestamp(pPackedStartEventsOfProtectionEquipment(self))

pPackedStartEventsOfProtectionEquipment = ctypes.POINTER(PackedStartEventsOfProtectionEquipment)


class PackedOutputCircuitInfo(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('oci', OutputCircuitInfo),
        ('qdp', QualityDescriptorP),
        ('operatingTime', CP16Time2a),
        ('timestamp', CP24Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.packedOutputCircuitInfoVFT, c_void_p)
        self.type = lib60870.TypeID.M_EP_TC_1.c_enum

    def get_oci(self):
        lib.PackedOutputCircuitInfo_getOCI.restype = OutputCircuitInfo
        return lib.PackedOutputCircuitInfo_getOCI(pPackedOutputCircuitInfo(self))

    def get_quality(self):
        lib.PackedOutputCircuitInfo_getQuality.restype = QualityDescriptorP
        return lib.PackedOutputCircuitInfo_getQuality(pPackedOutputCircuitInfo(self))

    def get_operating_time(self):
        lib.PackedOutputCircuitInfo_getOperatingTime.restype = pCP16Time2a
        return lib.PackedOutputCircuitInfo_getOperatingTime(pPackedOutputCircuitInfo(self))

    def get_timestamp(self):
        lib.PackedOutputCircuitInfo_getTimestamp.restype = pCP24Time2a
        return lib.PackedOutputCircuitInfo_getTimestamp(pPackedOutputCircuitInfo(self))

pPackedOutputCircuitInfo = ctypes.POINTER(PackedOutputCircuitInfo)


class PackedSinglePointWithSCD(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('scd', StatusAndStatusChangeDetection),
        ('qds', QualityDescriptor)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.packedSinglePointWithSCDVFT, c_void_p)
        self.type = lib60870.TypeID.M_PS_NA_1.c_enum

    def get_quality(self):
        lib.PackedSinglePointWithSCD_getQuality.restype = QualityDescriptor
        return lib.PackedSinglePointWithSCD_getQuality(pPackedSinglePointWithSCD(self))

    def get_scd(self):
        lib.PackedSinglePointWithSCD_getSCD.restype = pStatusAndStatusChangeDetection
        return lib.PackedSinglePointWithSCD_getSCD(pPackedSinglePointWithSCD(self))

pPackedSinglePointWithSCD = ctypes.POINTER(PackedSinglePointWithSCD)


class MeasuredValueNormalizedWithoutQuality(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('encodedValue', ctypes.c_uint8 * 2)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.measuredValueNormalizedWithoutQualityVFT, c_void_p)
        self.type = lib60870.TypeID.M_ME_ND_1.c_enum

    def get_value(self):
        lib.MeasuredValueNormalizedWithoutQuality_getValue.restype = c_float
        return lib.MeasuredValueNormalizedWithoutQuality_getValue(pMeasuredValueNormalizedWithoutQuality(self))

    def set_value(self, value):
        lib.MeasuredValueNormalizedWithoutQuality_setValue(
            pMeasuredValueNormalizedWithoutQuality(self),
            c_float(value))

pMeasuredValueNormalizedWithoutQuality = ctypes.POINTER(MeasuredValueNormalizedWithoutQuality)


class SinglePointWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', c_bool),
        ('quality', QualityDescriptor),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.singlePointWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_SP_TB_1.c_enum

    def get_timestamp(self):
        lib.SinglePointWithCP56Time2a_getTimestamp.restype = pCP56Time2a
        return lib.SinglePointWithCP56Time2a_getTimestamp(pSinglePointWithCP56Time2a(self))

pSinglePointWithCP56Time2a = ctypes.POINTER(SinglePointWithCP56Time2a)


class DoublePointWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', DoublePointValue),
        ('quality', QualityDescriptor),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.doublePointWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_DP_TB_1.c_enum

    def get_timestamp(self):
        lib.DoublePointWithCP56Time2a_getTimestamp.restype = pCP56Time2a
        return lib.DoublePointWithCP56Time2a_getTimestamp(pDoublePointWithCP56Time2a(self))

pDoublePointWithCP56Time2a = ctypes.POINTER(DoublePointWithCP56Time2a)


class StepPositionWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('vti', c_uint8),
        ('quality', QualityDescriptor),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.stepPositionWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_ST_TB_1.c_enum

    def get_timestamp(self):
        lib.StepPositionWithCP56Time2a_getTimestamp.restype = pCP56Time2a
        return lib.StepPositionWithCP56Time2a_getTimestamp(pStepPositionWithCP56Time2a(self))

pStepPositionWithCP56Time2a = ctypes.POINTER(StepPositionWithCP56Time2a)


class Bitstring32WithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', c_uint32),
        ('quality', QualityDescriptor),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.bitstring32WithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_BO_TB_1.c_enum

    def get_timestamp(self):
        lib.Bitstring32WithCP56Time2a_getTimestamp.restype = pCP56Time2a
        return lib.Bitstring32WithCP56Time2a_getTimestamp(pBitstring32WithCP56Time2a(self))

pBitstring32WithCP56Time2a = ctypes.POINTER(Bitstring32WithCP56Time2a)


class MeasuredValueNormalizedWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('encodedValue', ctypes.c_uint8 * 2),
        ('quality', QualityDescriptor),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.measuredValueNormalizedWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_ME_TD_1.c_enum

    def get_timestamp(self):
        lib.MeasuredValueNormalizedWithCP56Time2a_getTimestamp.restype = pCP56Time2a
        return lib.MeasuredValueNormalizedWithCP56Time2a_getTimestamp(pMeasuredValueNormalizedWithCP56Time2a(self))

    def set_timestamp(self, value):
        lib.MeasuredValueNormalizedWithCP56Time2a_setTimestamp(
            pMeasuredValueNormalizedWithCP56Time2a(self),
            pCP56Time2a(value))

pMeasuredValueNormalizedWithCP56Time2a = ctypes.POINTER(MeasuredValueNormalizedWithCP56Time2a)


class MeasuredValueScaledWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('encodedValue', ctypes.c_uint8 * 2),
        ('quality', QualityDescriptor),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.measuredValueScaledWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_ME_TE_1.c_enum

    def get_timestamp(self):
        lib.MeasuredValueScaledWithCP56Time2a_getTimestamp.restype = pCP56Time2a
        return lib.MeasuredValueScaledWithCP56Time2a_getTimestamp(pMeasuredValueScaledWithCP56Time2a(self))

    def set_timestamp(self, value):
        lib.MeasuredValueScaledWithCP56Time2a_setTimestamp(
            pMeasuredValueScaledWithCP56Time2a(self),
            pCP56Time2a(value))

pMeasuredValueScaledWithCP56Time2a = ctypes.POINTER(MeasuredValueScaledWithCP56Time2a)


class MeasuredValueShortWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', c_float),
        ('quality', QualityDescriptor),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.measuredValueShortWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_ME_TF_1.c_enum

    def get_timestamp(self):
        lib.MeasuredValueShortWithCP56Time2a_getTimestamp.restype = pCP56Time2a
        return lib.MeasuredValueShortWithCP56Time2a_getTimestamp(pMeasuredValueShortWithCP56Time2a(self))

    def set_timestamp(self, value):
        lib.MeasuredValueShortWithCP56Time2a_setTimestamp(
            pMeasuredValueShortWithCP56Time2a(self),
            pCP56Time2a(value))

pMeasuredValueShortWithCP56Time2a = ctypes.POINTER(MeasuredValueShortWithCP56Time2a)


class IntegratedTotalsWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('totals', BinaryCounterReading),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.integratedTotalsWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_IT_TB_1.c_enum

    def get_timestamp(self):
        lib.IntegratedTotalsWithCP56Time2a_getTimestamp.restype = pCP56Time2a
        return lib.IntegratedTotalsWithCP56Time2a_getTimestamp(pIntegratedTotalsWithCP56Time2a(self))

    def set_timestamp(self, value):
        lib.IntegratedTotalsWithCP56Time2a_setTimestamp(
            pIntegratedTotalsWithCP56Time2a(self),
            pCP56Time2a(value))

pIntegratedTotalsWithCP56Time2a = ctypes.POINTER(IntegratedTotalsWithCP56Time2a)


class EventOfProtectionEquipmentWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('event', SingleEvent),
        ('elapsedTime', CP16Time2a),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.eventOfProtectionEquipmentWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_EP_TD_1.c_enum

    def get_event(self):
        lib.EventOfProtectionEquipmentWithCP56Time2a_getEvent.restype = pSingleEvent
        return lib.EventOfProtectionEquipmentWithCP56Time2a_getEvent(pEventOfProtectionEquipmentWithCP56Time2a(self))

    def get_elapsed_time(self):
        lib.EventOfProtectionEquipmentWithCP56Time2a_getElapsedTime.restype = pCP16Time2a
        return lib.EventOfProtectionEquipmentWithCP56Time2a_getElapsedTime(pEventOfProtectionEquipmentWithCP56Time2a(self))

    def get_timestamp(self):
        lib.EventOfProtectionEquipmentWithCP56Time2a_getTimestamp.restype = pCP56Time2a
        return lib.EventOfProtectionEquipmentWithCP56Time2a_getTimestamp(pEventOfProtectionEquipmentWithCP56Time2a(self))

pEventOfProtectionEquipmentWithCP56Time2a = ctypes.POINTER(EventOfProtectionEquipmentWithCP56Time2a)


class PackedStartEventsOfProtectionEquipmentWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('event', StartEvent),
        ('qdp', QualityDescriptorP),
        ('elapsedTime', CP16Time2a),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.packedStartEventsOfProtectionEquipmentWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_EP_TE_1.c_enum

    def get_event(self):
        lib.PackedStartEventsOfProtectionEquipmentWithCP56Time2a_getEvent.restype = StartEvent
        return lib.PackedStartEventsOfProtectionEquipmentWithCP56Time2a_getEvent(pPackedStartEventsOfProtectionEquipmentWithCP56Time2a(self))

    def get_quality(self):
        lib.PackedStartEventsOfProtectionEquipmentWithCP56Time2a_getQuality.restype = QualityDescriptorP
        return lib.PackedStartEventsOfProtectionEquipmentWithCP56Time2a_getQuality(pPackedStartEventsOfProtectionEquipmentWithCP56Time2a(self))

    def get_elapsed_time(self):
        lib.PackedStartEventsOfProtectionEquipmentWithCP56Time2a_getElapsedTime.restype = pCP16Time2a
        return lib.PackedStartEventsOfProtectionEquipmentWithCP56Time2a_getElapsedTime(pPackedStartEventsOfProtectionEquipmentWithCP56Time2a(self))

    def get_timestamp(self):
        lib.PackedStartEventsOfProtectionEquipmentWithCP56Time2a_getTimestamp.restype = pCP56Time2a
        return lib.PackedStartEventsOfProtectionEquipmentWithCP56Time2a_getTimestamp(pPackedStartEventsOfProtectionEquipmentWithCP56Time2a(self))

pPackedStartEventsOfProtectionEquipmentWithCP56Time2a = ctypes.POINTER(PackedStartEventsOfProtectionEquipmentWithCP56Time2a)


class PackedOutputCircuitInfoWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('oci', OutputCircuitInfo),
        ('qdp', QualityDescriptorP),
        ('operatingTime', CP16Time2a),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.packedOutputCircuitInfoWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.M_EP_TF_1.c_enum

    def get_oci(self):
        lib.PackedOutputCircuitInfoWithCP56Time2a_getOCI.restype = OutputCircuitInfo
        return lib.PackedOutputCircuitInfoWithCP56Time2a_getOCI(pPackedOutputCircuitInfoWithCP56Time2a(self))

    def get_quality(self):
        lib.PackedOutputCircuitInfoWithCP56Time2a_getQuality.restype = QualityDescriptorP
        return lib.PackedOutputCircuitInfoWithCP56Time2a_getQuality(pPackedOutputCircuitInfoWithCP56Time2a(self))

    def get_operating_time(self):
        lib.PackedOutputCircuitInfoWithCP56Time2a_getOperatingTime.restype = pCP16Time2a
        return lib.PackedOutputCircuitInfoWithCP56Time2a_getOperatingTime(pPackedOutputCircuitInfoWithCP56Time2a(self))

    def get_timestamp(self):
        lib.PackedOutputCircuitInfoWithCP56Time2a_getTimestamp.restype = pCP56Time2a
        return lib.PackedOutputCircuitInfoWithCP56Time2a_getTimestamp(pPackedOutputCircuitInfoWithCP56Time2a(self))

pPackedOutputCircuitInfoWithCP56Time2a = ctypes.POINTER(PackedOutputCircuitInfoWithCP56Time2a)


class SingleCommand(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('sco', c_uint8)
        ]

    def __init__(self, oa, command, select_command, qu):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.singleCommandVFT, c_void_p)
        self.type = lib60870.TypeID.C_SC_NA_1.c_enum
        self.set_sco(command, select_command, qu)

    def get_qu(self):
        lib.SingleCommand_getQU.restype = c_int
        return lib.SingleCommand_getQU(pSingleCommand(self))

    def get_state(self):
        lib.SingleCommand_getState.restype = c_bool
        return lib.SingleCommand_getState(pSingleCommand(self))

    def is_select(self):
        lib.SingleCommand_isSelect.restype = c_bool
        return lib.SingleCommand_isSelect(pSingleCommand(self))

    def set_sco(self, command, select_command, qu):
        self.sco = ((qu & 0x1f) << 2)
        if command:
            self.sco |= 0x01
        if select_command:
            self.sco |= 0x80


pSingleCommand = ctypes.POINTER(SingleCommand)


class DoubleCommand(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('dcq', c_uint8)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.doubleCommandVFT, c_void_p)
        self.type = lib60870.TypeID.C_DC_NA_1.c_enum

    def get_qu(self):
        lib.DoubleCommand_getQU.restype = c_int
        return lib.DoubleCommand_getQU(pDoubleCommand(self))

    def get_state(self):
        lib.DoubleCommand_getState.restype = c_int
        return lib.DoubleCommand_getState(pDoubleCommand(self))

    def is_select(self):
        lib.DoubleCommand_isSelect.restype = c_bool
        return lib.DoubleCommand_isSelect(pDoubleCommand(self))

pDoubleCommand = ctypes.POINTER(DoubleCommand)


class StepCommand(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('dcq', c_uint8)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.stepCommandVFT, c_void_p)
        self.type = lib60870.TypeID.C_RC_NA_1.c_enum

    def get_qu(self):
        lib.StepCommand_getQU.restype = c_int
        return lib.StepCommand_getQU(pStepCommand(self))

    def get_state(self):
        lib.StepCommand_getState.restype = pStepCommandValue
        return lib.StepCommand_getState(pStepCommand(self))

    def is_select(self):
        lib.StepCommand_isSelect.restype = c_bool
        return lib.StepCommand_isSelect(pStepCommand(self))

pStepCommand = ctypes.POINTER(StepCommand)


class SetpointCommandNormalized(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('encodedValue', ctypes.c_uint8 * 2),
        ('qos', c_uint8)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.setpointCommandNormalizedVFT, c_void_p)
        self.type = lib60870.TypeID.C_SE_NA_1.c_enum

    def get_value(self):
        lib.SetpointCommandNormalized_getValue.restype = c_float
        return lib.SetpointCommandNormalized_getValue(pSetpointCommandNormalized(self))

    def get_ql(self):
        lib.SetpointCommandNormalized_getQL.restype = c_int
        return lib.SetpointCommandNormalized_getQL(pSetpointCommandNormalized(self))

    def is_select(self):
        lib.SetpointCommandNormalized_isSelect.restype = c_bool
        return lib.SetpointCommandNormalized_isSelect(pSetpointCommandNormalized(self))

pSetpointCommandNormalized = ctypes.POINTER(SetpointCommandNormalized)


class SetpointCommandScaled(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('encodedValue', ctypes.c_uint8 * 2),
        ('qos', c_uint8)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.setpointCommandScaledVFT, c_void_p)
        self.type = lib60870.TypeID.C_SE_NB_1.c_enum

    def get_value(self):
        lib.SetpointCommandScaled_getValue.restype = c_int
        return lib.SetpointCommandScaled_getValue(pSetpointCommandScaled(self))

    def get_ql(self):
        lib.SetpointCommandScaled_getQL.restype = c_int
        return lib.SetpointCommandScaled_getQL(pSetpointCommandScaled(self))

    def is_select(self):
        lib.SetpointCommandScaled_isSelect.restype = c_bool
        return lib.SetpointCommandScaled_isSelect(pSetpointCommandScaled(self))

pSetpointCommandScaled = ctypes.POINTER(SetpointCommandScaled)


class SetpointCommandShort(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', c_float),
        ('qos', c_uint8)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.setpointCommandShortVFT, c_void_p)
        self.type = lib60870.TypeID.C_SE_NC_1.c_enum

    def get_value(self):
        lib.SetpointCommandShort_getValue.restype = c_float
        return lib.SetpointCommandShort_getValue(pSetpointCommandShort(self))

    def get_ql(self):
        lib.SetpointCommandShort_getQL.restype = c_int
        return lib.SetpointCommandShort_getQL(pSetpointCommandShort(self))

    def is_select(self):
        lib.SetpointCommandShort_isSelect.restype = c_bool
        return lib.SetpointCommandShort_isSelect(pSetpointCommandShort(self))

pSetpointCommandShort = ctypes.POINTER(SetpointCommandShort)


class Bitstring32Command(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', c_uint32)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.bitstring32CommandVFT, c_void_p)
        self.type = lib60870.TypeID.C_BO_NA_1.c_enum

    def get_value(self):
        lib.Bitstring32Command_getValue.restype = c_uint32
        return lib.Bitstring32Command_getValue(pBitstring32Command(self))

pBitstring32Command = ctypes.POINTER(Bitstring32Command)


class SingleCommandWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('sco', c_uint8),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.singleCommandWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.C_SC_TA_1.c_enum

    def get_timestamp(self):
        lib.SingleCommandWithCP56Time2a_getTimestamp.restype = pCP56Time2a
        return lib.SingleCommandWithCP56Time2a_getTimestamp(pSingleCommandWithCP56Time2a(self))

pSingleCommandWithCP56Time2a = ctypes.POINTER(SingleCommandWithCP56Time2a)


class DoubleCommandWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('dcq', c_uint8),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.doubleCommandWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.C_DC_TA_1.c_enum

    def get_qu(self):
        lib.DoubleCommandWithCP56Time2a_getQU.restype = c_int
        return lib.DoubleCommandWithCP56Time2a_getQU(pDoubleCommandWithCP56Time2a(self))

    def get_state(self):
        lib.DoubleCommandWithCP56Time2a_getState.restype = c_int
        return lib.DoubleCommandWithCP56Time2a_getState(pDoubleCommandWithCP56Time2a(self))

    def is_select(self):
        lib.DoubleCommandWithCP56Time2a_isSelect.restype = c_bool
        return lib.DoubleCommandWithCP56Time2a_isSelect(pDoubleCommandWithCP56Time2a(self))

pDoubleCommandWithCP56Time2a = ctypes.POINTER(DoubleCommandWithCP56Time2a)


class StepCommandWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('dcq', c_uint8),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.stepCommandWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.C_RC_TA_1.c_enum

    def get_qu(self):
        lib.StepCommandWithCP56Time2a_getQU.restype = c_int
        return lib.StepCommandWithCP56Time2a_getQU(pStepCommandWithCP56Time2a(self))

    def get_state(self):
        lib.StepCommandWithCP56Time2a_getState.restype = pStepCommandValue
        return lib.StepCommandWithCP56Time2a_getState(pStepCommandWithCP56Time2a(self))

    def is_select(self):
        lib.StepCommandWithCP56Time2a_isSelect.restype = c_bool
        return lib.StepCommandWithCP56Time2a_isSelect(pStepCommandWithCP56Time2a(self))

pStepCommandWithCP56Time2a = ctypes.POINTER(StepCommandWithCP56Time2a)


class SetpointCommandNormalizedWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('encodedValue', ctypes.c_uint8 * 2),
        ('qos', c_uint8),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.setpointCommandNormalizedWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.C_SE_TA_1.c_enum

    def get_value(self):
        lib.SetpointCommandNormalizedWithCP56Time2a_getValue.restype = c_float
        return lib.SetpointCommandNormalizedWithCP56Time2a_getValue(pSetpointCommandNormalizedWithCP56Time2a(self))

    def get_ql(self):
        lib.SetpointCommandNormalizedWithCP56Time2a_getQL.restype = c_int
        return lib.SetpointCommandNormalizedWithCP56Time2a_getQL(pSetpointCommandNormalizedWithCP56Time2a(self))

    def is_select(self):
        lib.SetpointCommandNormalizedWithCP56Time2a_isSelect.restype = c_bool
        return lib.SetpointCommandNormalizedWithCP56Time2a_isSelect(pSetpointCommandNormalizedWithCP56Time2a(self))

pSetpointCommandNormalizedWithCP56Time2a = ctypes.POINTER(SetpointCommandNormalizedWithCP56Time2a)


class SetpointCommandScaledWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('encodedValue', ctypes.c_uint8 * 2),
        ('qos', c_uint8),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.setpointCommandScaledWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.C_SE_TB_1.c_enum

    def get_value(self):
        lib.SetpointCommandScaledWithCP56Time2a_getValue.restype = c_int
        return lib.SetpointCommandScaledWithCP56Time2a_getValue(pSetpointCommandScaledWithCP56Time2a(self))

    def get_ql(self):
        lib.SetpointCommandScaledWithCP56Time2a_getQL.restype = c_int
        return lib.SetpointCommandScaledWithCP56Time2a_getQL(pSetpointCommandScaledWithCP56Time2a(self))

    def is_select(self):
        lib.SetpointCommandScaledWithCP56Time2a_isSelect.restype = c_bool
        return lib.SetpointCommandScaledWithCP56Time2a_isSelect(pSetpointCommandScaledWithCP56Time2a(self))

pSetpointCommandScaledWithCP56Time2a = ctypes.POINTER(SetpointCommandScaledWithCP56Time2a)


class SetpointCommandShortWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', c_float),
        ('qos', c_uint8),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.setpointCommandShortWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.C_SE_TC_1.c_enum

    def get_value(self):
        lib.SetpointCommandShortWithCP56Time2a_getValue.restype = c_float
        return lib.SetpointCommandShortWithCP56Time2a_getValue(pSetpointCommandShortWithCP56Time2a(self))

    def get_ql(self):
        lib.SetpointCommandShortWithCP56Time2a_getQL.restype = c_int
        return lib.SetpointCommandShortWithCP56Time2a_getQL(pSetpointCommandShortWithCP56Time2a(self))

    def is_select(self):
        lib.SetpointCommandShortWithCP56Time2a_isSelect.restype = c_bool
        return lib.SetpointCommandShortWithCP56Time2a_isSelect(pSetpointCommandShortWithCP56Time2a(self))

pSetpointCommandShortWithCP56Time2a = ctypes.POINTER(SetpointCommandShortWithCP56Time2a)


class Bitstring32CommandWithCP56Time2a(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('value', c_uint32),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.bitstring32CommandWithCP56Time2aVFT, c_void_p)
        self.type = lib60870.TypeID.C_BO_TA_1.c_enum

    def get_value(self):
        lib.Bitstring32CommandWithCP56Time2a_getValue.restype = c_uint32
        return lib.Bitstring32CommandWithCP56Time2a_getValue(pBitstring32CommandWithCP56Time2a(self))

    def get_timestamp(self):
        lib.Bitstring32CommandWithCP56Time2a_getTimestamp.restype = pCP56Time2a
        return lib.Bitstring32CommandWithCP56Time2a_getTimestamp(pBitstring32CommandWithCP56Time2a(self))

pBitstring32CommandWithCP56Time2a = ctypes.POINTER(Bitstring32CommandWithCP56Time2a)


class EndOfInitialization(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('coi', c_uint8)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.endOfInitializationVFT, c_void_p)
        self.type = lib60870.TypeID.M_EI_NA_1.c_enum

    def get_coi(self):
        lib.EndOfInitialization_getCOI.restype = c_uint8
        return lib.EndOfInitialization_getCOI(pEndOfInitialization(self))

pEndOfInitialization = ctypes.POINTER(EndOfInitialization)


class InterrogationCommand(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('qoi', c_uint8)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.interrogationCommandVFT, c_void_p)
        self.type = lib60870.TypeID.C_IC_NA_1.c_enum

    def get_qoi(self):
        lib.InterrogationCommand_getQOI.restype = c_uint8
        return lib.InterrogationCommand_getQOI(pInterrogationCommand(self))

pInterrogationCommand = ctypes.POINTER(InterrogationCommand)


class CounterInterrogationCommand(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('qcc', c_uint8)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.counterInterrogationCommandVFT, c_void_p)
        self.type = lib60870.TypeID.C_CI_NA_1.c_enum

    def get_qcc(self):
        lib.CounterInterrogationCommand_getQCC.restype = pQualifierOfCIC
        return lib.CounterInterrogationCommand_getQCC(pCounterInterrogationCommand(self))

pCounterInterrogationCommand = ctypes.POINTER(CounterInterrogationCommand)


class ReadCommand(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.readCommandVFT, c_void_p)
        self.type = lib60870.TypeID.C_RD_NA_1.c_enum

pReadCommand = ctypes.POINTER(ReadCommand)


class ClockSynchronizationCommand(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('timestamp', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.clockSynchronizationCommandVFT, c_void_p)
        self.type = lib60870.TypeID.C_CS_NA_1.c_enum

    def get_time(self):
        lib.ClockSynchronizationCommand_getTime.restype = pCP56Time2a
        return lib.ClockSynchronizationCommand_getTime(pClockSynchronizationCommand(self)).contents

pClockSynchronizationCommand = ctypes.POINTER(ClockSynchronizationCommand)


class ResetProcessCommand(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('qrp', QualifierOfRPC)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.resetProcessCommandVFT, c_void_p)
        self.type = lib60870.TypeID.C_RP_NA_1.c_enum

    def get_qrp(self):
        lib.ResetProcessCommand_getQRP.restype = QualifierOfRPC
        return lib.ResetProcessCommand_getQRP(pResetProcessCommand(self))

pResetProcessCommand = ctypes.POINTER(ResetProcessCommand)


class DelayAcquisitionCommand(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('delay', CP16Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.delayAcquisitionCommandVFT, c_void_p)
        self.type = lib60870.TypeID.C_CD_NA_1.c_enum

    def get_delay(self):
        lib.DelayAcquisitionCommand_getDelay.restype = pCP16Time2a
        return lib.DelayAcquisitionCommand_getDelay(pDelayAcquisitionCommand(self))

pDelayAcquisitionCommand = ctypes.POINTER(DelayAcquisitionCommand)


class ParameterNormalizedValue(MeasuredValueNormalized):

    def get_value(self):
        lib.ParameterNormalizedValue_getValue.restype = c_float
        return lib.ParameterNormalizedValue_getValue(pParameterNormalizedValue(self))

    def set_value(self, value):
        lib.ParameterNormalizedValue_setValue(
            pParameterNormalizedValue(self),
            c_float(value))

    def get_qpm(self):
        lib.ParameterNormalizedValue_getQPM.restype = pQualifierOfParameterMV
        return lib.ParameterNormalizedValue_getQPM(pParameterNormalizedValue(self))

pParameterNormalizedValue = ctypes.POINTER(ParameterNormalizedValue)


class ParameterScaledValue(MeasuredValueScaled):
    def get_value(self):
        lib.ParameterScaledValue_getValue.restype = c_int
        return lib.ParameterScaledValue_getValue(pParameterScaledValue(self))

    def set_value(self, value):
        lib.ParameterScaledValue_setValue(
            pParameterScaledValue(self),
            c_int(value))

    def get_qpm(self):
        lib.ParameterScaledValue_getQPM.restype = pQualifierOfParameterMV
        return lib.ParameterScaledValue_getQPM(pParameterScaledValue(self))

pParameterScaledValue = ctypes.POINTER(ParameterScaledValue)


class ParameterFloatValue(MeasuredValueShort):
    def get_value(self):
        lib.ParameterFloatValue_getValue.restype = c_float
        return lib.ParameterFloatValue_getValue(pParameterFloatValue(self))

    def set_value(self, value):
        lib.ParameterFloatValue_setValue(
            pParameterFloatValue(self),
            c_float(value))

    def get_qpm(self):
        lib.ParameterFloatValue_getQPM.restype = pQualifierOfParameterMV
        return lib.ParameterFloatValue_getQPM(pParameterFloatValue(self))

pParameterFloatValue = ctypes.POINTER(ParameterFloatValue)


class ParameterActivation(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('qpa', QualifierOfParameterActivation)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.parameterActivationVFT, c_void_p)
        self.type = lib60870.TypeID.P_AC_NA_1.c_enum

    def get_quality(self):
        lib.ParameterActivation_getQuality.restype = QualifierOfParameterActivation
        return lib.ParameterActivation_getQuality(pParameterActivation(self))

pParameterActivation = ctypes.POINTER(ParameterActivation)


class FileReady(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('nof', c_uint16),
        ('lengthOfFile', c_uint32),
        ('frq', c_uint8)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.fileReadyVFT, c_void_p)
        self.type = lib60870.TypeID.F_FR_NA_1.c_enum

    def get_frq(self):
        lib.FileReady_getFRQ.restype = c_uint8
        return lib.FileReady_getFRQ(pFileReady(self))

    def set_frq(self, frq):
        lib.FileReady_setFRQ(
            pFileReady(self),
            c_uint8(frq))

    def is_positive(self):
        lib.FileReady_isPositive.restype = c_bool
        return lib.FileReady_isPositive(pFileReady(self))

    def get_nof(self):
        lib.FileReady_getNOF.restype = c_uint16
        return lib.FileReady_getNOF(pFileReady(self))

    def get_length_of_file(self):
        lib.FileReady_getLengthOfFile.restype = c_uint32
        return lib.FileReady_getLengthOfFile(pFileReady(self))

pFileReady = ctypes.POINTER(FileReady)


class SectionReady(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('nof', c_uint16),
        ('nameOfSection', c_uint8),
        ('lengthOfSection', c_uint32),
        ('srq', c_uint8)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.sectionReadyVFT, c_void_p)
        self.type = lib60870.TypeID.F_SR_NA_1.c_enum

    def is_not_ready(self):
        lib.SectionReady_isNotReady.restype = c_bool
        return lib.SectionReady_isNotReady(pSectionReady(self))

    def get_srq(self):
        lib.SectionReady_getSRQ.restype = c_uint8
        return lib.SectionReady_getSRQ(pSectionReady(self))

    def set_srq(self, srq):
        lib.SectionReady_setSRQ(
            pSectionReady(self),
            c_uint8(srq))

    def get_nof(self):
        lib.SectionReady_getNOF.restype = c_uint16
        return lib.SectionReady_getNOF(pSectionReady(self))

    def get_name_of_section(self):
        lib.SectionReady_getNameOfSection.restype = c_uint8
        return lib.SectionReady_getNameOfSection(pSectionReady(self))

    def get_length_of_section(self):
        lib.SectionReady_getLengthOfSection.restype = c_uint32
        return lib.SectionReady_getLengthOfSection(pSectionReady(self))

pSectionReady = ctypes.POINTER(SectionReady)


class FileCallOrSelect(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('nof', c_uint16),
        ('nameOfSection', c_uint8),
        ('scq', c_uint8)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.fileCallOrSelectVFT, c_void_p)
        self.type = lib60870.TypeID.F_SC_NA_1.c_enum

    def get_nof(self):
        lib.FileCallOrSelect_getNOF.restype = c_uint16
        return lib.FileCallOrSelect_getNOF(pFileCallOrSelect(self))

    def get_name_of_section(self):
        lib.FileCallOrSelect_getNameOfSection.restype = c_uint8
        return lib.FileCallOrSelect_getNameOfSection(pFileCallOrSelect(self))

    def get_scq(self):
        lib.FileCallOrSelect_getSCQ.restype = c_uint8
        return lib.FileCallOrSelect_getSCQ(pFileCallOrSelect(self))

pFileCallOrSelect = ctypes.POINTER(FileCallOrSelect)


class FileLastSegmentOrSection(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('nof', c_uint16),
        ('nameOfSection', c_uint8),
        ('lsq', c_uint8),
        ('chs', c_uint8)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.fileLastSegmentOrSectionVFT, c_void_p)
        self.type = lib60870.TypeID.F_LS_NA_1.c_enum

    def get_nof(self):
        lib.FileLastSegmentOrSection_getNOF.restype = c_uint16
        return lib.FileLastSegmentOrSection_getNOF(pFileLastSegmentOrSection(self))

    def get_name_of_section(self):
        lib.FileLastSegmentOrSection_getNameOfSection.restype = c_uint8
        return lib.FileLastSegmentOrSection_getNameOfSection(pFileLastSegmentOrSection(self))

    def get_lsq(self):
        lib.FileLastSegmentOrSection_getLSQ.restype = c_uint8
        return lib.FileLastSegmentOrSection_getLSQ(pFileLastSegmentOrSection(self))

    def get_chs(self):
        lib.FileLastSegmentOrSection_getCHS.restype = c_uint8
        return lib.FileLastSegmentOrSection_getCHS(pFileLastSegmentOrSection(self))

pFileLastSegmentOrSection = ctypes.POINTER(FileLastSegmentOrSection)


class FileACK(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('nof', c_uint16),
        ('nameOfSection', c_uint8),
        ('afq', c_uint8)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.fileACKVFT, c_void_p)
        self.type = lib60870.TypeID.F_AF_NA_1.c_enum

    def get_nof(self):
        lib.FileACK_getNOF.restype = c_uint16
        return lib.FileACK_getNOF(pFileACK(self))

    def get_name_of_section(self):
        lib.FileACK_getNameOfSection.restype = c_uint8
        return lib.FileACK_getNameOfSection(pFileACK(self))

    def get_afq(self):
        lib.FileACK_getAFQ.restype = c_uint8
        return lib.FileACK_getAFQ(pFileACK(self))

pFileACK = ctypes.POINTER(FileACK)


class FileSegment(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('nof', c_uint16),
        ('nameOfSection', c_uint8),
        ('los', c_uint8),
        ('data', ctypes.POINTER(c_uint8))
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.fileSegmentVFT, c_void_p)
        self.type = lib60870.TypeID.F_SG_NA_1.c_enum

    def get_nof(self):
        lib.FileSegment_getNOF.restype = c_uint16
        return lib.FileSegment_getNOF(pFileSegment(self))

    def get_name_of_section(self):
        lib.FileSegment_getNameOfSection.restype = c_uint8
        return lib.FileSegment_getNameOfSection(pFileSegment(self))

    def get_length_of_segment(self):
        lib.FileSegment_getLengthOfSegment.restype = c_uint8
        return lib.FileSegment_getLengthOfSegment(pFileSegment(self))

    def get_segment_data(self):
        lib.FileSegment_getSegmentData.restype = ctypes.POINTER(c_uint8)
        return lib.FileSegment_getSegmentData(pFileSegment(self))

    def get_max_data_size(parameters):
        lib.FileSegment_GetMaxDataSize.restype = c_int
        return lib.FileSegment_GetMaxDataSize(pConnectionParameters(parameters))

pFileSegment = ctypes.POINTER(FileSegment)


class FileDirectory(ctypes.Structure, IOBase):
    _fields_ = [
        ('objectAddress', c_int),
        ('type', TypeID),
        ('virtualFunctionTable', pInformationObjectVFT),
        ('nof', c_uint16),
        ('lengthOfFile', c_int),
        ('sof', c_uint8),
        ('creationTime', CP56Time2a)
        ]

    def __init__(self, oa):
        self.objectAddress = oa
        self.virtualFunctionTable = ctypes.cast(lib.fileDirectoryVFT, c_void_p)
        self.type = lib60870.TypeID.F_DR_TA_1.c_enum

    def get_nof(self):
        lib.FileDirectory_getNOF.restype = c_uint16
        return lib.FileDirectory_getNOF(pFileDirectory(self))

    def get_sof(self):
        lib.FileDirectory_getSOF.restype = c_uint8
        return lib.FileDirectory_getSOF(pFileDirectory(self))

    def get_status(self):
        lib.FileDirectory_getSTATUS.restype = c_int
        return lib.FileDirectory_getSTATUS(pFileDirectory(self))

    def get_lfd(self):
        lib.FileDirectory_getLFD.restype = c_bool
        return lib.FileDirectory_getLFD(pFileDirectory(self))

    def get_for(self):
        lib.FileDirectory_getFOR.restype = c_bool
        return lib.FileDirectory_getFOR(pFileDirectory(self))

    def get_fa(self):
        lib.FileDirectory_getFA.restype = c_bool
        return lib.FileDirectory_getFA(pFileDirectory(self))

    def get_length_of_file(self):
        lib.FileDirectory_getLengthOfFile.restype = c_uint8
        return lib.FileDirectory_getLengthOfFile(pFileDirectory(self))

    def get_creation_time(self):
        lib.FileDirectory_getCreationTime.restype = pCP56Time2a
        return lib.FileDirectory_getCreationTime(pFileDirectory(self))

pFileDirectory = ctypes.POINTER(FileDirectory)


def GetIoTypeFromTypeId(type_id):
    """
    Look-up function used for setting the return type of ASDU.get_upcasted_element(i)
    """
    type_id_to_struct = {
        lib60870.TypeID.INVALID: None,
        lib60870.TypeID.M_SP_NA_1: SinglePointInformation,  # 1
        lib60870.TypeID.M_SP_TA_1: SinglePointWithCP24Time2a,  # 2
        lib60870.TypeID.M_DP_NA_1: DoublePointInformation,  # 3
        lib60870.TypeID.M_DP_TA_1: DoublePointWithCP24Time2a,  # 4
        lib60870.TypeID.M_ST_NA_1: StepPositionInformation,  # 5
        lib60870.TypeID.M_ST_TA_1: StepPositionWithCP24Time2a,  # 6
        lib60870.TypeID.M_BO_NA_1: BitString32,  # 7
        lib60870.TypeID.M_BO_TA_1: Bitstring32WithCP24Time2a,  # 8
        lib60870.TypeID.M_ME_NA_1: MeasuredValueNormalized,  # 9
        lib60870.TypeID.M_ME_TA_1: MeasuredValueNormalizedWithCP24Time2a,  # 10
        lib60870.TypeID.M_ME_NB_1: MeasuredValueScaled,  # 11
        lib60870.TypeID.M_ME_TB_1: MeasuredValueScaledWithCP24Time2a,  # 12
        lib60870.TypeID.M_ME_NC_1: MeasuredValueShort,  # 13
        lib60870.TypeID.M_ME_TC_1: MeasuredValueShortWithCP24Time2a,  # 14
        lib60870.TypeID.M_IT_NA_1: IntegratedTotals,  # 15
        lib60870.TypeID.M_IT_TA_1: IntegratedTotalsWithCP24Time2a,  # 16
        lib60870.TypeID.M_EP_TA_1: EventOfProtectionEquipment,  # 17
        lib60870.TypeID.M_EP_TB_1: PackedStartEventsOfProtectionEquipment,  # 18
        lib60870.TypeID.M_EP_TC_1: PackedOutputCircuitInfo,  # 19
        lib60870.TypeID.M_PS_NA_1: PackedSinglePointWithSCD,  # 20
        lib60870.TypeID.M_ME_ND_1: MeasuredValueNormalizedWithoutQuality,  # 21
        lib60870.TypeID.M_SP_TB_1: SinglePointWithCP56Time2a,  # 30
        lib60870.TypeID.M_DP_TB_1: DoublePointWithCP56Time2a,  # 31
        lib60870.TypeID.M_ST_TB_1: StepPositionWithCP56Time2a,  # 32
        lib60870.TypeID.M_BO_TB_1: Bitstring32WithCP56Time2a,  # 33
        lib60870.TypeID.M_ME_TD_1: MeasuredValueNormalizedWithCP56Time2a,  # 34
        lib60870.TypeID.M_ME_TE_1: MeasuredValueScaledWithCP56Time2a,  # 35
        lib60870.TypeID.M_ME_TF_1: MeasuredValueShortWithCP56Time2a,  # 36
        lib60870.TypeID.M_IT_TB_1: IntegratedTotalsWithCP56Time2a,  # 37
        lib60870.TypeID.M_EP_TD_1: EventOfProtectionEquipmentWithCP56Time2a,  # 38
        lib60870.TypeID.M_EP_TE_1: PackedStartEventsOfProtectionEquipmentWithCP56Time2a,  # 39
        lib60870.TypeID.M_EP_TF_1: PackedOutputCircuitInfoWithCP56Time2a,  # 40
        # 41 - 44 reserved
        lib60870.TypeID.C_SC_NA_1: SingleCommand,  # 45
        lib60870.TypeID.C_DC_NA_1: DoubleCommand,  # 46
        lib60870.TypeID.C_RC_NA_1: StepCommand,  # 47
        lib60870.TypeID.C_SE_NA_1: SetpointCommandNormalized,  # 48 - Set-point command, normalized value
        lib60870.TypeID.C_SE_NB_1: SetpointCommandScaled,  # 49 - Set-point command, scaled value
        lib60870.TypeID.C_SE_NC_1: SetpointCommandShort,  # 50 - Set-point command, short floating point number
        lib60870.TypeID.C_BO_NA_1: Bitstring32Command,  # 51 - Bitstring command
        # 52 - 57 reserved
        lib60870.TypeID.C_SC_TA_1: SingleCommandWithCP56Time2a,  # 58 - Single command with CP56Time2a
        lib60870.TypeID.C_DC_TA_1: DoubleCommandWithCP56Time2a,  # 59 - Double command with CP56Time2a
        lib60870.TypeID.C_RC_TA_1: StepCommandWithCP56Time2a,  # 60 - Step command with CP56Time2a
        lib60870.TypeID.C_SE_TA_1: SetpointCommandNormalizedWithCP56Time2a,
        # 61 - Setpoint command, normalized value with CP56Time2a
        lib60870.TypeID.C_SE_TB_1: SetpointCommandScaledWithCP56Time2a,
        # 62 - Setpoint command, scaled value with CP56Time2a
        lib60870.TypeID.C_SE_TC_1: SetpointCommandShortWithCP56Time2a,
        # 63 - Setpoint command, short value with CP56Time2a
        lib60870.TypeID.C_BO_TA_1: Bitstring32CommandWithCP56Time2a,  # 64 - Bitstring command with CP56Time2a
        lib60870.TypeID.M_EI_NA_1: EndOfInitialization,  # 70 - End of Initialization
        lib60870.TypeID.C_IC_NA_1: InterrogationCommand,  # 100 - Interrogation command
        lib60870.TypeID.C_CI_NA_1: CounterInterrogationCommand,  # 101 - Counter interrogation command
        lib60870.TypeID.C_RD_NA_1: ReadCommand,  # 102 - Read command
        lib60870.TypeID.C_CS_NA_1: ClockSynchronizationCommand,  # 103 - Clock synchronization command
        lib60870.TypeID.C_RP_NA_1: ResetProcessCommand,  # 105 - Reset process command
        lib60870.TypeID.C_CD_NA_1: DelayAcquisitionCommand,  # 106 - Delay acquisition command
        lib60870.TypeID.P_ME_NA_1: ParameterNormalizedValue,  # 110 - Parameter of measured values, normalized value
        lib60870.TypeID.P_ME_NB_1: ParameterScaledValue,  # 111 - Parameter of measured values, scaled value
        lib60870.TypeID.P_ME_NC_1: ParameterFloatValue,
        # 112 - Parameter of measured values, short floating point number
        lib60870.TypeID.P_AC_NA_1: ParameterActivation,  # 113 - Parameter for activation
        lib60870.TypeID.F_FR_NA_1: FileReady,  # 120 - File ready
        lib60870.TypeID.F_SR_NA_1: SectionReady,  # 121 - Section ready
        lib60870.TypeID.F_SC_NA_1: FileCallOrSelect,  # 122 - Call/Select directory/file/section
        lib60870.TypeID.F_LS_NA_1: FileLastSegmentOrSection,  # 123 - Last segment/section
        lib60870.TypeID.F_AF_NA_1: FileACK,  # 124 -  ACK file/section
        lib60870.TypeID.F_SG_NA_1: FileSegment,  # 125 - File segment
        lib60870.TypeID.F_DR_TA_1: FileDirectory,  # 126 - File directory
    }
    return type_id_to_struct[type_id]
