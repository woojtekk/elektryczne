#!/usr/bin/python
# -*- coding: utf-8 -*-
import K2400
import K2400_help
import K2400_time
import K2400_output
import K2400_transfer
import signal
import logging
import serial
import os
import fcntl
import sys
import shutil
import time
from datetime import datetime
#import numpy
#import argparse
#import serial, time, datetime

USB_VGS     = "/dev/ttyUSB1"
USB_VDS     = "/dev/ttyUSB2"
USB_PICO    = "/dev/ttyPICO"
USB_SHUTTER = "/dev/ttySHUTTER"

PATH          = "/home/mar345/src/ele4/"
PATH_LOG      = PATH+"/log/"
PATH_DATA     = PATH+"/data/"
FILE_NAME     = "TR_TEST"
FILE_SSHT     = PATH+"/wd/shutter.txt"
FILE_CHANGE   = PATH+"/wd/change.txt"
FILE_SWITCH   = PATH+"/wd/switch.txt"
FILE_COMMENTS = PATH+"/wd/comments.txt"
PICNPLC=1.0
SSHT=0
FILE=0

#def shtt():return sht()

def sht():
	global SSHT
	global USB_SHUTTER
	if SSHT!=0:
		return sht_change()
	else:
		SSHT = serial.Serial(USB_SHUTTER, 9600,timeout=1)
		time.sleep(1)
		sht()
	return 0

def sht_change():
	global SSHT
	global FILE
	status = int(port_wr(SSHT,"?").split(":")[1])

        with open(FILE_SSHT, 'r') as f:
                l = str(f.readline()).rstrip().split(" ")
		line = l[0]
                if line == "ON"  or line == "O" or line == "1": new_status = 1
                if line == "OFF" or line == "F" or line == "0": new_status = 0

		if len(l)==2: line="Shutter open for "+str(l[1])+" seconds before measurements starts."

		if new_status != status or not FILE:
			SSHT.write(str(new_status))
			#txt="SHUTTER STATUS: "+str(new_status)+" ["+str(line)+"]"
			#with open(FILE_COMMENTS , 'w+') as the_file: the_file.write(txt)


	return int(port_wr(SSHT,"?").split(":")[1])

def port_write(ser,cmd):
        cmd = cmd+"\n"
        ser.write(cmd)
        return 0

def port_read(ser):
        out = ''
        c = ser.read()
        while c!='\r': #\n
		#print ord(c),c
                out += c
                c = ser.read()
	return out

def port_wr(ser,cmd):
        port_write(ser,cmd)
        return str(port_read(ser))

def get_TUI(ser):
#	return port_wr(ser,"MEASure?").split(",")
	return port_wr(ser,"READ?").split(",")

def get_PICO(ser):
	return port_wr(ser,"MEASure?")

def set_voltage2(a):
	return set_voltage(*a)

def set_voltage(ser, set_VOLT):
        port_write(ser,":SOUR:VOLT:LEV "+str(set_VOLT)) # Set source output level to 10V.
        return port_wr(ser,"READ?").split(",") # Trigger and acquire one data string.

def set_voltage_init(ser, set_VOLT, set_compl, NPLC, DELAY):
        logging.info("SET_VOLTAGE_INIT: "+str(ser))
        logging.info(str(set_VOLT) +" "+ str(set_compl) +" "+ str(NPLC) +" "+ str(DELAY)+" OUTPUT ON")

        port_write(ser,":SOUR:FUNC VOLT") # Select voltage source function.
        port_write(ser,":SOUR:VOLT:MODE FIX") # Select fixed voltage source mode.
        port_write(ser,":SOUR:VOLT:LEV "+str(float(set_VOLT)) ) # Set source output level to 10V.
	port_write(ser,":SOUR:DEL "+str(DELAY) ) # Set delay between set volt and measure
        port_write(ser,":SENS:FUNC 'CURR'" ) # Select current measurement function.
        port_write(ser,":SENS:CURR:NPLC "+str(NPLC) ) # Select current measurement function.
	if set_compl != 0:
		port_write(ser,":SENS:CURR:PROT "+str(set_compl) )	# Set compliance limit to 10mA.
		port_write(ser,":SENS:CURR:RANG "+str(set_compl) ) # Select the 10mA measurement range.
	else:
		port_write(ser,":SENS:CURR:PROT AUTO" ) # Set compliance limit to auto.
		port_write(ser,":SENS:CURR:RANG AUTO" ) # Select the auto measurement range.
        port_write(ser,":OUTP ON") # Turn the output on.


