#!/usr/bin/python
# -*- coding: utf-8 -*-
import serial
import os
import sys
import time
from datetime import datetime


def shutter(ser,cmd):
	ser.write(cmd)
	return ser.readline()

def shutter_check(ser):
	ser.write('?')
	return int(ser.readline().split(':')[1])

if __name__ == "__main__":
	print "...::: SSHT :::..."
	ser = serial.Serial('/dev/ttyACM0', 9600,timeout=1)
        time.sleep(2)

	print "STATUS::",shutter_check(ser),

	if len(sys.argv) == 2:
		if (str(sys.argv[1]) == "ON") or (str(sys.argv[1]) == "O") or (str(sys.argv[1]) == "1"):
			if (shutter(ser,"O").split(':')[1].rstrip()) == " ON":
				print "OPEN SHUTTER"
			else:
				print "stye the same"

		if (str(sys.argv[1]) == "OFF") or (str(sys.argv[1]) == "F") or (str(sys.argv[1]) == "0"):
			if (shutter(ser,"F").split(':')[1].rstrip()) == " OFF":
				print "CLOSE SHUTTER"
			else:
				print "stye the same"

	print "STATUS::",shutter_check(ser)
