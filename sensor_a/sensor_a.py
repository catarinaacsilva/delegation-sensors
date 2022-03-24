#!/usr/bin/python3
# encoding=utf-8


import time
import json
import signal
import random
import logging
import paho.mqtt.client as mqtt


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


SERVER = 'mosquitto'
PORT = 1883
BATTERY_LEVEL = 17
BATTERY_CRITICAL_LEVEL = 15
CONNECTED = False
DELEGATED = False
ACTIVE = False
DONE = False


def handle_exit(sig, frame):
    global DONE
    DONE = True


def on_connect(client, userdata, flags, rc):
    global CONNECTED
    global ACTIVE
    global DONE
    #subcribe control topic
    client.subscribe('sensor_a/control')
    # Register the sensor
    payload={'id':'sensor_a',
    'capabilities':['temperature'],
    'control':'sensor_a/control'}
    client.publish('delegator/register', payload=json.dumps(payload))
    CONNECTED = True
    ACTIVE = True
    logger.info(f'Connected with result code {rc} Connected {CONNECTED} Active {ACTIVE} Done {DONE}')


def on_message(client, userdata, msg):
    global ACTIVE
    
    logger.debug(f'{msg.topic} {str(msg.qos)} {str(msg.payload)}')

    payload = json.loads(msg.payload)
    if msg.topic == 'sensor_a/control':
        ACTIVE = False


def on_disconnect(client, userdata, rc=0):
    global CONNECTED
    global ACTIVE
    global DONE
    logging.debug("DisConnected result code "+str(rc))
    CONNECTED = False
    ACTIVE = False
    DONE = True


def main():
    global BATTERY_CRITICAL_LEVEL
    global BATTERY_LEVEL
    global CONNECTED
    global DELEGATED
    global ACTIVE
    global DONE
    signal.signal(signal.SIGTERM, handle_exit)
    
    # wait for delegator to be ready
    time.sleep(3.0)
    
    client = mqtt.Client(client_id='sensor/a')
    
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    client.connect(host=SERVER, port=PORT)

    while not DONE and BATTERY_LEVEL > 0:
        client.loop()
        if CONNECTED and ACTIVE:
            # publish temperature and baterry levels
            payload={'temperature':25}
            client.publish('sensor/temperature', payload=json.dumps(payload))
            payload={'battery':BATTERY_LEVEL}
            client.publish('sensor/battery', payload=json.dumps(payload))
        

            if BATTERY_LEVEL <= BATTERY_CRITICAL_LEVEL and not DELEGATED:
                # start the delegation process
                payload={'id':'sensor_a','role':'sensor', 'topics':['sensor/temperature'], 'capabilities':['temperature']}
                client.publish('delegator/delegate', payload=json.dumps(payload))
                DELEGATED = True
        BATTERY_LEVEL -= 1
        time.sleep(1.0)
    client.disconnect()


if __name__ == '__main__':
    main()
    