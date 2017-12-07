#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <signal.h>

#include "iec60870_slave.h"

#include "hal_thread.h"
#include "hal_time.h"

static bool running = true;

static ConnectionParameters connectionParameters;

void
sigint_handler(int signalId)
{
    running = false;
}

void
printCP56Time2a(CP56Time2a time)
{
    printf("%02i:%02i:%02i %02i/%02i/%04i", CP56Time2a_getHour(time),
                             CP56Time2a_getMinute(time),
                             CP56Time2a_getSecond(time),
                             CP56Time2a_getDayOfMonth(time),
                             CP56Time2a_getMonth(time) + 1,
                             CP56Time2a_getYear(time) + 2000);
}

static bool
clockSyncHandler (void* parameter, MasterConnection connection, ASDU asdu, CP56Time2a newTime)
{
    printf("Process time sync command with time "); printCP56Time2a(newTime); printf("\n");

    return true;
}

static bool
interrogationHandler(void* parameter, MasterConnection connection, ASDU asdu, uint8_t qoi)
{
    printf("Received interrogation for group %i\n", qoi);

    if (qoi == 20) { /* only handle station interrogation */

        MasterConnection_sendACT_CON(connection, asdu, false);

        /* The CS101 specification only allows information objects without timestamp in GI responses */

        ASDU newAsdu = ASDU_create(connectionParameters, M_ME_NB_1, false, INTERROGATED_BY_STATION,
                0, 1, false, false);

        InformationObject io = (InformationObject) MeasuredValueScaled_create(NULL, 100, -1, IEC60870_QUALITY_GOOD);

        ASDU_addInformationObject(newAsdu, io);

        ASDU_addInformationObject(newAsdu, (InformationObject)
            MeasuredValueScaled_create((MeasuredValueScaled) io, 101, 23, IEC60870_QUALITY_GOOD));

        ASDU_addInformationObject(newAsdu, (InformationObject)
            MeasuredValueScaled_create((MeasuredValueScaled) io, 102, 2300, IEC60870_QUALITY_GOOD));

        InformationObject_destroy(io);

        MasterConnection_sendASDU(connection, newAsdu);

        newAsdu = ASDU_create(connectionParameters, M_SP_NA_1, false, INTERROGATED_BY_STATION,
                    0, 1, false, false);

        io = (InformationObject) SinglePointInformation_create(NULL, 104, true, IEC60870_QUALITY_GOOD);

        ASDU_addInformationObject(newAsdu, io);

        ASDU_addInformationObject(newAsdu, (InformationObject)
            SinglePointInformation_create((SinglePointInformation) io, 105, false, IEC60870_QUALITY_GOOD));

        InformationObject_destroy(io);

        MasterConnection_sendASDU(connection, newAsdu);

        newAsdu = ASDU_create(connectionParameters, M_SP_NA_1, true, INTERROGATED_BY_STATION,
                0, 1, false, false);

        ASDU_addInformationObject(newAsdu, io = (InformationObject) SinglePointInformation_create(NULL, 300, true, IEC60870_QUALITY_GOOD));
        ASDU_addInformationObject(newAsdu, (InformationObject) SinglePointInformation_create((SinglePointInformation) io, 301, false, IEC60870_QUALITY_GOOD));
        ASDU_addInformationObject(newAsdu, (InformationObject) SinglePointInformation_create((SinglePointInformation) io, 302, true, IEC60870_QUALITY_GOOD));
        ASDU_addInformationObject(newAsdu, (InformationObject) SinglePointInformation_create((SinglePointInformation) io, 303, false, IEC60870_QUALITY_GOOD));
        ASDU_addInformationObject(newAsdu, (InformationObject) SinglePointInformation_create((SinglePointInformation) io, 304, true, IEC60870_QUALITY_GOOD));
        ASDU_addInformationObject(newAsdu, (InformationObject) SinglePointInformation_create((SinglePointInformation) io, 305, false, IEC60870_QUALITY_GOOD));
        ASDU_addInformationObject(newAsdu, (InformationObject) SinglePointInformation_create((SinglePointInformation) io, 306, true, IEC60870_QUALITY_GOOD));
        ASDU_addInformationObject(newAsdu, (InformationObject) SinglePointInformation_create((SinglePointInformation) io, 307, false, IEC60870_QUALITY_GOOD));

        InformationObject_destroy(io);

        MasterConnection_sendASDU(connection, newAsdu);

        MasterConnection_sendACT_TERM(connection, asdu);
    }
    else {
        MasterConnection_sendACT_CON(connection, asdu, true);
    }

    return true;
}

