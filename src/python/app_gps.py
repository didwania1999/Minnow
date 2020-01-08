#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import zmq
import time
# minnow comms
from minnow_comms.minnow_app_multiprocess import App
# flatbuffer serialization
import flatbuffers
# generated by flatc
import topics.nav.gps
# depth driver MS5837
from minnow_drivers.pyZOEM8 import pyZOEM8

class GPS(App):
    def __init__(self):
        super().__init__()
        self.setup_subscribers()
        # setup flatbuffers
        self.fb_builder = flatbuffers.Builder(1024)
        # setup GPS sensor
        self.zoe_m8q = ZOEM8(2)

    def setup_subscribers(self):
        pass    # no subscriptions for this app

    def process(self):
        self.zoe_m8q.read()

        topics.nav.gps.gpsStart(self.fb_builder)
        topics.nav.gps.gpsAddTime(self.fb_builder, time.time())
        topics.nav.gps.gpsAddStatus(self.fb_builder, self.zoe_m8q.position_status)
        topics.nav.gps.gpsAddMode(self.fb_builder, self.zoe_m8q.mode)
        topics.nav.gps.gpsAddQuality(self.fb_builder, self.zoe_m8q.quality)
        topics.nav.gps.gpsAddLongitude(self.fb_builder, self.zoe_m8q.longitude)
        topics.nav.gps.gpsAddLatitude(self.fb_builder, self.zoe_m8q.latitude)
        topics.nav.gps.gpsAddAltitude(self.fb_builder, self.zoe_m8q.altitude)
        topics.nav.gps.gpsAddUtc(self.fb_builder, self.zoe_m8q.utc)
        topics.nav.gps.gpsAddNumSatellites(self.fb_builder, self.zoe_m8q.num_satellites)
        topics.nav.gps.gpsAddSpeed(self.fb_builder, self.zoe_m8q.speed_over_ground)
        topics.nav.gps.gpsAddCourse(self.fb_builder, self.zoe_m8q.course_over_ground)
        topics.nav.gps.gpsAddHdop(self.fb_builder, self.zoe_m8q.horizontal_dilution)
        topics.nav.gps.gpsAddMagDeclination(self.fb_builder, self.zoe_m8q.magnetic_declination)

        print('Quality: {}'.format(self.zoe_m8q.quality))
        print('UTC: {:10.3f} s'.format(self.zoe_m8q.utc))
        print('Latitude: {:6.5f} deg'.format(self.zoe_m8q.latitude))
        print('Longitude: {:6.5f} deg'.format(self.zoe_m8q.longitude))
        print('Magnetic Declination: {:6.5f} deg'.format(self.zoe_m8q.magnetic_declination))

        gps_msg = topics.nav.gps.gpsEnd(self.fb_builder)
        self.fb_builder.Finish(gps_msg)
        bin_gps_msg = self.fb_builder.Output()
        self.publish(b'nav.gps' + b' ' + gps_msg)

        time.sleep(0.001)

if __name__ == "__main__":
    app = GPS()
    app.run()
