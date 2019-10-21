#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import zmq
import time
import math
import signal
from collections import deque
from threading import Thread
import flatbuffers
#generated by flatc
import topics.nav.imu
import topics.nav.gps
#IMU sensor
from em7180 import EM7180_Master

class Subscriber(Thread):
    def __init__(self, context, id, topics_callbacks):
        super().__init__()
        self.context = context
        self.topics_callbacks = topics_callbacks
        self.loop = False

    def run(self):
        print('starting subscriber, on topic(s) {}'.format(self.topics_callbacks.keys()))
        subscriber = self.context.socket(zmq.SUB)
        subscriber.connect("tcp://127.0.0.1:5555")
        for topic in self.topics_callbacks.keys():
            subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)
        poller = zmq.Poller()
        poller.register(subscriber, zmq.POLLIN)
        self.loop = True
        while self.loop:
            evts = poller.poll(1000)
            if evts:
                message = subscriber.recv()
                for topic in self.topics_callbacks.keys():
                    topic_name_msg = message.split(None,1)
                    topic_name = topic_name_msg[0]
                    topic_msg = topic_name_msg[1]
                    if topic == topic_name.decode('utf-8'):
                        self.topics_callbacks[topic](topic_msg)

    def stop(self):
        self.loop = False

class Publisher:
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_signal)
        self.zmq_context = zmq.Context()
        self.setup_subscriber()
        self.nav_gps_msg = None
        self.mag_declination = -14.42   #declination at MIT
        #setup flatbuffers
        self.fb_builder = flatbuffers.Builder(1024)
        #setup IMU sensor
        self.MAG_RATE       = 100  #Hz
        self.ACCEL_RATE     = 200  #Hz
        self.GYRO_RATE      = 200  #Hz
        self.BARO_RATE      = 50   #Hz
        self.Q_RATE_DIVISOR = 3    #1/3 gyro rate
        self.em7180 = EM7180_Master(self.MAG_RATE, self.ACCEL_RATE, self.GYRO_RATE, self.BARO_RATE, self.Q_RATE_DIVISOR)
        if not self.em7180.begin(2):
            print('IMU initialization error!')
            print(self.em7180.getErrorString())
            exit(1)

    def exit_signal(self, sig, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

    def setup_subscriber(self):
        self.subscriber = Subscriber(self.zmq_context, 0, {'nav.gps':self.nav_gps_callback})
        self.subscriber.start()

    def nav_gps_callback(self, msg):
        self.nav_gps_msg = topics.nav.gps.gps.GetRootAsgps(msg, 0)

    def run(self):
        socket = self.zmq_context.socket(zmq.PUB)
        socket.connect("tcp://127.0.0.1:5556")

        count = 0
        while True:
            count += 1

            if self.nav_gps_msg is not None:
                self.mag_declination = self.nav_gps_msg.Mag_Declination()

            self.em7180.checkEventStatus()

            if self.em7180.gotError():
                print('IMU runtime error: ' + self.em7180.getErrorString())
                exit(1)

            topics.nav.imu.imuStart(self.fb_builder)
            topics.nav.imu.imuAddTime(self.fb_builder, time.time())

            if (self.em7180.gotQuaternion()):
                qw, qx, qy, qz = self.em7180.readQuaternion()
                roll  = math.atan2(2.0 * (qw * qx + qy * qz), qw * qw - qx * qx - qy * qy + qz * qz)
                pitch = -math.asin(2.0 * (qx * qz - qw * qy))
                yaw   = math.atan2(2.0 * (qx * qy + qw * qz), qw * qw + qx * qx - qy * qy - qz * qz)

                pitch *= 180.0 / math.pi
                yaw   *= 180.0 / math.pi
                yaw   += self.mag_declination
                if yaw < 0: yaw   += 360.0  # Ensure yaw stays between 0 and 360
                roll  *= 180.0 / math.pi
                print('roll, pitch, yaw: {:2.2f}, {:2.2f}, {:2.2f}'.format(roll,pitch,yaw))
                topics.nav.imu.imuAddRoll(self.fb_builder, roll)
                topics.nav.imu.imuAddPitch(self.fb_builder, pitch)
                topics.nav.imu.imuAddYaw(self.fb_builder, yaw)

            if self.em7180.gotAccelerometer():
                ax,ay,az = self.em7180.readAccelerometer()
                print('accel: {:3.3f}, {:3.3f}, {:3.3f}'.format(ax,ay,az))
                topics.nav.imu.imuAddAccelX(self.fb_builder, ax)
                topics.nav.imu.imuAddAccelY(self.fb_builder, ay)
                topics.nav.imu.imuAddAccelZ(self.fb_builder, az)

            if self.em7180.gotGyrometer():
                gx,gy,gz = self.em7180.readGyrometer()
                print('gyro: {:3.3f}, {:3.3f}, {:3.3f}'.format(gx,gy,gz))
                topics.nav.imu.imuAddGyroX(self.fb_builder, gx)
                topics.nav.imu.imuAddGyroY(self.fb_builder, gy)
                topics.nav.imu.imuAddGyroZ(self.fb_builder, gz)

            if self.em7180.gotBarometer():
                pressure, temperature = self.em7180.readBarometer()
                print('baro:')
                print('  temperature: {:2.2f} C'.format(temperature))
                print('  pressure: {:2.2f} mbar'.format(pressure))
                topics.nav.imu.imuAddTemp(self.fb_builder, temperature)
                topics.nav.imu.imuAddPressure(self.fb_builder, pressure)

            imu_msg = topics.nav.imu.imuEnd(self.fb_builder)
            self.fb_builder.Finish(imu_msg)
            bin_imu_msg = self.fb_builder.Output()
            socket.send(b'nav.imu' + b' ' + bin_imu_msg)

            time.sleep(.01)

if __name__ == "__main__":
    pub = Publisher()
    pub.run()
