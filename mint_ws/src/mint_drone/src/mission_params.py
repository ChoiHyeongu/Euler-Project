#!/usr/bin/env python
# ROS python API
import rospy
import readchar

# 3D point & Stamped Pose msgs
from geometry_msgs.msg import Point, PoseStamped
# import all mavros messages and services
from mavros_msgs.msg import *
from mavros_msgs.srv import *

# Flight modes class
# Flight modes are activated using ROS services
class fcuModes:
    def __init__(self):
        pass

    def setTakeoff(self):
    	rospy.wait_for_service('mavros/cmd/takeoff')
    	try:
    		takeoffService = rospy.ServiceProxy('mavros/cmd/takeoff', mavros_msgs.srv.CommandTOL)
    		takeoffService(altitude = 3)
    	except rospy.ServiceException, e:
    		print "Service takeoff call failed: %s"%e

    def setArm(self):
        rospy.wait_for_service('mavros/cmd/arming')
        try:
            armService = rospy.ServiceProxy('mavros/cmd/arming', mavros_msgs.srv.CommandBool)
            armService(True)
        except rospy.ServiceException, e:
            print "Service arming call failed: %s"%e

    def setDisarm(self):
        rospy.wait_for_service('mavros/cmd/arming')
        try:
            armService = rospy.ServiceProxy('mavros/cmd/arming', mavros_msgs.srv.CommandBool)
            armService(False)
        except rospy.ServiceException, e:
            print "Service disarming call failed: %s"%e

    def setStabilizedMode(self):
        rospy.wait_for_service('mavros/set_mode')
        try:
            flightModeService = rospy.ServiceProxy('mavros/set_mode', mavros_msgs.srv.SetMode)
            flightModeService(custom_mode='STABILIZED')
        except rospy.ServiceException, e:
            print "service set_mode call failed: %s. Stabilized Mode could not be set."%e

    def setOffboardMode(self):
        rospy.wait_for_service('mavros/set_mode')
        try:
            flightModeService = rospy.ServiceProxy('mavros/set_mode', mavros_msgs.srv.SetMode)
            flightModeService(custom_mode='OFFBOARD')
        except rospy.ServiceException, e:
            print "service set_mode call failed: %s. Offboard Mode could not be set."%e

    def setAltitudeMode(self):
        rospy.wait_for_service('mavros/set_mode')
        try:
            flightModeService = rospy.ServiceProxy('mavros/set_mode', mavros_msgs.srv.SetMode)
            flightModeService(custom_mode='ALTCTL')
        except rospy.ServiceException, e:
            print "service set_mode call failed: %s. Altitude Mode could not be set."%e

    def setPositionMode(self):
        rospy.wait_for_service('mavros/set_mode')
        try:
            flightModeService = rospy.ServiceProxy('mavros/set_mode', mavros_msgs.srv.SetMode)
            flightModeService(custom_mode='POSCTL')
        except rospy.ServiceException, e:
            print "service set_mode call failed: %s. Position Mode could not be set."%e

    def setAutoLandMode(self):
        rospy.wait_for_service('mavros/set_mode')
        try:
            flightModeService = rospy.ServiceProxy('mavros/set_mode', mavros_msgs.srv.SetMode)
            flightModeService(custom_mode='AUTO.LAND')
        except rospy.ServiceException, e:
               print "service set_mode call failed: %s. Autoland Mode could not be set."%e

