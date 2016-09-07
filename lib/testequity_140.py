# Author: Brian Sierawski (brian.sierawski@vanderbilt.edu)

import struct, minimalmodbus

class testequity_140():
    def __init__(self,dev,address=1):
        self.instrument = minimalmodbus.Instrument(dev,address)
        self.instrument.serial.baudrate = 9600

    def get_temperature(self):
        x = self.instrument.read_register(100)
        return minimalmodbus._fromTwosComplement(x)/10.0

    def get_setpoint(self):
        x = self.instrument.read_register(300)
        return minimalmodbus._fromTwosComplement(x)/10.0

    def set_temperature(self,T):
        x = minimalmodbus._twosComplement(int(T*10))
        self.instrument.write_register(300,x)

temp = testequity_140("/dev/ttyUSB1")