def log_reset():
	with open(FILE_COMMENTS, "w") as f: f.write("init_log")
	with open(FILE_SSHT    , "w") as f: f.write("0")
	with open(FILE_CHANGE  , "w") as f: f.write("")
        with open(FILE_SWITCH  , 'w') as f: f.write("ON")

def log_init(FName):
	global FILE

	FName = checkfile(FName)
	logging.info("Create NEW FILE: "+FName)

	with open(PATH+"/log/FName_Last", 'r') as f: LastFName=str(f.readline())
	with open(PATH+"/log/FName_Last", 'w') as f: f.write(FName)
	with open(PATH+"/FName", 'w') as f: f.write(FName)
	shutil.move(str(PATH)+"/raw.txt",LastFName+".raw" )

	with open(str(PATH)+"/raw.txt", 'aw+') as the_file: the_file.write("")
	FILE = open(str(FName),"w")
	FILE.write("#-------------- Creating on "+str(os.uname()[1])+" @ "+str( datetime.now())+"\n" )
	return 0

def log_save(txt):
	log_save_to_file(txt)
	log_save_comments()
	log_save_raw(txt)

def log_save_comments():
	if os.path.isfile(FILE_COMMENTS) and os.path.getsize(FILE_COMMENTS) > 0:
		with open(FILE_COMMENTS, "r") as f: txt="#------ comments: "+str(f.readline()).rstrip()
		with open(FILE_COMMENTS, "w"): pass
		print txt
		log_save_to_file(txt)

def log_save_to_file(txt):
	global FILE
	FILE.write(str(txt)+"\n")

def log_save_raw(txt):
	with open(PATH_LOG+'/raw_all.txt', 'a') as the_file: the_file.write(str(txt)+"\n")
	with open(PATH+'/raw.txt' , 'a')        as the_file: the_file.write(str(txt)+"\n")
	print txt
	return 0

def checkfile(path):
        logging.info("CHECK FILE: "+path)
        path = os.path.expanduser(path)
        root, ext = os.path.splitext(os.path.expanduser(path))
        dir = os.path.dirname(root)
        fname = os.path.basename(root)
        candidate = fname+ext
        index = 1
        ls = set(os.listdir(dir))
        while candidate in ls:
                candidate = "{0}_{1:02d}{2}".format(fname,index,ext)
                index += 1
        ffname = os.path.join(dir,candidate)
        logging.info("CHECK FILE: "+path)
        logging.info("CHECK FILE will save:"+ffname)
        return ffname

def signal_handler(signal, frame):
	K2400.log_save("#::::: ABORT ::::::")
        print "\n:: You pressed Ctrl+C!"
        print "::Programm will be TERMINATED ... \n . . .  .  .  .    .    .     .       ."
	with open(FILE_SWITCH, 'w+') as the_file: the_file.write("OFF")


def init():
	global ser_VGS
	global ser_VDS
	logging.info("--------------- NEW ------------------")
	logging.info("INIT - START")

	logging.info("INIT:: USB_VDS:"+USB_VDS)
	logging.info("INIT:: USB_VGS:"+USB_VGS)
	logging.info("INIT:: USB_PIC:"+USB_PICO)

        ser_VDS = init_port(USB_VDS)
        ser_VGS = init_port(USB_VGS)
        ser_PIC = init_port(USB_PICO)
	logging.info("INIT:: ser_VDS:"+str(ser_VDS))
	logging.info("INIT:: ser_VGS:"+str(ser_VGS))
	logging.info("INIT:: ser_PIC:"+str(ser_PIC))

        init_controler(ser_VDS)
        init_controler(ser_VGS)
        init_controler_pic(ser_PIC)
        logging.info("INIT - END")
        return ser_VDS, ser_VGS, ser_PIC

