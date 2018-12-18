# Python 2.7
import threading
from socketIO_client_nexus import SocketIO, LoggingNamespace, ConnectionError
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal
import json
import time
import math
from classes.interval import Interval

class Drone(object):
    def __init__(self):
        self.intervals = {}
        self.g_id_counter = 0
        self.interval = None
        self.vehicle = None
        self.socketIO = None
        # test square path drone
        self.dronePosLisIdx = 0
        self.dronePosList = []
        self.dronePosList.append({
            "type": "marker",
            "coordinates": [
                139.58855534,
                35.82004085

             ],
            "properties": {
                "id": str(time.time())
            }
        })
        self.dronePosList.append({
            "type": "marker",
            "coordinates": [
                139.588850,
                35.820344

             ],
            "properties": {
                "id": str(time.time())
            }
        })
        self.dronePosList.append({
            "type": "marker",
            "coordinates": [
                139.589331,
                35.820088

             ],
            "properties": {
                "id": str(time.time())
            }
        })
        self.dronePosList.append({
            "type": "marker",
            "coordinates": [
                139.588671,
                35.819371

             ],
            "properties": {
                "id": str(time.time())
            }
        })
        self.dronePosList.append({
            "type": "marker",
            "coordinates": [
                139.588237,
                35.819651

             ],
            "properties": {
                "id": str(time.time())
            }
        })


    def connect(self, droneIP, socketIP, socketPort):
        self.vehicle = connect(droneIP, wait_ready=True)
        self.arm_and_takeoff(10)
        self.socketIO = SocketIO(socketIP, socketPort, LoggingNamespace) 
        self.socketIO.on("on_aaa_response", self.on_aaa_response)
        self.socketIO.wait()
    
    def delete(self):
        #self.clear_interval(self.interval)
        self.vehicle.close()

    def clear_interval(self, interval_id):
        # terminate this interval's while loop
        self.intervals[interval_id].daemon_alive = False
        # kill the thread
        self.intervals[interval_id].thread.join()
        # pop out the interval from registry for reusing
        self.intervals.pop(interval_id)
        print("thread killed")
    
    def set_interval(self, interval, func):
        interval_obj = Interval()
        # Put this interval on a new thread
        t = threading.Thread(target=interval_obj.ticktock, args=(interval, func))
        t.setDaemon(True)
        interval_obj.thread = t
        t.start()

        # Register this interval so that we can clear it later
        # using roughly generated id
        interval_id = self.g_id_counter
        self.g_id_counter += 1
        self.intervals[interval_id] = interval_obj

        # return interval id like it does in JavaScript
        return interval_id

    def emitPosition(self):
        if (self.dronePosLisIdx == 5):
            self.dronePosLisIdx = 0

        x = self.dronePosList[self.dronePosLisIdx]

        # convert into JSON:
        y = json.dumps(x)
        self.socketIO.emit("fromPy", y)
        # we increment the counter for the index
        self.dronePosLisIdx += 1 

    def on_aaa_response(self, *args):
        if(args[0] == True):
            print("connected")
            # need to set a variable to start the thread
            self.interval = self.set_interval(1, self.emitPosition)
        else :
            print("not connected")
    
    def arm_and_takeoff(self, aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """

        print "Basic pre-arm checks"
        # Don't try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            print " Waiting for vehicle to initialise..."
            time.sleep(1)

        print "Arming motors"
        # Copter should arm in GUIDED mode
        self.vehicle.mode    = VehicleMode("GUIDED")
        self.vehicle.armed   = True

        # Confirm vehicle armed before attempting to take off
        while not self.vehicle.armed:
            print " Waiting for arming..."
            time.sleep(1)

        print "Taking off!"
        self.vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
            print " Altitude: ", self.vehicle.location.global_relative_frame.alt
            #Break and return from function just below target altitude.
            if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude*0.95:
                print "Reached target altitude"
                break
            time.sleep(1)


