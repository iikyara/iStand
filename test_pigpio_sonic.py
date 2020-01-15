#!/usr/bin/env python
# -*- coding: utf-8 -*-
# HC-SR04 ultrasonic range sensor
# with ADT7410 temperature sensor for sonic velocity correction
# ultrasonic
#   GPIO 17 output  = "Trig"
#   GPIO 27 input = "Echo"


import time
import pigpio
#import smbus

# prepare for ADT7410 temperature sensor
#bus = smbus.SMBus(1)
'''
address_adt7410 = 0x48
register_adt7410 = 0x00
'''

# prepare for HC-SR04 ultrasonic sensor
PIN1 = {
    'ECHO' : 14,
    'TRIG' : 15
}
PIN2 = {
    'ECHO' : 17,
    'TRIG' : 27
}
pig = pigpio.pi()
pig.set_mode(PIN1['ECHO'], pigpio.INPUT)
pig.set_mode(PIN1['TRIG'], pigpio.OUTPUT)
pig.set_mode(PIN2['ECHO'], pigpio.INPUT)
pig.set_mode(PIN2['TRIG'], pigpio.OUTPUT)
'''
pig.set_mode(PIN1['ECHO'], pigpio.ALT0)
pig.set_mode(PIN1['TRIG'], pigpio.ALT0)
pig.set_mode(PIN2['TRIG'], pigpio.ALT0)
pig.set_mode(PIN2['ECHO'], pigpio.ALT0)
'''
'''
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(27,GPIO.IN)
'''
# detect temperature in C
'''
def read_adt7410():
    word_data =  bus.read_word_data(address_adt7410, register_adt7410)
    data = (word_data & 0xff00)>>8 | (word_data & 0xff)<<8
    data = data>>3 # 13�r�b�g�f�[�^
    if data & 0x1000 == 0:  # ���x�����܂���0�̏ꍇ
        temperature = data*0.0625
    else: # ���x�����̏ꍇ�A ���Βl�������Ă����}�C�i�X��������
        temperature = ( (~data&0x1fff) + 1)*-0.0625
    return temperature
'''

def reading_sonic(sensor, temp, PIN):
    if sensor == 0:
        #GPIO.output(17, GPIO.LOW)
        pig.write(PIN['TRIG'], 0)

        time.sleep(0.3)
        # send a 10us plus to Trigger
        pig.write(PIN['TRIG'], 1)
        time.sleep(0.00001)
        pig.write(PIN['TRIG'], 0)

        # detect TTL level signal on Echo
        '''
        while GPIO.input(27) == 0:
          signaloff = time.time()
        while GPIO.input(27) == 1:
          signalon = time.time()
        '''
        while pig.read(PIN['ECHO']) == 0:
          signaloff = time.time()
        while pig.read(PIN['ECHO']) == 1:
          signalon = time.time()

        # calculate the time interval
        timepassed = signalon - signaloff

        # we now have our distance but it's not in a useful unit of
        # measurement. So now we convert this distance into centimetres
        distance = timepassed * (331.50 + 0.606681 * temp)* 100/2

        # return the distance of an object in front of the sensor in cm
        return distance

        # we're no longer using the GPIO, so tell software we're done
        #GPIO.cleanup()

    else:
        print "Incorrect usonic() function varible."

try:
    while True:
        #temp = read_adt7410()
        temp =
        print "temperature[C] =", round(temp, 1)
        print("\tdistance 1 to obstcle = ", round(reading_sonic(0, temp, PIN1),1), "[cm]",
              "\tdistance 2 to obstcle = ", round(reading_sonic(0, temp, PIN2),1), "[cm]")
        time.sleep(0.5)
except KeyboardInterrupt:
    pass

GPIO.cleanup()
