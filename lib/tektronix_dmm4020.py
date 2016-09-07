import serial

class tektronix_dmm4020():
    def __init__(self,dev):
        self.serial = serial.Serial(dev)
        self.serial.setTimeout(2)

    def transaction(self,data):
        (err,reason,ret) = (0,0,None)
        # Read old data
        while self.serial.inWaiting():
            self.serial.readline()
        self.serial.write(data+"\n")
        # Read the response
        ret = self.serial.readline()
        # Read the prompt
        prompt = self.serial.readline()
        if prompt == '?>':
            err = '1'
            reason = 'Command error detected'
        elif prompt == '!>':
            err = '2'
            reason = 'Execution error or device-dependent error detected'
        return (err,reason,ret)

    def write(self,data):
        nbytes = self.serial.write(data+"\n")
        return (0,nbytes)

    def get_idn(self):
        msg = "*IDN?"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return result.strip()        

    def cls(self):
        msg = "*CLS"
        self.write(msg)

    def rst(self):
        msg = "*RST"
        self.write(msg)

    def get_stb(self):
        msg = "*STB?"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return result.strip()

    def get_auto_range_enabled(self):
        msg = "AUTO?"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return result.strip()        

    def set_auto_range(self):
        msg = "AUTO"
        self.write(msg)

    def set_fixed_range(self,volts=None):
        voltage_range=[0,0.200,2,20,200,1000]
        msg = "FIXED"
        self.write(msg)

        if volts and volts <= 1000:
            for idx in range(len(voltage_range)):
                if voltage_range[idx] >= volts:
                    break
            msg = "RANGE %d" % idx
            self.write(msg)

    STB = property(get_stb)

    def set_rate(self,speed):
        if speed == "fast":
            msg = "RATE F"
        elif speed == "medium":
            msg = "RATE M"
        elif speed == "slow":
            msg = "RATE S"
        else:
            return
        self.write(msg)

    def measure(self):
        msg = "MEAS?"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return float(result.strip().split(' ')[0])

    def rwls(self):
        msg = "RWLS"
        self.write(msg)

    def trigger(self):
        msg = "*TRG"
        

dmm = tektronix_dmm4020("/dev/ttyUSB0")
