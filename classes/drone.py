# Python 2.7
import threading
from socketIO_client_nexus import SocketIO, LoggingNamespace, ConnectionError
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal
import json
import time
import math
from classes.interval import Interval

class Drone(object):

    """
    Class to define a drone object.
    """

    def __init__(self):
        """__init__ method fro the Drone class.

        The __init__ method will set all the attribute to their default values.

        Args:
            param1 (str): Description of `param1`.
            param2 (:obj:`int`, optional): Description of `param2`. Multiple
                lines are supported.
            param3 (list(str)): Description of `param3`.

        """

        self.__intervals = {}
        self.__g_id_counter = 0
        self.__interval = None
        self.__vehicle = None
        self.__socketIO = None
        self.__currentLocation = None
        

    def connect(self, droneIP, socketIP, socketPort):
        self.__vehicle = connect(droneIP, wait_ready=True)
        self.__arm_and_takeoff(10)
        self.__vehicle.groundspeed = 5
        self.__currentLocation = self.__vehicle.location.global_relative_frame
        # connect to the web API
        self.__socketIO = SocketIO(socketIP, socketPort, LoggingNamespace) 
        self.__socketIO.on("on_aaa_response", self.__on_aaa_response)
        self.__socketIO.wait(2)
    
    def delete(self):
        #self.clear_interval(self.interval)
        self.__vehicle.mode = VehicleMode("LAND") 
        self.__vehicle.close()

    def __clear_interval(self, interval_id):
        # terminate this interval's while loop
        self.__intervals[interval_id].daemon_alive = False
        # kill the thread
        self.__intervals[interval_id].thread.join()
        # pop out the interval from registry for reusing
        self.__intervals.pop(interval_id)
        print("thread killed")
    
    def __set_interval(self, interval, func):
        interval_obj = Interval()
        # Put this interval on a new thread
        t = threading.Thread(target=interval_obj.ticktock, args=(interval, func))
        t.setDaemon(True)
        interval_obj.thread = t
        t.start()

        # Register this interval so that we can clear it later
        # using roughly generated id
        interval_id = self.__g_id_counter
        self.__g_id_counter += 1
        self.__intervals[interval_id] = interval_obj

        # return interval id like it does in JavaScript
        return interval_id

    def __emitPosition(self):
        x = {
            "type": "marker",
            "coordinates": [
                self.__vehicle.location.global_relative_frame.lon,
                self.__vehicle.location.global_relative_frame.lat

             ],
            "properties": {
                "id": str(time.time())
            }
        }
        # convert into JSON:
        y = json.dumps(x)
        self.__socketIO.emit("fromPy", y)

    def __on_aaa_response(self, *args):
        if(args[0] == True):
            print("connected")
            # need to set a variable to start the thread
            self.__interval = self.__set_interval(1, self.__emitPosition)
        else :
            print("not connected")
    
    def __arm_and_takeoff(self, aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """

        print "Basic pre-arm checks"
        # Don't try to arm until autopilot is ready
        while not self.__vehicle.is_armable:
            print " Waiting for vehicle to initialise..."
            time.sleep(1)

        print "Arming motors"
        # Copter should arm in GUIDED mode
        self.__vehicle.mode    = VehicleMode("GUIDED")
        self.__vehicle.armed   = True

        # Confirm vehicle armed before attempting to take off
        while not self.__vehicle.armed:
            print " Waiting for arming..."
            time.sleep(1)

        print "Taking off!"
        self.__vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
            print " Altitude: ", self.__vehicle.location.global_relative_frame.alt
            #Break and return from function just below target altitude.
            if self.__vehicle.location.global_relative_frame.alt >= aTargetAltitude*0.95:
                print "Reached target altitude"
                break
            time.sleep(1)


    def setSpeed(self, speed):
        self.__vehicle.groundspeed = speed


    def __get_distance_metres(self, aLocation1, aLocation2):
        """
        Returns the ground distance in metres between two LocationGlobal objects.

        This method is an approximation, and will not be accurate over large distances and close to the 
        earth's poles. It comes from the ArduPilot test code: 
        https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
        """
        dlat = aLocation2.lat - aLocation1.lat
        dlong = aLocation2.lon - aLocation1.lon
        return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

    def goto(self, targetLocation):
        """
        Moves the vehicle to a position dNorth metres North and dEast metres East of the current position.
        The method takes a function pointer argument with a single `dronekit.lib.LocationGlobal` parameter for 
        the target position. This allows it to be called with different position-setting commands. 
        By default it uses the standard method: dronekit.lib.Vehicle.simple_goto().
        The method reports the distance to target every two seconds.

        Args:
               
               param1 (type): describe
               param2 (type): describe
        
        Returns:
               returnParam (type) : describe

        """
        
        self.__currentLocation = self.__vehicle.location.global_relative_frame
        
        targetDistance = self.__get_distance_metres(self.__currentLocation, targetLocation)
        print(targetDistance)
        self.__vehicle.simple_goto(targetLocation)
        

        while self.__vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
            #print "DEBUG: mode: %s" % vehicle.mode.name
            remainingDistance=self.__get_distance_metres(self.__vehicle.location.global_relative_frame, targetLocation)
            print "Distance to target: ", remainingDistance
            if remainingDistance<=targetDistance*0.01: #Just below target, in case of undershoot.
                print "Reached target"
                break
            time.sleep(2)



