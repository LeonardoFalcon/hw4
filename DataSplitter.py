import paho.mqtt.client as mqtt
import time, threading
from collections import deque

brokerIp = "192.168.86.77" #LAN
accelerometerXTopic = "accelerometerX"
bufferSize = 1000

data = deque(maxlen=bufferSize)
counter = 0

def on_connect(client, userdata, flags, rc):
   print("Connected with result code "+str(rc))
   client.subscribe(accelerometerXTopic, 0)

def on_message(client, userdata, msg):
    global counter
    if msg.topic == accelerometerXTopic:
        data.append(float(msg.payload))
        counter = counter + 1

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

client = mqtt.Client(client_id="6", clean_session=True)
client.on_connect = on_connect
client.on_message = on_message

client.connect(brokerIp, 1883, 60)

client.loop_start()

while True:
    if counter >= bufferSize:
       s = sum(data)


#testDataAcceX = [0] * 100 #this will be the testData within the start and end event.

#dataInChunks = list(chunks(testData, 7))) #this will be the data chunks
