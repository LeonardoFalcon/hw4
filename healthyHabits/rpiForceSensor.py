import serial
import time
import datetime
from time import strftime, sleep

filterReady = False
avg = 0
sum = 0
sampleCount = 0
onBedThreshold = 700
onTheBedFlag = False

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
         filterReady = True
   else:
      avg = sum/windowSize
      sum -= avg
      sum += val

def stopWatch(value):
    '''From seconds to Days;Hours:Minutes;Seconds'''

    valueD = (((value/365)/24)/60)
    Days = int (valueD)

    valueH = (valueD-Days)*365
    Hours = int(valueH)

    valueM = (valueH - Hours)*24
    Minutes = int(valueM)

    valueS = (valueM - Minutes)*60
    Seconds = int(valueS)


    print Days,";",Hours,":",Minutes,";",Seconds

ser=serial.Serial("/dev/ttyACM0",9600)  #change ACM number as found from ls /dev/tty/ACM*
ser.baudrate=9600
force = 0

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
         sleep(1)
         if avg > onBedThreshold:
            if onTheBedFlag == False:
               onTheBedFlag = True
               start = time.time()
               print("on the bed")
         else:
            if onTheBedFlag == True:
               onTheBedFlag = False
               end = time.time()
               stopWatch(end-start)
               print("off the bed")
