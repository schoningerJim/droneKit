# Python 2.7
import threading
from socketIO_client_nexus import SocketIO, LoggingNamespace, ConnectionError
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal
import json
import time
from classes.interval import Interval

class Drone(object):
    def __init__(self):
        self.intervals = {}
        self.g_id_counter = 0
        self.interval = None
        self.vehicle = None
        self.socketIO = None

    def connect(self, droneIP, socketIP, socketPort):
        self.vehicle = connect(droneIP, wait_ready=True)
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
        x = {
            "type": "marker",
            "coordinates": [
                139.58855534,
                35.82004085

             ],
            "properties": {
                "id": str(time.time())
            }
        }

        # convert into JSON:
        y = json.dumps(x)
        self.socketIO.emit("fromPy", y)

    def on_aaa_response(self, *args):
        if(args[0] == True):
            print("connected")
            # need to set a variable to start the thread
            self.interval = self.set_interval(1, self.emitPosition)
        else :
            print("not connected")