def init_port(PortUSB):
        signal.signal(signal.SIGINT, signal_handler)

        ser = serial.Serial(
                port=PortUSB,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1,
                xonxoff=0,
                rtscts=1)

        if ser.isOpen():
                try:
                        fcntl.flock(ser.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except IOError:
                        print ":: K2400 :: Port temporarily unavailable ..... exit"
                        sys.exit()
        else:
                print ":: K2400 :: Some problem with Port ...... exit"
                sys.exit()

        ser.flushOutput()
        ser.flushInput()
        logging.info("INIT_PORT")
        return ser

def init_controler(ser):
        if ser.isOpen():
                try:
                        ser.flushInput() #flush input buffer, discarding all its contents
                        ser.flushOutput() #flush output buffer, aborting current output
                                                        #and discard all that is in buffer
                        port_write(ser,':ABORt')
                        port_write(ser,"*RST")
                        port_write(ser,"TRIG:CLE") # Clear any pending input triggers
                        port_write(ser,":SYSTem:TIME:RESet:AUTO 0") # zerujemy zegar
                        port_write(ser,":SYSTem:LFRequency:AUTO ON") # ustawiamy automatyczny dobor czestotliwosci
                        port_write(ser,":SYSTem:BEEPer 300, 0.4")
                        port_write(ser,":FORM:ELEM CURR,TIME")
#                        port_write(ser,":DISPlay:ENABle OFF")

                except Exception, e1:
                        print ":: ERROR: promlem with communicating ...: " + str(e1)
        else:
                print ":: ERROR: Can not open serial port: ",ser
        logging.info("INIT_CONTROLER")
        return 0

def init_controler_pic(ser):
        if ser.isOpen():
                try:
                        ser.flushInput() 	#flush input buffer, discarding all its contents
                        ser.flushOutput() 	#flush output buffer, aborting current output
						#and discard all that is in buffer
                        port_write(ser,"*CLS")
                        port_write(ser,"*RST")
                        port_write(ser,"FORM:ELEM READ,TIME")
                        port_write(ser,":RANGe:AUTO:ULIMit")
                        port_write(ser,"CURR:NPLC "+str(PICNPLC/2))
                        port_write(ser,":MEASure?")
			#port_write(ser,":DISPlay:ENABle OFF")

                except Exception, e1:
                        print ":: ERROR: promlem with communicating ...: " + str(e1)
        else:
                print ":: ERROR: Can not open serial port: ",ser
        logging.info("INIT_CONTROLER_PIC")

        return 0

def port_close(ser):
        print ":: Ports close...."
        for s in ser:
		logging.info(s)
	        s.close()
	        logging.info("PORT: CLOSE")

def format_e(n):
    a = '%E' % n
    return a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]

def switch():
        with open(FILE_SWITCH, 'r') as f:
                line = str(f.readline())
                line = line.rstrip()
                if line == "OFF":
		        logging.info("USE SWITCH: OFF")
		        with open(FILE_SWITCH , 'w+') as the_file: the_file.write("ON")
                        return "OFF"
                else:
                        return "ON"

def change():
	VGS=-888
	VDS=-888

        if os.path.isfile(FILE_CHANGE ) and  os.path.getsize(FILE_CHANGE) > 0:
                with open(FILE_CHANGE , 'r') as f:
			lines = len(f.readlines())
			f.seek(0)
			if lines == 2:
				line = f.readlines()
				if   line[0].split("=")[0] == "VGS": VGS = float(line[0].split("=")[1])
				elif line[0].split("=")[0] == "VDS": VDS = float(line[0].split("=")[1])
				if   line[1].split("=")[0] == "VGS": VGS = float(line[1].split("=")[1])
				elif line[1].split("=")[0] == "VDS": VDS = float(line[1].split("=")[1])
				else : return False,0,0

			if lines == 1:
				line = f.readlines()
				if   line[0].split("=")[0] == "VGS": VGS = float(line[0].split("=")[1])
				elif line[0].split("=")[0] == "VDS": VDS = float(line[0].split("=")[1])
				else : return False,0,0

			with open(FILE_CHANGE, "w"): pass
                        txt="#------ comments: Change VGS or VDS: "+str(line)
			log_save(txt)
                        #print txt
			return "True",VGS,VDS
	else:
		return "False",VGS,VDS

def file_header(ser_VGS, ser_VDS):
        logging.info("CREATE FILE HEADER")
	return 0

