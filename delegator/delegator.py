#!/usr/bin/python3
# encoding=utf-8


import time
import json
import uuid
import signal
import random
import logging
import datetime
import paho.mqtt.client as mqtt


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


SERVER = 'mosquitto'
PORT = 1883
CONNECTED = False
DONE = False


DEVICE_DB = {}
RECEIPT_DB = []


def handle_exit(sig, frame):
    global DONE
    DONE = True


def on_connect(client, userdata, flags, rc):
    global CONNECTED
    global DONE
    #subcribe delegator topics
    client.subscribe('delegator/register')
    client.subscribe('delegator/delegate')
    CONNECTED = True
    logger.info(f'Connected with result code {rc} Connected {CONNECTED} Done {DONE}')


def on_message(client, userdata, msg):
    global DEVICE_DB
    global RECEIPT_DB

    #logger.debug(f'{msg.topic} {str(msg.qos)} {str(msg.payload)}')
    payload = json.loads(msg.payload)
    if msg.topic == 'delegator/register':
        # register device
        device_id = payload['id']
        logger.info(f'Register device {device_id}')
        if device_id not in DEVICE_DB:
            DEVICE_DB[device_id] = payload
        #client.publish(payload['control'], payload=json.dumps({'action':'register'}))
    elif msg.topic == 'delegator/delegate':
        device_id = payload['id']
        capabilities = payload['capabilities']
        topics = payload['topics']
        role = payload['role']
        # find sensor with same capabilities
        for key in DEVICE_DB:
            device = DEVICE_DB[key]
            if all(item in device['capabilities'] for  item in capabilities) and device['id'] != device_id:
                # create receipt
                receipt = {'Delegator':device_id,
                'Delegatee': device['id'],
                'Deta Level': 'Public Data',
                'Delegator Consent': True,
                'Delegatee Consent': True,
                'Role': role,
                'Date': datetime.datetime.now(),
                'Token': str(uuid.uuid4())}
                RECEIPT_DB.append(receipt)

                # delegate operation
                client.publish(device['control'], payload=json.dumps({'action':'delegate',
                'capabilities': payload['capabilities'], 'topics': payload['topics']}))

                client.publish(DEVICE_DB[device_id]['control'], payload=json.dumps({'action':'delegate'}))

                logger.info(f'Delegate the {capabilities} to {device["id"]}: {receipt}')

                break

def on_disconnect(client, userdata, rc=0):
    global CONNECTED 
    global DONE
    logging.debug("DisConnected result code "+str(rc))
    CONNECTED = False
    DONE = True


def main():
    global CONNECTED 
    global DONE
    signal.signal(signal.SIGTERM, handle_exit)
    client = mqtt.Client(client_id='delegator')

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    client.connect(host=SERVER, port=PORT)
    
    while not DONE:
        client.loop()
        if CONNECTED:
            pass
        time.sleep(1.0)
    client.disconnect()


if __name__ == '__main__':
    main()