#!/usr/bin/python
# -*- coding: utf-8 -*-
import K2400
import logging
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
#------------------------------------------ OUTPUT STEPS
#---------------------------------------------------------------------------------------------------------------
def output_steps(ser,*param):
	a=[ser[0],66]
	print len(a)
        logging.info("********* OUTPUT_STEPS_START *********")
	start_time = datetime.now()


	LogFileName	= str(param[0])+"_output.txt"
	VDS_start       = float(param[1])
	VDS_stop        = float(param[2])
	VDS_step        = float(param[3])
	VDS_comp        = float(param[4])
	VGS_start       = float(param[5])
	VGS_stop        = float(param[6])
	VGS_step        = float(param[7])
	VGS_comp        = float(param[8])
	NPLC            = float(param[9])
	DEL             = float(param[10])
	SWEEP		= param[11]

        K2400.log_init(LogFileName)


        if VGS_start < VGS_stop:  VGS_step =  1*abs(float(VGS_step))
        else:                     VGS_step = -1*abs(float(VGS_step))
        if VDS_start < VDS_stop:  VDS_step =  1*abs(float(VDS_step))
        else:                     VDS_step = -1*abs(float(VDS_step))

        VGS_todo=[float(VGS_start)]
        for x in range(1,int(abs((float(VGS_stop)-float(VGS_start))/float(VGS_step))+1)):
                VGS_todo.append(round(VGS_todo[x-1]+float(VGS_step),4))

        VDS_todo=[float(VDS_start)]
        for x in range(1,int(abs((float(VDS_stop)-float(VDS_start))/float(VDS_step))+1)):
                VDS_todo.append(round(VDS_todo[x-1]+float(VDS_step),4))

	if SWEEP :
	        for x in range(1,int(abs((float(VDS_stop)-float(VDS_start))/float(VDS_step))+1)):
        	        VDS_todo.append(round(VDS_todo[int(abs((float(VDS_stop)-float(VDS_start))/float(VDS_step))+1)-x]-float(VDS_step),4))


	# init measurement
        K2400.set_voltage_init(ser[0], 0, VDS_comp, NPLC, DEL)
	K2400.set_voltage_init(ser[1], 0, VGS_comp, NPLC, DEL)

	txt=	"# INIT OUTPUT TEST .....\n#\n"\
		"# VDS_START : " + str(VDS_start) + " \t Compliance " + str(VDS_comp) + "\n"\
		"# VDS_STOP  : " + str(VDS_stop ) + "\n"\
		"# VDS_STEP  : " + str(VDS_step ) + "\n"\
		"# VGS_START : " + str(VGS_start) + " \t Compliance " + str(VGS_comp) + "\n"\
		"# VGS_STOP  : " + str(VGS_stop ) + "\n"\
		"# VGS_STEP  : " + str(VGS_step ) + "\n"\
		"# NPLC      : " + str(NPLC     ) + "\n"\
		"# DELETE    : " + str(DEL      ) + "\n"\
		"# SWEEP     : " + str(SWEEP    ) + "\n"\
        	"# :: -------------------------------------------------------------------------------\n" +\
        	"# ::   VDS     |       VGS           IDS           IGS     ::  ....   \n" +\
        	"# :: -------------------------------------------------------------------------------"

	K2400.log_save(txt)
	print txt

	M=[]
	MM=[]

	for VDS_S in VDS_todo: 	M.append(str(K2400.format_e(VDS_S))+" | ")
	MM.append(M)

	tstart = datetime.now()
	swexit = False
        for VGS_S in VGS_todo:
		M=[]
		K2400.set_voltage(ser[1], VGS_S)
		if swexit: break

		for VDS_S in VDS_todo:
			pool        = ThreadPool(6)
			resoults    = pool.map(K2400.set_voltage2, [(ser[0],VDS_S),(ser[1],VGS_S)])
			pool.close()
                        VDS_I,VDS_T = resoults[0]
                        VGS_I,VGS_T = resoults[1]

#			VDS_I,VDS_T =  K2400.set_voltage(ser[0], VDS_S)
#			VGS_I,VGS_T =  K2400.set_voltage(ser[1], VGS_S)

			txt = str(VGS_S) + " " + str(VDS_I) + " " + str(VGS_I) + " :: "
			ttx = str(VDS_S) + " " + str(VDS_I) + " " + str(VGS_I)

			print ttx

			K2400.log_save_raw(ttx)
			M.append(txt)
	                if K2400.switch() == "OFF":
				swexit=True
				break
		MM.append(M)

	MM=[list(i) for i in zip(*MM)]
	for i in range(len(MM)):
		K2400.log_save( ''.join(MM[i]) )


	K2400.file_footer(ser[1], ser[0])
	return 0


if __name__ == '__main__':

	FName     = K2400.PATH_DATA+K2400.FILE_NAME
	VDS_start = 0
	VDS_stop  = 100
	VDS_step  = 2

	VGS_start = 0
	VGS_stop  = 100
	VGS_step  = 10

	VDS_comp  = 0.01
	VGS_comp  = 0.01
	NPLC      = 0.1
	DEL       = 0
	SWEEP	  = True

	sa,sb=K2400.init()
	output_param =  [FName, VDS_start, VDS_stop, VDS_step, VDS_comp, VGS_start, VGS_stop, VGS_step, VGS_comp, NPLC, DEL, SWEEP]
	output_steps(sa,sb,*output_param)

