from mpu6050 import mpu6050
import time
import paho.mqtt.client as mqtt
import os,json
import ibmiotf.application

brokerIp = "192.168.86.77" #LAN
accelerometerXTopic = "accelerometerX"
accelerometerYTopic = "accelerometerY"
accelerometerZTopic = "accelerometerZ"
gyroscopeXTopic = "gyroscopeX"
gyroscopeYTopic = "gyroscopeY"
gyroscopeZTopic = "gyroscopeZ"

sensor = mpu6050(0x68)

client=None
def myCommandCallback(cmd):
	print cmd.event
	p=json.loads(cmd.payload)
	print p

try:
	options = {"org":"vwcasz",
		   "type":"standalone",
	       "id":"b827eba7caaf",
	       "auth-method":"use-token-auth",
           "auth-token":"f4Q-03@Ti9*gysZdqa",
		   "auth-key":"a-vwcasz-7ag752fyzc"}

	client=ibmiotf.application.Client(options)
	print "bef"
	client.connect()

while True:
    accel_data = sensor.get_accel_data()
    gyro_data = sensor.get_gyro_data()

    mydata = {'xAcc':accel_data['x']}

#    print("Accelerometer data")
#    print("x: " + str(accel_data['x']))
#    print("y: " + str(accel_data['y']))
#    print("z: " + str(accel_data['z']))

    client.publishEvent("RaspberryPi","b827eba7caaf","door","json",mydata)

#   client.publish(accelerometerXTopic, payload=accel_data['x'], qos=0, retain=False)
#   client.publish(accelerometerYTopic, payload=accel_data['y'], qos=0, retain=False)
#   client.publish(accelerometerZTopic, payload=accel_data['z'], qos=0, retain=False)

#   print("Gyroscope data")
#   print("x: " + str(gyro_data['x']))
#   print("y: " + str(gyro_data['y']))
#   print("z: " + str(gyro_data['z']))

#    client.publish(gyroscopeXTopic, payload=gyro_data['x'], qos=0, retain=False)
#    client.publish(gyroscopeYTopic, payload=gyro_data['y'], qos=0, retain=False)
#    client.publish(gyroscopeZTopic, payload=gyro_data['z'], qos=0, retain=False)

    sleep(0.01)