class Controller:
    # initialization method
    def __init__(self):
        # Drone state
        self.state = State()
        # Instantiate a setpoints message
        self.sp = PositionTarget()
        # set the flag to use position setpoints and yaw angle
        self.sp.type_mask = int('010111111000', 2)
        # LOCAL_NED
        self.sp.coordinate_frame = 1

        # We will fly at a fixed altitude for now
        # Altitude setpoint, [meters]
        self.ALT_SP = 3.0
        # update the setpoint message with the required altitude
        self.sp.position.z = self.ALT_SP
        # Step size for position update
        self.STEP_SIZE = 2.0
		# Fence. We will assume a square fence for now
        self.FENCE_LIMIT = 5.0

        # A Message for the current local position of the drone
        self.local_pos = Point(0.0, 0.0, 3.0)

        # initial values for setpoints
        self.sp.position.x = 0.0
        self.sp.position.y = 0.0

        # speed of the drone is set using MPC_XY_CRUISE parameter in MAVLink
        # using QGroundControl. By default it is 5 m/s.

        self.position = Position()

	# Callbacks

    ## local position callback
    def posCb(self, msg):
        self.local_pos.x = msg.pose.position.x
        self.local_pos.y = msg.pose.position.y
        self.local_pos.z = msg.pose.position.z

    ## Drone State callback
    def stateCb(self, msg):
        self.state = msg

    ## Update setpoint message
    def updateSp(self):
        self.sp.position.x = self.local_pos.x
        self.sp.position.y = self.local_pos.y
        self.sp.position.z = self.local_pos.z

    def x_dir(self):
    	self.sp.position.x = self.local_pos.x + 3
    	self.sp.position.y = self.local_pos.y
        self.sp.position.z = self.local_pos.z

    def neg_x_dir(self):
    	self.sp.position.x = self.local_pos.x - 3
    	self.sp.position.y = self.local_pos.y
        self.sp.position.z = self.local_pos.z

    def y_dir(self):
    	self.sp.position.x = self.local_pos.x
    	self.sp.position.y = self.local_pos.y + 3
        self.sp.position.z = self.local_pos.z

    def neg_y_dir(self):
    	self.sp.position.x = self.local_pos.x
    	self.sp.position.y = self.local_pos.y - 3
        self.sp.position.z = self.local_pos.z

    def z_dir(self):
        self.sp.position.x = self.local_pos.x
    	self.sp.position.y = self.local_pos.y
        self.sp.position.z = self.local_pos.z + 3
    
    def neg_z_dir(self):
        self.sp.position.x = self.local_pos.x
    	self.sp.position.y = self.local_pos.y
        self.sp.position.z = self.local_pos.z - 3

    def move(self, waypoint):
        # while self.sp.position.x != waypoint.x:
        #     if self.sp.position.x > waypoint.x:
        #         print("Neg_x_dir")
        #         self.neg_x_dir()
        #     else:
        #         print("x_dir")
        #         self.x_dir()
        #     self.position.updatePosition(self.sp)

        # while self.sp.position.y != waypoint.y:
        #     if self.sp.position.y > waypoint.y:
        #         print("Neg_y_dir")
        #         self.neg_y_dir()
        #     else:
        #         print("y_dir")
        #         self.y_dir()
        #     self.position.updatePosition(self.sp)

        # while self.sp.position.z < waypoint.z:
        #     if self.sp.position.z > waypoint.z:
        #         print("Neg_z_dir")
        #         self.neg_z_dir()
        #     else:
        #         print("z_dir")
        #         self.z_dir()
        #     self.position.updatePosition(self.sp)
        
        if self.sp.position.z < waypoint.z:
            print("true")
            while self.sp.position.z <= waypoint.z:
                print(waypoint.z)
                self.position.updatePosition(self.sp)
                self.z_dir()
        else:
            print("false")
            while self.sp.position.z > waypoint.z:
                self.position.updatePosition(self.sp)
                self.neg_z_dir()

        if self.sp.position.y < waypoint.y:
            print("true")
            while self.sp.position.y <= waypoint.y:
                self.position.updatePosition(self.sp)
                self.y_dir()
        else:
            print("false")
            while self.sp.position.y > waypoint.y:
                self.position.updatePosition(self.sp)
                self.neg_y_dir()

        if self.sp.position.x < waypoint.x:
            print("true")
            while self.sp.position.x <= waypoint.x:
                self.position.updatePosition(self.sp)
                self.x_dir()
        else:
            print("false")
            while self.sp.position.x > waypoint.x:
                self.position.updatePosition(self.sp)
                self.neg_x_dir()

class Waypoint:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Position:
    def __init__(self):
        # Setpoint publisher    
        self.sp_pub = rospy.Publisher('mavros/setpoint_raw/local', PositionTarget, queue_size=1)
        # ROS loop rate
        self.rate = rospy.Rate(20.0)

    def updatePosition(self, sp):
        self.sp_pub.publish(sp)
        self.rate.sleep()
        # Setpoint publisher    
        sp_pub = rospy.Publisher('mavros/setpoint_raw/local', PositionTarget, queue_size=1)
        # ROS loop rate
        rate = rospy.Rate(20.0)

    def sleep(self):
        self.rate.sleep

# Main function
def main():

    # initiate node
    rospy.init_node('setpoint_node', anonymous=True)

    # flight mode object
    modes = fcuModes()

    # controller object
    cnt = Controller()

    position = Position()

    # Subscribe to drone state
    rospy.Subscriber('mavros/state', State, cnt.stateCb)

    # Subscribe to drone's local position
    rospy.Subscriber('mavros/local_position/pose', PoseStamped, cnt.posCb)

    # Make sure the drone is armed
    while not cnt.state.armed:
        modes.setArm()
        position.sleep()

    # set in takeoff mode and takeoff to default altitude (3 m)
    # modes.setTakeoff()
    # rate.sleep()

    # We need to send few setpoint messages, then activate OFFBOARD mode, to take effect
    k=0
    while k<10:
        position.updatePosition(cnt.sp)
        k = k + 1

    # activate OFFBOARD mode
    modes.setOffboardMode()

    # ROS main loop

    waypoint1 = Waypoint(0, 0, 8)
    waypoint2 = Waypoint(0, 13, 8)
    waypoint3 = Waypoint(13, 13, 8)
    waypoint4 = Waypoint(13, 0, 8)
    waypoint5 = Waypoint(0, 0, 0)


    progress = [True, True, True, True, True, True]
    missoin = [waypoint1, waypoint2, waypoint3, waypoint4, waypoint5]
    while :
        for waypoint in missoin:
            print("Mission start")
            cnt.move(waypoint)
            

if __name__ == '__main__':
	try:
		main()
	except rospy.ROSInterruptException:
		pass
