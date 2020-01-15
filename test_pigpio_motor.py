#!/usr/bin/python
# -*- coding: utf-8 -*-

import pigpio
import time

PIN = 17

Frequency = 2
Duty = 500000

pi = pigpio.pi()
pi.set_mode(PIN, pigpio.OUTPUT)
#pi.set_mode(PIN, pigpio.ALT0)

pi.harware_PWM(PIN, Frequency, Duty)

time.sleep(5)

pi.harware_PWM(PIN, Frequency, 0)
pi.stop()
pi = None
