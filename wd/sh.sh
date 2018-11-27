#!/bin/bash
for i in {1..50}
do
#echo "SHT ON"
#echo "ON" > ./shutter.txt
#sleep 1

#echo "COMMENTS: "$i
#echo $i > ./comments.txt
#sleep 1

echo -e "VGS=$i\nVDS=$i" > ./change.txt
echo -e "VGS=$i\nVDS=$i" > ./change.txt
sleep 1

#echo "SHT OFF"
#echo "OFF" > ./shutter.txt
#sleep 1

done

echo "OFF" > ./switch.txt
