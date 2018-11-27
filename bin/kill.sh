#!/bin/bash
proc=`pgrep K2400`

if [ $proc  ]
then
echo "KILLING PROCESS:" $proc
kill -9 $proc
else
	echo "Nobody to KILL !!!"
fi
