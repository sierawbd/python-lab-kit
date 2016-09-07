# Author: Brian Sierawski (brian.sierawski@vanderbilt.edu)

from usbtmc import *

class channel(object):
    def __init__(self,supply,channel_number):
        self.supply = supply
        self.channel_number=channel_number

    def get_enabled(self):
        """Returns the enabled state of the channel."""
        msg=":SOUR:OUTP:STATE?\n"
        (err,reason,result) = self.supply.transaction(msg)
        if err: raise Exception(reason)
        return bool(int(result.strip()))

    def set_enabled(self,enable):
        """Sets the enabled state of the channel."""
        msg = ":SOUR:OUTP:STAT %d\n" % int(bool(enable))
        (err,bytes_sent) = self.supply.write(msg)
        if err: raise Exception(err)

    def get_voltage(self):
        """Returns the output voltage on the channel."""
        msg=":SOUR:VOLT:LEV?"
        (err,reason,result) = self.supply.transaction(msg)
        if err: raise Exception(reason)
        return float(result.strip())

    def set_voltage(self,voltage,current_limit=None):
        """Set the output voltage on the channel."""        
        msg=":SOUR:VOLT:LEV %f" % (voltage)
        (err,bytes_sent) = self.supply.write(msg)
        if err: raise Exception(err)
        if current_limit:
            msg=":SOUR:CURR:LEV %f" % (current_limit)
            (err,bytes_sent) = self.supply.write(msg)
            if err: raise Exception(err)            

    def get_current(self):
        """Returns the output current on the channel."""
        msg=":SOUR:CURR:LEV?"
        (err,reason,result) = self.supply.transaction(msg)
        if err: raise Exception(reason)
        return float(result.strip())

    def measure_current(self):
        """Returns the output current on the channel."""
        msg=":MEAS:CURR:DC?"
        (err,reason,result) = self.supply.transaction(msg)
        if err: raise Exception(reason)
        return float(result.strip())        

    enabled = property(get_enabled, set_enabled)
    voltage = property(get_voltage, set_voltage)
    current = property(measure_current)

class tektronix_pws4205(usbtmc_device):
    def __init__(self,dev):
        usbtmc_device.__init__(self,dev)
        self.ch1 = channel(self,1)

    def set_remote(self):
        msg = "SYST:REM"
        self.write(msg)

    def set_local(self):
        msg = "SYST:LOC"
        self.write(msg)

    def get_idn(self):
        msg = "*IDN?"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return result.strip()

    def get_serial(self):
        (manufacturer,product,serialNumber,version) = (self.get_idn()).split(',')
        return serialNumber.strip()

    def get_status(self):
        msg = "*STB?"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return int(result.strip())

    STB = property(get_status)

    def get_error(self):
        msg = ":SYST:ERR?"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return result.strip()

    def clear(self):
        msg = "*CLS"
        self.write(msg)

    def get_ocr(self):
        msg = "STAT:OPER:COND?"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return int(result.strip())

    def get_mode(self):
        o=self.get_ocr()
        if o & 8: return "CC"
        if o & 4: return "CV"
        else: return None

    OCR = property(get_ocr)