static bool
asduHandler(void* parameter, MasterConnection connection, ASDU asdu)
{
    if (ASDU_getTypeID(asdu) == C_SC_NA_1) {
        printf("received single command\n");

        if  (ASDU_getCOT(asdu) == ACTIVATION) {
            InformationObject io = ASDU_getElement(asdu, 0);

            if (InformationObject_getObjectAddress(io) == 5000) {
                SingleCommand sc = (SingleCommand) io;

                printf("IOA: %i switch to %i\n", InformationObject_getObjectAddress(io),
                        SingleCommand_getState(sc));

                ASDU_setCOT(asdu, ACTIVATION_CON);
            }
            else
                ASDU_setCOT(asdu, UNKNOWN_INFORMATION_OBJECT_ADDRESS);

            InformationObject_destroy(io);
        }
        else
            ASDU_setCOT(asdu, UNKNOWN_CAUSE_OF_TRANSMISSION);

        MasterConnection_sendASDU(connection, asdu);

        return true;
    }

    return false;
}

static bool
connectionRequestHandler(void* parameter, const char* ipAddress)
{
    printf("New connection from %s\n", ipAddress);

#if 0
    if (strcmp(ipAddress, "127.0.0.1") == 0) {
        printf("Accept connection\n");
        return true;
    }
    else {
        printf("Deny connection\n");
        return false;
    }
#else
    return true;
#endif
}

int
main(int argc, char** argv)
{
    /* Add Ctrl-C handler */
    signal(SIGINT, sigint_handler);

    TLSConfiguration tlsConfig = TLSConfiguration_create();

    TLSConfiguration_setChainValidation(tlsConfig, false);
    TLSConfiguration_setAllowOnlyKnownCertificates(tlsConfig, true);

    if (!TLSConfiguration_setOwnKeyFromFile(tlsConfig, "server-key.pem", NULL)) {
        printf("Failed to load private key!\n");
        return 0;
    }

    if (!TLSConfiguration_setOwnCertificateFromFile(tlsConfig, "server.cer")) {
        printf("ERROR: Failed to load own certificate!\n");
        return 0;
    }

    if (!TLSConfiguration_addCACertificateFromFile(tlsConfig, "root.cer")) {
        printf("ERROR: Failed to load root certificate\n");
        return 0;
    }

    if (!TLSConfiguration_addAllowedCertificateFromFile(tlsConfig, "client1.cer")) {
        printf("ERROR: Failed to load allowed client certificate\n");
        return 0;
    }


    /* create a new slave/server instance with default connection parameters and
     * default message queue size */
    Slave slave = T104Slave_createSecure(NULL, 100, 100, tlsConfig);

    T104Slave_setLocalAddress(slave, "0.0.0.0");

    /* get the connection parameters - we need them to create correct ASDUs */
    connectionParameters = Slave_getConnectionParameters(slave);

    /* set the callback handler for the clock synchronization command */
    Slave_setClockSyncHandler(slave, clockSyncHandler, NULL);

    /* set the callback handler for the interrogation command */
    Slave_setInterrogationHandler(slave, interrogationHandler, NULL);

    /* set handler for other message types */
    Slave_setASDUHandler(slave, asduHandler, NULL);

    T104Slave_setConnectionRequestHandler(slave, connectionRequestHandler, NULL);

    Slave_start(slave);

    if (Slave_isRunning(slave) == false) {
        printf("Starting server failed!\n");
        goto exit_program;
    }

    int16_t scaledValue = 0;

    while (running) {

        Thread_sleep(1000);

        ASDU newAsdu = ASDU_create(connectionParameters, M_ME_NB_1, false, PERIODIC, 0, 1, false, false);

        InformationObject io = (InformationObject) MeasuredValueScaled_create(NULL, 110, scaledValue, IEC60870_QUALITY_GOOD);

        scaledValue++;

        ASDU_addInformationObject(newAsdu, io);

        InformationObject_destroy(io);

        /* Add ASDU to slave event queue - don't release the ASDU afterwards!
         * The ASDU will be released by the Slave instance when the ASDU
         * has been sent.
         */
        Slave_enqueueASDU(slave, newAsdu);
    }

    Slave_stop(slave);

exit_program:
    Slave_destroy(slave);

    TLSConfiguration_destroy(tlsConfig);

    Thread_sleep(500);
}
