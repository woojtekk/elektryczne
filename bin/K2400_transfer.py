#!/usr/bin/python
# -*- coding: utf-8 -*-
import K2400
import logging
import time
from multiprocessing.pool import ThreadPool
from datetime import datetime
#import numpy
#import argparse
#import signal
#import os
#import fcntl
#import sys
#import shutil
#import serial, time, datetime


#---------------------------------------------------------------------------------------------------------------
#------------------------------------------ TRANSFER STEPS
#---------------------------------------------------------------------------------------------------------------
#def transfer_steps(ser[0], ser_VGS, VDS, VDS_comp, VGS_start, VGS_stop, VGS_step, VGS_comp, NPLC=1, DEL=0.001):
def transfer_steps(ser, *param):
        logging.info("********* TRANSFER_STEPS_START *********")
	start_time = datetime.now()
        sa  = ser[0]
        sb  = ser[1]
        sc  = ser[2]

	LogFileName	= param[0]
	LogFileName	= param[0]+"_transfer.txt"
	VDS		= float(param[1])
	VGS_start	= float(param[2])
	VGS_stop	= float(param[3])
	VGS_step	= float(param[4])
	VDS_comp	= float(param[5])
	VGS_comp	= float(param[6])
	NPLC		= float(param[7])
	DEL		= float(param[8])
	SWEEP		= param[9]
	ttime		= float(param[10])
	SHUTTER		= param[11]
        sht             = K2400.sht()
        sht             = K2400.sht()

        K2400.log_init(LogFileName)

        if VGS_start < VGS_stop: VGS_step = +1*abs(float(VGS_step))
        else:                    VGS_step = -1*abs(float(VGS_step))

        VGS_todo=[float(VGS_start)]
	pts=range(1,int(abs((float(VGS_stop)-float(VGS_start))/float(VGS_step))+1))
        for x in pts: VGS_todo.append(round(VGS_todo[x-1]+float(VGS_step)         ,4))
	if SWEEP:
		VGS_todo.append(VGS_stop)
        	for x in pts: VGS_todo.append(round(VGS_todo[len(pts)+x]-float(VGS_step),4))


	txt=	"#--------------------------------------------------------------------------------\n"\
		"# \t INIT TRANSFER TEST .....						       \n#\n"\
		"# VDS       : " + str(VDS      ) + " \t Current compliance " + str(VDS_comp) + "\n"\
		"# VGS       : " + str(VGS_start) + " \t Current compliance " + str(VGS_comp) + "\n"\
		"# VGS_STOP  : " + str(VGS_stop ) + "\n"\
		"# VGS_STEP  : " + str(VGS_step ) + "\n"\
		"# NPLC      : " + str(NPLC     ) + "\n"\
		"# DELETE    : " + str(DEL      ) + "\n"\
		"# SWEEP     : " + str(SWEEP    ) + "\n"\
		"# Number of Pts.: " +str(len(pts))+"\n"\
                "# pozycja poczatkowa szhuttera: " +str(sht) +" keep open "+ str(SHUTTER)+ " before measurmeents\n"\
		"# TIME START:     " +str(datetime.now())+"\n"\
        	"# :: --------------------------- transfer ------------------------------------------\n" +\
        	"# ::   VGS          IDS           IGS           VDS         IDS_Time       delta    \n" +\
        	"# :: -------------------------------------------------------------------------------"

	K2400.log_save(txt)

        if SHUTTER:
		txt="# :: ---------- SHUTTER open for "+str(SHUTTER)+"sec. before measurements. [Shutter status:"+str(K2400.sht())+"]"
		K2400.log_save(txt)
		time.sleep(SHUTTER)

	# init measurement
        K2400.set_voltage_init(ser[0], 0, VDS_comp, NPLC, DEL)
	K2400.set_voltage_init(ser[1], 0, VGS_comp, NPLC, DEL)


	# ------------------ proceed measurements
	K2400.set_voltage(ser[0], VDS)
        for VGS_SET in VGS_todo:
                if K2400.switch() == "OFF": break
		if ttime > 0:
			timestart = time.time()
			timeout   = timestart+ttime	# everythng in secounds
			txt 	  = str(VGS_SET)
			i=igs=ids=0
			while True:
		                if K2400.switch() == "OFF": break

				pool        = ThreadPool(6)
                		resoults    = pool.map(K2400.set_voltage2, [(ser[0],VDS),(ser[1],VGS_SET)])
		                pool.close()
                		VDS_I,VDS_T = resoults[0]
		                VGS_I,VGS_T = resoults[1]

				i+=1
				ids+=float(VDS_I)
				igs+=float(VGS_I)

				txt += " " + str(VDS_I) + " " + str(VGS_I)
				ttx = str(VGS_SET) + " " + " " + str(VDS_I) + " " + str(VGS_I) + " " + str(time.time()-timestart)

				if time.time() > timeout:
					ttx+= " | " + str(ids/i) + " " + str(igs/i)
					K2400.log_save_raw(ttx)
					break
				else:
					K2400.log_save_raw(ttx)

			txt= txt + " || " + str(ids/i) + " " + str(igs/i)
			K2400.log_save(txt)

		elif ttime==0:
                        pool        = ThreadPool(6)
                        resoults    = pool.map(K2400.set_voltage2, [(ser[0],VDS),(ser[1],VGS_SET)])
                        pool.close()
                        VDS_I,VDS_T = resoults[0]
                        VGS_I,VGS_T = resoults[1]

        	        txt = str(VGS_SET) + " " + str(VDS_I) + " " + str(VGS_I) 
			K2400.log_save(txt)


        K2400.file_footer(ser[0], ser[1])

        return 0


if __name__ == '__main__':
	#------- TRANSFER: parametry pomiaru
	FName     = K2400.PATH_DATA+K2400.FILE_NAME
	VDS       = 50
	VGS_start = 0
	VGS_stop  = 50
	VGS_step  = 2
	VDS_comp  = 0.001
	VGS_comp  = 0.001
	NPLC      = 1
	DEL       = 0
	SWEEP	  = True

	param_transfer = [FName, VDS, VGS_start, VGS_stop, VGS_step, VDS_comp, VGS_comp,  NPLC, DEL,SWEEP]
	sa,sb=K2400.init()
	transfer_steps(sa,sb,*param_transfer)

