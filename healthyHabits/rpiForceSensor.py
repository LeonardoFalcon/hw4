import serial
import time
import os,json
import ibmiotf.application
from datetime import datetime
from time import strftime, sleep
from threading import Timer

filterReady = False
avg = 0
sum = 0
sampleCount = 0
onBedThreshold = 700 //ADC counts higher than this means, there's someone on the bed.
onTheBedFlag = False
maxSleep = 720 #in minutes - 12 hours
minSleep = 240 #in minutes - 4 hours
accumulatedSleep = 0 #in minutes - This is the accumulated time asleep.

def feed(val):
   global filterReady
   global avg
   global sum
   global sampleCount
   windowSize = 10

   if(sampleCount < windowSize):
      sum += val
      sampleCount += 1
      if sampleCount == windowSize:
         avg = sum/windowSize
         filterReady = True
   else:
      avg = sum/windowSize
      sum -= avg
      sum += val

def stopWatch(value):
    global accumulatedSleep
    '''From seconds to Days;Hours:Minutes;Seconds'''
    seconds = int(value)
    accumulatedSleep += int(seconds/60)
    print(accumulatedSleep) //prints accumulated sleep every time you get off the bed

def on_connect(client, userdata, flags, rc):
   print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
   print("msg received")

def getSecondsInADay():
    x=datetime.today()
    y=x.replace(day=x.day+1, hour=8, minute=0, second=0, microsecond=0)
    delta_t=y-x

    return delta_t.seconds+1

def publishSleepInADay():
    global accumulatedSleep

    normalizedSleep = (float(accumulatedSleep - minSleep)) / (maxSleep - minSleep)
    print(normalizedSleep)
    mydata = {'sleepFeature':normalizedSleep}
    client.publishEvent("RaspberryPi","b827eba7caaf","sleepFeature","json",mydata)
    t = Timer(getSecondsInADay(), publishSleepInADay)
    t.start()
    accumulatedSleep = 0 //reset time slept at the end of the day.

ser=serial.Serial("/dev/ttyACM0",9600)  #setup communication to Arduino
ser.baudrate=9600
force = 0

client=None
try:
    options = {"org":"vwcasz",
    "type":"standalone",
    "id":"54321", # this value needs to be changed and has to be unique
    "auth-method":"use-token-auth",
    "auth-token":"f4Q-03@Ti9*gysZdqa",
    "auth-key":"a-vwcasz-7ag752fyzc"}
    client=ibmiotf.application.Client(options)
    client.connect()
except ibmiotf.ConnectionException as e:
    print e

t = Timer(getSecondsInADay(), publishSleepInADay)
t.start()

with open("cpu_temp.csv", "a") as log:
   while True:
      if ser.inWaiting() > 0:
         read_ser=ser.readline().strip('\0')
         try:
            force = int(read_ser)
         except ValueError:
            pass

         if type(force) == int:
            feed(force)

      if filterReady == True:
         log.write("{0},{1}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(avg)))
         sleep(0.5)
         if avg > onBedThreshold:
            if onTheBedFlag == False:
               onTheBedFlag = True
               mydata = {'sleepActive':1}
               client.publishEvent("RaspberryPi","b827eba7caaf","sleepActive","json",mydata)
               start = time.time()
               print("on the bed")
         else:
            if onTheBedFlag == True:
               onTheBedFlag = False
               mydata = {'sleepActive':0}
               client.publishEvent("RaspberryPi","b827eba7caaf","sleepActive","json",mydata)
               end = time.time()
               stopWatch(end-start)
               print("off the bed")
