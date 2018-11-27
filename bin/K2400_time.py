#!/usr/bin/python
# -*- coding: utf-8 -*-
import K2400
import logging
import time
from multiprocessing.pool import ThreadPool
from datetime import datetime

#---------------------------------------------------------------------------------------------------------------
#------------------------------------------ Time STEPS
#---------------------------------------------------------------------------------------------------------------
#def time_steps(ser_VDS, ser_VGS, VDS, VDS_comp, VGS, VGS_comp, NPLC=1, DEL=0.01):

def time_steps(ser,*param):

        logging.info("********* TIME_STEPS_START *********")
        start_time = datetime.now()
	ser_VDS  = ser[0]
	ser_VGS  = ser[1]
	ser_PICO = ser[2]

        LogFileName   	= str(param[0])+"_time.txt"
        VDS     	= float(param[1])
        VDS_comp	= float(param[2])
        VGS     	= float(param[3])
        VGS_comp	= float(param[4])
        NPLC    	= float(param[5])
        DEL     	= float(param[6])
	SHUTTER		= param[7]
	sht 		= K2400.sht()
	sht 		= K2400.sht()

	K2400.log_init(LogFileName)

        txt=    "# INIT TIME STEP TEST ..................................................  \n"\
                "# VDS       : " + str(VDS) + " \t Current compliance " + str(VDS_comp) + "\n"\
                "# VGS       : " + str(VGS) + " \t Current compliance " + str(VGS_comp) + "\n"\
                "# NPLC      : " + str(NPLC     ) 					+ "\n"\
                "# DELETE    : " + str(DEL      ) 					+ "\n"\
                "# pozycja poczatkowa szhuttera: " +str(sht) +" keep open "+ str(SHUTTER)+ " before measurmeents\n"\
        	"# :: ----------------------------------- TIME --------------------------------------\n" +\
                "# ::     Time \t IDS \t IGS \t VDS \t VGS \t XPIN \t | Shutter | \t Delta Time	     \n" +\
                "# :: -------------------------------------------------------------------------------"
        #print txt

	K2400.log_save(txt)
	if SHUTTER:
                txt="# :: ---------- SHUTTER open for "+str(SHUTTER)+"sec. before measurements: Shutter status:"+str(K2400.sht())
                K2400.log_save(txt)
		time.sleep(SHUTTER)

        # init measurement
        K2400.set_voltage_init(ser_VDS, 0.1, VDS_comp, NPLC, DEL)
        K2400.set_voltage_init(ser_VGS, 0.1, VGS_comp, NPLC, DEL)


	time_0=-888
        while True:
                if K2400.switch() == "OFF" : break
		sht = K2400.sht()

		change = K2400.change()
		if change[0] == "True":
			if float(change[1]) != -888: VGS = change[1]
			if float(change[2]) != -888: VDS = change[2]
			pool        = ThreadPool(6)
                        resoults    = pool.map(K2400.set_voltage2, [(ser[0],VDS),(ser[1],VGS)])
			pool.close()
		else:
			pool        = ThreadPool(6)
			resoults    = pool.map(K2400.get_TUI, ser)
			VDS_I,VDS_T = resoults[0]
			VGS_I,VGS_T = resoults[1]
			PICO        = resoults[2][0]
			pool.close()

		if time_0 == -888:
			time_0 = float(VDS_T)
			time_1 = float(VGS_T)
                        dto    = -888

		dt=float(VDS_T)-time_0
                txt = str("%.4f" %(dt)) +" "+ str(VDS_I) +" "+ str(VGS_I) +" "+ str(VDS) +" "+ str(VGS) +" "+ str(PICO)  +" | "+str(sht) +" | "+ str("%.4f" %(dt-dto))
                #print txt
	        K2400.log_save(txt)
		dto=dt

        K2400.file_footer(ser_VGS, ser_VDS)
	print "\nDONE ..... \nEXIT!!!\n"
        return 0


if __name__ == '__main__':

	#------- TIME: parametry pomiaru
	FName     =  K2400.PATH_DATA+"qqqqqqq"
	VDS       =  10
	VGS       =  10
	VDS_comp  =  0.01
	VGS_comp  =  0.01
	NPLC      =  1
	DEL       =  0

	param_timesteps = [FName, VDS, VDS_comp, VGS, VGS_comp,  NPLC, DEL]

	sa,sb=K2400.init()
	time_steps(sa,sb,*param_timesteps)
	#print K2400.change()
