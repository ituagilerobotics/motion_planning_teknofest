#!/bin/bash

px4_dir=~/src/Firmware
cd $px4_dir
#DONT_RUN=1 make px4_sitl gazebo_solo
source ~/Desktop/motion_planning_teknofest/devel/setup.bash
source $(pwd)/Tools/setup_gazebo.bash $(pwd) $(pwd)/build/px4_sitl_default
export ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH:$(pwd)
export ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH:$(pwd)/Tools/sitl_gazebo
