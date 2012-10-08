import serial
import time
import numpy as np
import sys
from scipy.interpolate import *

class PhotoSensor:    
    def __init__(self):
        self.ser = serial.Serial('/dev/tty.usbmodem411',timeout=1.0/100)
        self.ambient=0;
        self.readings=[]
        self.values=[]
        self.lastreading=None

        readings=np.array([
                [0,1.,0,0], #0
                [0,1.,0.5,0],
                [0,1.,1.,0], #45
                [0,0.5,1.,0],
                [0,0,1.,0], #90
                [0.5,0,1,0],
                [1.,0,1.,0], #135
                [1.,0,0.5,0],
                [1.,0,0,0], #180
                [1.,0,0,0.5],
                [1.,0,0,1.], #225
                [0.5,0,0,1.],
                [0,0,0,1.], #270
                [0,0.5,0,1.],
                [0,1.,0,1.], #315                
                [0,1.,0,0.5]
                ])
        for i,r in enumerate(readings):
            readings[i,:] = r/np.linalg.norm(r)

        values=np.array([0,22.5,45,77.5,90,112.5,135,157.5,
                         180,202.5,225,247.5,270,292.5,315,337.5])
        
        #print readings
        self.li =  NearestNDInterpolator(readings,values)
        
    def calibrate_ambient(self):
        raw_input("Press enter to get an ambient reading")
        for i in xrange(100):
            self.getSensorReading(); #discard this reading

        self.ambient = self.getSensorReading();
        print "Ambient: " + str(self.ambient)
        sys.stdout.write('\a')

    def calibrate(self):
        raw_input("Press enter to get an ambient reading")
        for i in xrange(100):
            self.getSensorReading(); #discard this reading
        self.ambient = self.getSensorReading();
        print "Ambient: " + str(self.ambient)
        sys.stdout.write('\a')
        self.lastreading=self.ambient.copy()

        for i in [0,45,90,135,180,225,270,315]:
            raw_input("Place the light at "+str(i)+" and press enter")
            for j in xrange(100):
                self.getSensorReading(); #discard this reading
            sreading = self.getSensorReading();
            print "last =" + str(self.lastreading)

            while np.linalg.norm(sreading-self.lastreading) < 200.0:
                sreading = self.getSensorReading();                
                #print np.linalg.norm(sreading-self.lastreading)

            self.lastreading = sreading.copy()
            
            sreading-=self.ambient #subtract the ambient and normalized
            print "at " + str(i)+": " + str(sreading)
            self.readings+=[sreading/np.linalg.norm(sreading)]
            self.values +=[i]
            print "at " + str(i)+": " + str(self.readings[-1])

            sys.stdout.write('\a')

        self.li =  NearestNDInterpolator(np.array(self.readings),
                                         np.array(self.values))
            
    def getSensorReading(self):
        reading = None
        while(reading is None):
            lines = self.ser.read(128).split('\n');
        
            if (len(lines) > 3):
                reading = lines[-2].split(" ")
                reading = np.array([int(r) for r in reading ])
        return reading


    def getAngle(self,reading):
        r = reading - self.ambient
        if(np.linalg.norm(r) < 50):
            return np.nan
        r = r / np.linalg.norm(r)
        #print r
        return -self.li(r.reshape([1,4]))

def main():
    sensor = PhotoSensor()
    sensor.calibrate_ambient()

    while(True):
        r = sensor.getSensorReading()
        print sensor.getAngle(r)


if __name__ == '__main__':
    main()
