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
        # goto Test
        targetlocation=LocationGlobal(35.820088, 139.589331, 10)
        droneTest.goto(targetlocation)

    except KeyboardInterrupt:
        droneTest.delete()
        del droneTest
        print("KeyboardInterrupt has been caught.")



if __name__ == '__main__':
    main()

 
