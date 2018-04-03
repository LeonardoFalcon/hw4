from mpu6050 import mpu6050
from time import sleep
import paho.mqtt.client as mqtt

brokerIp = "192.168.86.77" #LAN
accelerometerXTopic = "accelerometerX"
accelerometerYTopic = "accelerometerY"
accelerometerZTopic = "accelerometerZ"
gyroscopeXTopic = "gyroscopeX"
gyroscopeYTopic = "gyroscopeY"
gyroscopeZTopic = "gyroscopeZ"

sensor = mpu6050(0x68)

def on_connect(client, userdata, flags, rc):
   print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
   print("msg received")

client = mqtt.Client(client_id="5", clean_session=False)
client.on_connect = on_connect
client.on_message = on_message

client.connect(brokerIp, 1883, 60)

client.loop_start()

while True:
    accel_data = sensor.get_accel_data()
    gyro_data = sensor.get_gyro_data()

    print("Accelerometer data")
    print("x: " + str(accel_data['x']))
    print("y: " + str(accel_data['y']))
    print("z: " + str(accel_data['z']))

    client.publish(accelerometerXTopic, payload=accel_data['x'], qos=2, retain=False)
    client.publish(accelerometerYTopic, payload=accel_data['y'], qos=2, retain=False)
    client.publish(accelerometerZTopic, payload=accel_data['z'], qos=2, retain=False)

    print("Gyroscope data")
    print("x: " + str(gyro_data['x']))
    print("y: " + str(gyro_data['y']))
    print("z: " + str(gyro_data['z']))

    client.publish(gyroscopeXTopic, payload=gyro_data['x'], qos=2, retain=False)
    client.publish(gyroscopeYTopic, payload=gyro_data['y'], qos=2, retain=False)
    client.publish(gyroscopeZTopic, payload=gyro_data['z'], qos=2, retain=False)

    sleep(0.1)

