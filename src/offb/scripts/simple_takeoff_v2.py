#!/usr/bin/env python

import rospy
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode
from mavros_msgs.msg import State
from geometry_msgs.msg import PoseStamped
import time

#global variables
latitude = 0.0
longitude = 0.0
altitude = 0.0

def set_arm():
    print("\n----------set_arm----------")
    rospy.wait_for_service("/mavros/cmd/arming")
    try:
        arm_service = rospy.ServiceProxy("/mavros/cmd/arming", CommandBool)
        resp = arm_service(value=True)
        print "set_arm success: %s" % resp.success
    except rospy.ServiceException, e:
        print "Service arm call failed: %s" % e


def set_disarm():
    print("\n----------set_disarm----------")
    rospy.wait_for_service("/mavros/cmd/arming")
    try:
        arm_service = rospy.ServiceProxy("/mavros/cmd/arming", CommandBool)
        resp = arm_service(value=False)
        print "set_disarm success: %s" % resp.success
    except rospy.ServiceException, e:
        print "Service disarm call failed: %s" % e


def set_takeoff(lat=0, long=0, alt=2):
    print("\n----------set_takeoff----------")
    rospy.wait_for_service("/mavros/cmd/takeoff")
    try:
        takeoff_service = rospy.ServiceProxy("/mavros/cmd/takeoff", CommandTOL)
        resp = takeoff_service(min_pitch = 0, yaw = 0, latitude = lat, longitude = long, altitude = alt)
        print "takeoff success: %s" % resp.success
    except rospy.ServiceException, e:
        print "Service takeoff call failed: %s" % e


def set_land(lat=0, long=0, alt=0):
    print("\n----------set_land----------")
    rospy.wait_for_service("/mavros/cmd/land")
    try:
        land_service = rospy.ServiceProxy("/mavros/cmd/land", CommandTOL)
        resp = land_service(min_pitch = 0, yaw = 0, latitude = lat, longitude = long, altitude = alt)
        print "land success: %s" % resp.success
    except rospy.ServiceException, e:
        print "Service land call failed: %s" % e


def switch_mode(mode):
    print("\n----------switch_mode----------")
    rospy.wait_for_service("/mavros/set_mode")
    try:
        set_mode_service = rospy.ServiceProxy("/mavros/set_mode", SetMode)
        resp = set_mode_service(custom_mode=mode)
        print "switch_mode success: %s" % resp
    except rospy.ServiceException, e:
        print "Service set_mode call failed: %s" % e



current_state = State()
def state_cb(state):
    global current_state
    current_state = state


pose = PoseStamped()
pose.pose.position.x = 0
pose.pose.position.y = 0
pose.pose.position.z = 3

def position_control():

    rospy.init_node("simple_takeoff_v2", anonymous=True)
    rate = rospy.Rate(20.0) # 20hz
    local_pos_pub = rospy.Publisher("/mavros/setpoint_position/local", PoseStamped, queue_size=10)
    state_sub = rospy.Subscriber("/mavros/state", State, state_cb)
    prev_state = current_state
    

    # send a few setpoints before starting
    for i in range(100):
        local_pos_pub.publish(pose)
        rate.sleep()
    
    # wait for FCU connection
    while not current_state.connected:
        rate.sleep()

    last_request = rospy.get_rostime()
    while not rospy.is_shutdown():
        now = rospy.get_rostime()
        if current_state.mode != "OFFBOARD" and (now - last_request > rospy.Duration(5.)):
            switch_mode("OFFBOARD")
            last_request = now 
        else:
            if not current_state.armed and (now - last_request > rospy.Duration(5.)):
               set_arm()
               last_request = now 

        # older versions of PX4 always return success==True, so better to check Status instead
        if prev_state.armed != current_state.armed:
            rospy.loginfo("Vehicle armed: %r" % current_state.armed)
        if prev_state.mode != current_state.mode: 
            rospy.loginfo("Current mode: %s" % current_state.mode)
        prev_state = current_state

        # Update timestamp and publish pose 
        pose.header.stamp = rospy.Time.now()
        local_pos_pub.publish(pose)
        rate.sleep()

if __name__ == '__main__':
    try:
        position_control()
    except rospy.ROSInterruptException:
        pass