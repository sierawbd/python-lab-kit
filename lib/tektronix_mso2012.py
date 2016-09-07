# Author: Brian Sierawski (brian.sierawski@vanderbilt.edu)

from usbtmc import *
import array

class channel(object):
    def __init__(self,scope,channel_number):
        self.scope = scope
        self.channel_number = channel_number
        self.local_dict = dict( {'source': 'CH%d'%(channel_number)} )

    def get_cmd(self,cmd):
        (err,reason,result) = self.scope.transaction(cmd % self.local_dict)
        if err: raise Exception(reason)
        return result.strip()

    def set_cmd(self,cmd,x):
        (err,nbytes) = self.scope.write((cmd % self.local_dict) + " " + str(x))
        if err: raise Exception(reason)
        return

    """Turns on or off the specified channel or returns whether the channel is on or off"""
    select = property(
        lambda self: bool(int(self.get_cmd(":SELECT:%(source)s?"))),
        lambda self, x: self.set_cmd(":SELECT:%(source)s", int(x)))
    invert = property(
        lambda self: bool(int(self.get_cmd(":%(source)s:INVERT?"))),
        lambda self, x: self.set_cmd(":%(source)s:INVERT", int(x)))
    label = property(
        lambda self: str(self.get_cmd(":%(source)s:LABEL?")),
        lambda self, x: self.set_cmd(":%(source)s:LABEL", '"'+x+'"'))
    scale = property(
        lambda self: float(self.get_cmd(":%(source)s:SCALE?")),
        lambda self, x: self.set_cmd(":%(source)s:SCALE", float(x)))
    position = property(
        lambda self: float(self.get__cmd(":%(source)s:POSITION?")),
        lambda self, x: self.set_cmd(":%(source)s:POSITION", float(x)))
    probe_id = property(
        lambda self: float(self.get_cmd(":%(source)s:PROBE:ID?")))
    probe_gain = property(
        lambda self: float(self.get_cmd(":%(source)s:PROBE:GAIN?")))
    probe_resistance = property(
        lambda self: float(self.get_cmd(":%(source)s:PROBE:RESISTANCE?")))

class tektronix_mso2012(usbtmc_device):
    def __init__(self,dev):
        usbtmc_device.__init__(self,dev)
        self.ch1 = channel(self,1)
        self.ch2 = channel(self,2)

    def get_cmd(self,cmd):
        (err,reason,result) = self.transaction(cmd)
        if err: raise Exception(reason)
        return result.strip()

    def set_cmd(self,cmd,x):
        (err,nbytes) = self.write((cmd) + " " + str(x))
        if err: raise Exception(reason)
        return

    idn = property(
        lambda self: self.get_cmd("*IDN?"))
    stb = property(
        lambda self: int(self.get_cmd("*STB?")))

    def get_serial(self):
        (manufacturer,product,serialNumber,version) = (self.idn).split(',')
        return serialNumber.strip()

    def clear(self):
        msg = "*CLS";
        (err,reason) = self.write(msg)
        if err: raise Exception(reason)

    def message(self,s=None):
        if(s):
            msg = 'MESSAGE:SHOW "%s"; STATE 1' % s;
            (err,reason) = self.write(msg)
            if err: raise Exception(reason)
        else:
            msg = 'MESSAGE:STATE 0';
            (err,reason) = self.write(msg)
            if err: raise Exception(reason)

    def get_error(self):
        msg = ":SYST:ERR?"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return result.strip()

    def get_horizontal_record_length(self):
        msg = ":HOR:ACQLENGTH?\n"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return int(float(result.strip()))

    def get_record_length(self,source,reduced=0):
        msg = ":DAT:SOU %s\n" % (source)
        (err,nbytes) = self.write(msg)
        if err: raise Exception(reason)

        if reduced:
            msg = ":DAT:RESO REDU\n"
            (err,nbytes) = self.write(msg)
            if err: raise Exception(reason)
        else:
            msg = ":DAT:RESO FULL\n"
            (err,nbytes) = self.write(msg)
            if err: raise Exception(reason)

        msg = ":WFMOutpre:RECOrdlength?\n"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return int(float(result.strip()))

    def get_waveform_id(self,source):
        msg = ":DAT:SOU %s\n" % (source)
        (err,nbytes) = self.write(msg)
        if err: raise Exception(reason)
        msg = ":WFMOutpre:WFId?\n"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return result.strip()

    def get_waveform_xincr(self,source):
        msg = ":DAT:SOU %s\n" % (source)
        (err,nbytes) = self.write(msg)
        if err: raise Exception(reason)
        msg = ":WFMOutpre:XINcr?\n"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return float(result.strip())

    def get_waveform_xunit(self,source):
        msg = ":DAT:SOU %s\n" % (source)
        (err,nbytes) = self.write(msg)
        if err: raise Exception(reason)
        msg = ":WFMOutpre:XUNit?\n"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return result.strip()

    def get_waveform_yunit(self,source):
        msg = ":DAT:SOU %s\n" % (source)
        (err,nbytes) = self.write(msg)
        if err: raise Exception(reason)
        msg = ":WFMOutpre:YUNit?\n"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return result.strip()

    def get_waveform_ymult(self,source):
        msg = ":DAT:SOU %s\n" % (source)
        (err,nbytes) = self.write(msg)
        if err: raise Exception(reason)
        msg = ":WFMOutpre:YMUlt?\n"
        (err,reason,result) = self.transaction(msg)
        if err: raise Exception(reason)
        return float(result.strip())

    def get_waveform(self,source='CH1',width=1,reduced=1,outfile=None):
        if width == 1: retformat = 'b'
        elif width == 2: retformat = 'h'
        # Select the data source
        msg = ":DATA:SOURCE %s\n" % (source)
        (err,nbytes) = self.write(msg)
        if err: raise Exception(reason)

        # Select the data encoding
        msg = ":DAT:ENC RIB\n"
        (err,nbytes) = self.write(msg)
        if err: raise Exception(reason)
        msg = ":WFMOutpre:BYT_Nr %d\n" % (width)
        (err,nbytes) = self.write(msg)
        if err: raise Exception(reason)

        if reduced:
            msg = ":DAT:RESO REDU\n"
            (err,nbytes) = self.write(msg)
            if err: raise Exception(reason)
        else:
            msg = ":DAT:RESO FULL\n"
            (err,nbytes) = self.write(msg)
            if err: raise Exception(reason)

        rec_length = self.get_record_length(source,reduced)
        ymult = self.get_waveform_ymult(source)
        ydata = []
        xincr = self.get_waveform_xincr(source)
        xdata = [xincr * x for x in range(rec_length)]

        for i in range(0,rec_length,1000):
            # Set the data domain
            start = i
            stop = min(i+1000,rec_length)
            points = stop - start
            msg = ":DAT:START %d; :DAT:STOP %d\n" % (start,stop)
            (err,nbytes) = self.write(msg)
            if err: raise Exception(reason)

            # Get the data
            msg = ":CURVE?\n"
            (err,reason,result) = self.transaction(msg)
            if err: raise Exception(reason)
            preamble = result[:-width*points]
            a = array.array(retformat,result[-width*points:])
            lst = [ymult * x for x in a]
            ydata.extend(lst)

        if outfile:
            f=open(outfile,'w')
            for i in range(len(xdata)):
                print >>f, xdata[i], ydata[i]
            f.close()

        return (xdata,ydata)

