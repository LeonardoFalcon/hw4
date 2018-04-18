import serial
import time
import datetime
from time import strftime, sleep
import paho.mqtt.client as mqtt
from threading import Timer

brokerIp = "192.168.86.77" #LAN
sleepTopic = "sleepFeature"
currentlySleepingTopic = "sleepActive"
filterReady = False
avg = 0
sum = 0
sampleCount = 0
onBedThreshold = 700
onTheBedFlag = False
maxSleep = 720 #in minutes - 12 hours
minSleep = 240 #in minutes - 4 hours
accumulatedSleep = 0 #in minutes

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

def on_connect(client, userdata, flags, rc):
   print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
   print("msg received")

def getSecondsInADay():
    x=datetime.today()
    y=x.replace(day=x.day+1, hour=1, minute=0, second=0, microsecond=0)
    delta_t=y-x

    return secs=delta_t.seconds+1

def publishSleepInADay():
    normalizedSleep = (accumulatedSleep - minSleep) / (sleepMax - sleepMin)
    client.publish(currentlySleepingTopic, payload=normalizedSleep, qos=2, retain=False)
    t = Timer(getSecondsInADay(), publishSleepInADay)
    t.start()

ser=serial.Serial("/dev/ttyACM0",9600)  #setup communication to Arduino
ser.baudrate=9600
force = 0

client = mqtt.Client(client_id="5", clean_session=False)
client.on_connect = on_connect
client.on_message = on_message

client.connect(brokerIp, 1883, 60)

client.loop_start()

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
               client.publish(currentlySleepingTopic, payload=1, qos=2, retain=False)
               start = time.time()
               print("on the bed")
         else:
            if onTheBedFlag == True:
               onTheBedFlag = False
               client.publish(currentlySleepingTopic, payload=0, qos=2, retain=False)
               end = time.time()
               stopWatch(end-start)
               print("off the bed")
