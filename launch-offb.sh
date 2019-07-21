#!/bin/bash

source ./launch-common.sh
echo $1
roslaunch offb offb.launch vehicle:=$1
