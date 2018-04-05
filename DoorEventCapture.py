import paho.mqtt.client as mqtt
import time, threading
from collections import deque

brokerIp = "192.168.86.77" #LAN
accelerometerXTopic = "accelerometerX"
bufferSize = 100
meanCapturedFlag = 0
capturingDataFlag = 0
eventActive = 0

data = deque(maxlen=bufferSize)
doorEventData = deque()
counter = 0
startDataCaptureCount = 0
stopDataCaptureCount = 0

def on_connect(client, userdata, flags, rc):
   print("Connected with result code "+str(rc))
   client.subscribe(accelerometerXTopic, 0)

def on_message(client, userdata, msg):
    global counter
    global startDataCaptureCount
    global stopDataCaptureCount
    global eventActive

    if msg.topic == accelerometerXTopic:
        data.append(float(msg.payload)) #used for determining mean
        counter = counter + 1 #used for determining mean
        if meanCapturedFlag == 1:
            if(abs(float(msg.payload)) > threshold): #value significantly far from mean
                startDataCaptureCount += 1 #this is to debounce
        if startDataCaptureCount >= 10: #door opening/closing | this number can be adjusted for sensitivity
            if startDataCaptureCount == 10:
                print("start")
                eventActive = 1
                stopDataCaptureCount = 0 #reset stop data counter
            doorEventData.append(float(msg.payload)) #data from door event is here
        if meanCapturedFlag == 1:
            if(abs(float(msg.payload)) < threshold): #data close to mean
                stopDataCaptureCount += 1
                if(stopDataCaptureCount >= 10): #door has stopped moving
                   if eventActive == 1:
                       print("stop")
                       print(doorEventData)
                       doorEventData.clear()
                   startDataCaptureCount = 0
                   stopDataCaptureCount = 0
                   eventActive = 0

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/float(n) # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def stddev(data, ddof=0):
    """Calculates the population standard deviation
    by default; specify ddof=1 to compute the sample
    standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/(n-ddof)
    return pvar**0.5

client = mqtt.Client(client_id="6", clean_session=True)
client.on_connect = on_connect
client.on_message = on_message

client.connect(brokerIp, 1883, 60)

client.loop_start()

while True:
    # First capture the mean as a baseline
    if counter == bufferSize:
        if meanCapturedFlag == 0:
            meanOfData = mean(data)
            stddevOfData = stddev(data)
            threshold = meanOfData + (stddevOfData * 3)
            meanCapturedFlag = 1
            print("mean captured")
            print(meanOfData)
            print("threshold")
            print(threshold)




#testDataAcceX = [0] * 100 #this will be the testData within the start and end event.

#dataInChunks = list(chunks(testData, 7))) #this will be the data chunks
