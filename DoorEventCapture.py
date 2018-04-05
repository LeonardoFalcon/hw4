import paho.mqtt.client as mqtt
import time, threading
from collections import deque
import csv

brokerIp = "192.168.86.77" #LAN
accelerometerXTopic = "accelerometerX"
csvfile = "/Users/leonardofalcon/Documents/NCSU/ECE792/Homework 4/doorEvent.csv"

#design parameters
bufferSize = 100 #samples taken for the start-up average calculation
standarDeviationsToStart = 3 #number of standard deviations that indicate door event is starting
numberOfChunks = 5 #number of chunks we want data to be broken up into
numberOfSamplesAboveThresholdToStart = 5
numberOfSamplesBelowThresholdToStop = 50
# end of design parameters

meanCapturedFlag = 0
capturingDataFlag = 0
eventActive = 0

data = deque(maxlen=bufferSize) #this buffer is used to mean calculation
doorEventData = deque() #this buffer contains the door event data
counter = 0
startDataCaptureCount = 0
stopDataCaptureCount = 0

def chunks(lst, div):
    lst = [ lst[i:i + len(lst)/div] for i in range(0, len(lst), len(lst)/div) ] #Subdivide list.
    if len(lst) > div: # If it is an uneven list.
        lst[div-1].extend(sum(lst[div:],[])) # Take the last part of the list and append it to the last equal division.
    return lst[:div] #Return the list up to that point.

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
            if(abs(meanOfData - float(msg.payload)) > threshold): #value significantly far from mean
                startDataCaptureCount += 1 #this is to debounce
                doorEventData.append(float(msg.payload)) #data from door event is here
        if startDataCaptureCount >= numberOfSamplesAboveThresholdToStart: #door opening/closing | this number can be adjusted for sensitivity
            if startDataCaptureCount == numberOfSamplesAboveThresholdToStart:
                print("start")
                eventActive = 1
                stopDataCaptureCount = 0 #reset stop data counter
        if meanCapturedFlag == 1:
            if(abs(meanOfData - float(msg.payload)) < threshold): #data close to mean
                stopDataCaptureCount += 1
                if(stopDataCaptureCount >= numberOfSamplesBelowThresholdToStop): #door has stopped moving
                   if eventActive == 1:
                       print("stop")
                       dataInChunks = list(chunks(list(doorEventData), numberOfChunks)) #this will be the data chunks
                       #Assuming res is a flat list
                       with open(csvfile, "w") as output:
                           print("writing to file")
                           writer = csv.writer(output, lineterminator='\n')
                           for val in list(doorEventData):
                               writer.writerow([val])
                       print(dataInChunks)
                   doorEventData.clear()
                   startDataCaptureCount = 0
                   stopDataCaptureCount = 0
                   eventActive = 0

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
            threshold = stddevOfData * standarDeviationsToStart
            meanCapturedFlag = 1
            print("mean captured")
            print(meanOfData)
            print("threshold")
            print(threshold)
