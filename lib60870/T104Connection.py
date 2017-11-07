import logging
import ctypes
import time
from ctypes import *

from lib60870.common import *
from lib60870.CP56Time2a import CP56Time2a, pCP56Time2a
from lib60870.asdu import pConnectionParameters, pASDU
from lib60870.information_object import pInformationObject
from lib60870 import lib60870

logger = logging.getLogger(__name__)
lib = lib60870.get_library()

# type aliases
pT104Connection = ctypes.c_void_p
c_enum = c_int


class T104Connection():
    def __init__(self, ip, port=lib60870.IEC_60870_5_104_DEFAULT_PORT):
        logger.debug("calling T104Connection()")
        lib.T104Connection_create.restype = pT104Connection
        self.con = pT104Connection(lib.T104Connection_create(c_char_p(ip), c_uint16(port)))

    def __del__(self):
        # clear callbacks. If a final callback is required, call disconnect before the connection is deleted
        lib.T104Connection_setConnectionHandler(self.con, None, None)
        lib.T104Connection_setASDUReceivedHandler(self.con, None, None)
        self.destroy()

    def destroy(self):
        logger.debug("calling T104Connection_destroy({})".format(self.con))
        lib.T104Connection_destroy(self.con)

    def connect(self):
        logger.debug("calling T104Connection_connect({})".format(self.con))
        lib.T104Connection_connect.restype = c_bool
        return lib.T104Connection_connect(self.con)

    def disconnect(self):
        self.close()

    def close(self):
        logger.debug("calling T104Connection_close()")
        lib.T104Connection_close(self.con)

    def send_start_dt(self):
        logger.debug("calling T104Connection_sendStartDT()")
        lib.T104Connection_sendStartDT(self.con)

    def send_stop_dt(self):
        logger.debug("calling T104Connection_sendStopDT()")
        lib.T104Connection_sendStopDT(self.con)

    def is_transmit_buffer_full(self):
        logger.debug("calling T104Connection_isTransmitBufferFull()")
        lib.T104Connection_isTransmitBufferFull.restype = c_bool
        return lib.T104Connection_isTransmitBufferFull(self.con)

    def send_interrogation_command(self,
                                   cot=lib60870.CauseOfTransmission.ACTIVATION,
                                   ca=1,
                                   qoi=lib60870.QualifierOfInterrogation.IEC60870_QOI_STATION):
        logger.debug("calling T104Connection_sendInterrogationCommand()")
        lib.T104Connection_sendInterrogationCommand.restype = c_bool
        return lib.T104Connection_sendInterrogationCommand(
            self.con,
            c_int(cot.value),
            c_int(ca),
            c_int(qoi.value))

    def send_counter_interrogation_command(self, cot, ca, qcc):
        logger.debug("calling T104Connection_sendCounterInterrogationCommand()")
        lib.T104Connection_sendCounterInterrogationCommand.restype = c_bool
        return lib.T104Connection_sendCounterInterrogationCommand(
            self.con,
            c_int(cot.value),
            c_int(ca),
            c_int(qcc.value))

    def send_read_command(self, ca, ioa):
        logger.debug("calling T104Connection_sendReadCommand()")
        lib.T104Connection_sendReadCommand.restype = c_bool
        return lib.T104Connection_sendReadCommand(self.con, c_int(ca), c_int(ioa))

    def send_clock_sync_command(self, ca=1, cp56time2a=None):
        if not cp56time2a:
            cp56time2a = CP56Time2a(int(time.time()*1000))
        logger.debug("calling T104Connection_sendClockSyncCommand()")
        lib.T104Connection_sendClockSyncCommand(
            self.con,
            c_int(ca),
            pCP56Time2a(cp56time2a))

    def send_control_command(self, cot, ca, command):
        lib.T104Connection_sendControlCommand.restype = c_bool
        type_id = command.type
        return lib.T104Connection_sendControlCommand(
            self.con,
            type_id,
            c_enum(cot.value),
            c_int(ca),
            pInformationObject(command))

    def send_asdu(self, asdu):
        lib.T104Connection_sendASDU.restype = c_bool
        return lib.T104Connection_sendASDU(self.con, pASDU(asdu))

    def set_connection_handler(self, callback, parameter=None):
        logger.debug("setting connection callback")
        T104Connection_ConnectionHandler = ctypes.CFUNCTYPE(None, c_void_p, c_void_p, c_int)

        def wrapper(parameter, connection, event):
            event = lib60870.IEC60870ConnectionEvent(event)
            """
            Wraps python function into a ctypes function

            :param parameter: pointer to parameter
            :param event: Enum IEC60870ConnectionEvent
            :returns: None
            """
            logger.debug("connection event: {} {} {}".format(event, connection, parameter))
            callback(parameter, event)

        self._connection_handler_callback = T104Connection_ConnectionHandler(wrapper)
        lib.T104Connection_setConnectionHandler(self.con, self._connection_handler_callback, parameter)

    def set_asdu_received_handler(self, callback, parameter=None):
        logger.debug("setting asdu received callback")
        T104Connection_ASDUReceivedHandler = ctypes.CFUNCTYPE(c_bool, pConnectionParameters, pASDU)

        def wrapper(connection, asdu):
            """
            Wraps python function into a ctypes function

            :param asdu: ASDU
            :returns: bool
            """
            logger.debug("asdu received : {}".format(asdu.contents))
            return c_bool(callback(asdu.contents))

        self._asdu_received_callback = T104Connection_ASDUReceivedHandler(wrapper)
        lib.T104Connection_setASDUReceivedHandler(self.con, self._asdu_received_callback, parameter)
