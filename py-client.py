# Python 2.7
from classes.drone import Drone
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal

def main():
    try:
        ipDrone = '127.0.0.1:14550'
        ipSocket = 'http://192.168.100.189'
        portSocket = 4001

        droneTest = Drone()
        droneTest.connect(ipDrone, ipSocket, portSocket)
        # define WP
        targetlocation=LocationGlobalRelative(35.820344, 139.588850, 20)
        targetlocation2=LocationGlobalRelative(35.820088, 139.589331, 20)
        targetlocation3=LocationGlobalRelative(35.819371, 139.588671, 20)
        targetlocation4=LocationGlobalRelative(35.819651, 139.588237, 20)
        targetlocation5=LocationGlobalRelative(35.82004085, 139.58855534, 20)
        # start the movement
        droneTest.goto(targetlocation)
        droneTest.goto(targetlocation2)
        droneTest.goto(targetlocation3)
        droneTest.goto(targetlocation4)
        droneTest.goto(targetlocation5)

        # mission done, land the drone
        droneTest.delete()
        del droneTest


    except KeyboardInterrupt:
        droneTest.delete()
        del droneTest
        print("KeyboardInterrupt has been caught.")



if __name__ == '__main__':
    main()

 