def file_footer(ser_VGS, ser_VDS):
        logging.info("CREATE FILE FOOTER")
	global File

        off(ser_VGS)
        off(ser_VDS)
	with open(FILE_SSHT , 'w+') as the_file: the_file.write("OFF")
	sht()

	log_save("#\n#----------------------- FOOTER ------------------------------------")
	log_save("# DEV_1 VDS: "+" "+port_wr(ser_VDS,'*IDN?'))
	log_save("# DEV_1 VDS: "+ str(ser_VDS))
	log_save("# DEV_2 VGS: "+" "+port_wr(ser_VGS,'*IDN?'))
	log_save("# DEV_1 VDS: "+ str(ser_VGS))
	log_save("#")
        log_save(port_error(ser_VDS,"VDS"))
        log_save(port_error(ser_VGS,"VGS"))
	log_save("#")
	log_save("# ----* zajaczkowksi@mpip-mainz.mpg.de *-------------------------------")
	log_save("# ----- End of file "+str(datetime.now())+" created by:"+str(__file__))

	return 0

def off(ser):
        logging.info("SENS OFF [:OUTP OFF]")
        port_write(ser,":OUTP OFF")

def port_error(ser,cmd):
        logging.info("READ ERRORS")
	err =[":STAT:MEAS?  ",
		":SYST:ERR:ALL?",
		"*ESR?  ",
		"*OPC?  ",
		":STAT:OPER?  ",
		":STAT:MEAS?  ",
		":STAT:QUES?  "]
	out="# ======= ERROR'S @ "+str(cmd)+"\n#"
	for x in err: out+= "# "+ str(x)+ " \t " +str(port_wr(ser,x)) + " \n#"
	#print out
	return out



# ============================= MAIN

if __name__ == '__main__':
	args = K2400_help.help()
	log_reset()

#------- podstawowe parametry:
	if args.filename != "tr00": FILE_NAME=args.filename
	if args.shutter: 
		print "SHUTTER WILL BE OPEN"
		with open(FILE_SSHT , 'w+') as the_file: the_file.write("ON "+str(args.shutter))


	if args.out:
		#------- OUTPUT: parametry pomiaru
                FName = PATH_DATA+FILE_NAME
		VDS_start= float(args.out[0][0])
		VDS_stop = float(args.out[0][1])
		VDS_step = float(args.out[0][2])
		VDS_comp = float(args.DCOMP)

		VGS_start= float(args.out[0][3])
		VGS_stop = float(args.out[0][4])
		VGS_step = float(args.out[0][5])
		VGS_comp = float(args.GCOMP)

		NPLC     = float(args.NPLC)
		PICNPLC  = NPLC
		DEL      = float(args.DEL)
		SWEEP    = True

	        ser = init()
	        output_param = [FName, VDS_start, VDS_stop, VDS_step, VDS_comp, VGS_start, VGS_stop, VGS_step, VGS_comp, NPLC, DEL,SWEEP]
		K2400_output.output_steps(ser,*output_param)
		port_close(ser)

        if args.timee:
		#------- TIME: parametry pomiaru
       		FName = PATH_DATA+FILE_NAME
        	VDS = float(args.timee[0][0])
        	VGS = float(args.timee[0][1])
        	VDS_comp = args.DCOMP
        	VGS_comp = args.GCOMP
        	NPLC = args.NPLC
		PICNPLC  = NPLC
        	DEL = args.DEL
		sht 	  = args.shutter

	        ser = init()
        	param_timesteps = [FName, VDS, VDS_comp, VGS, VGS_comp, NPLC, DEL, sht]
        	K2400_time.time_steps(ser,*param_timesteps)
		port_close(ser)


	if args.trans :
		#------- TRANSFER: parametry pomiaru
		FName = PATH_DATA+FILE_NAME
		VDS       = args.trans[0][0]
		VGS_start = args.trans[0][1]
		VGS_stop  = args.trans[0][2]
		VGS_step  = args.trans[0][3]
		VDS_comp  = args.DCOMP
		VGS_comp  = args.GCOMP
		NPLC      = args.NPLC
		PICNPLC  = NPLC
		DEL       = args.DEL
		SWEEP     = True
		ttime     = args.wait
		sht 	  = args.shutter

        	param_transfer = [FName, VDS, VGS_start, VGS_stop, VGS_step, VDS_comp, VGS_comp, NPLC, DEL, SWEEP, ttime, sht]
	        ser = init()
	        K2400_transfer.transfer_steps(ser,*param_transfer)
		port_close(ser)

        sys.exit()




