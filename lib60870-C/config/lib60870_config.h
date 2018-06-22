/*
 * lib60870_config.h
 */

#ifndef CONFIG_LIB60870_CONFIG_H_
#define CONFIG_LIB60870_CONFIG_H_


/* print debugging information with printf if set to 1 */
#define CONFIG_DEBUG_OUTPUT 1



/**
 * Use static memory for the slave (outstation) message queue.
 *
 * Note: Use only when statically linking the library. You can only have
 * a single slave instance!
 * */
#define CONFIG_SLAVE_WITH_STATIC_MESSAGE_QUEUE 0

/**
 * Compile the library to use threads. This will require semaphore support
 *
 * CONFIG_USE_THREADS = 0 not yet supported
 */
#define CONFIG_USE_THREADS 1

/**
 * Use a separate thread to call the callback functions. This allows the user
 * to have a more natural program flow in the callback function. Otherwise callback
 * functions have to return immediately and send functions called from the callback
 * may not work when the send message queue is full.
 */
#define CONFIG_SLAVE_USE_SEPARATE_CALLBACK_THREAD 0

/**
 * Queue to store received ASDUs before passing them to the user provided callback.
 */
#define CONFIG_SLAVE_SEPARATE_CALLBACK_THREAD_QUEUE_SIZE 12

/**
 * Define the default size for the slave (outstation) message queue. This is used also
 * to buffer ASDUs in the case when the connection is lost.
 *
 * For each queued message about 256 bytes of memory are required.
 */
#define CONFIG_SLAVE_ASDU_QUEUE_SIZE 100

/**
 * This is a connection specific ASDU queue for the slave (outstation). It is used for connection
 * specific ASDUs like those that are automatically generated by the stack or created in
 * the slave side callback. The messages in the queue are removed when the connection is lost.
 *
 * For each queued message about 256 bytes of memory are required.
 */
#define CONFIG_SLAVE_CONNECTION_ASDU_QUEUE_SIZE 10

/**
 * Compile library with support for SINGLE_REDUNDANCY_GROUP server mode (only CS104 server)
 */
#define CONFIG_CS104_SUPPORT_SERVER_MODE_SINGLE_REDUNDANCY_GROUP 1

/**
 * Compile library with support for CONNECTION_IS_REDUNDANCY_GROUP server mode (only CS104 server)
 */
#define CONFIG_CS104_SUPPORT_SERVER_MODE_CONNECTION_IS_REDUNDANCY_GROUP 1

/**
 * Set the maximum number of client connections or 0 for no restriction
 */
#define CONFIG_CS104_MAX_CLIENT_CONNECTIONS 0

/* activate TCP keep alive mechanism. 1 -> activate */
#define CONFIG_ACTIVATE_TCP_KEEPALIVE 0

/* time (in s) between last message and first keepalive message */
#define CONFIG_TCP_KEEPALIVE_IDLE 5

/* time between subsequent keepalive messages if no ack received */
#define CONFIG_TCP_KEEPALIVE_INTERVAL 2

/* number of not missing keepalive responses until socket is considered dead */
#define CONFIG_TCP_KEEPALIVE_CNT 2


#endif /* CONFIG_LIB60870_CONFIG_H_ */
