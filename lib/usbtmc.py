# Author: Brian Sierawski (brian.sierawski@vanderbilt.edu)

import usb.core
import usb.util
import struct
import threading

verbose = False

class usbtmc_device():
    def __init__(self,dev):
        # find our device
        self.dev = dev
        self.bTag = 1
        self.lock = threading.Lock()

        # set the active configuration. With no arguments, the first
        # configuration will be the active one

        if self.dev.is_kernel_driver_active(0):
            print "Kernel driver is active, detaching..."
            self.dev.detach_kernel_driver(0)

        # get an endpoint instance
        self.dev.set_configuration(1)
        cfg = self.dev.get_active_configuration()
        interface_number = cfg[(0,0)].bInterfaceNumber
        #alternate_settting = usb.control.get_interface(dev,interface_number)

        intf = usb.util.find_descriptor(
            cfg, bInterfaceNumber = interface_number,
            bAlternateSetting = 0#alternate_setting
            )

        self.bulk_out = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match = \
                lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT
            )

        self.bulk_in  = usb.util.find_descriptor(
            intf,
            # match the first IN endpoint
            custom_match = \
                lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_IN
            )

    def dev_dep_msg_out(self,msg):
        header = struct.pack("<bbbbIbbbb", 0x01, self.bTag, ~self.bTag, 0x00, len(msg), 0x01, 0x00, 0x00, 0x00)
        align=""
        if len(msg)%4 == 1: align = struct.pack("<bbb",0x00,0x00,0x00)
        elif len(msg)%4 == 2: align = struct.pack("<bb",0x00,0x00)
        elif len(msg)%4 == 3: align = struct.pack("<b",0x00)
        cmd=header+msg+align
        self.bTag = (self.bTag + 1)%128
        nbytes = self.bulk_out.write(cmd)
        return nbytes

    def request_dev_dep_msg_in(self,sz):
        req = struct.pack("<bbbbIbbbb", 0x02, self.bTag, ~self.bTag, 0x00, sz, 0x00, 0x00, 0x00, 0x00)
        self.bTag = (self.bTag + 1)%128
        self.bulk_out.write(req)

        if verbose: print "usbtmc: request_dev_dep_msg_in bTag=%d sz=%d" % (self.bTag,sz)
        bulk_in = self.bulk_in.read(sz)
        (msgid,bTag,bTagInv,Res,TxSize,bmTxAttr) = struct.unpack("<bbbbIb", bulk_in[:9])
        if verbose: print "usbtmc: bulk_in returned msgid=%d bTag=%d TxSize=%d bmTxAttr=%d" % (msgid,bTag,TxSize,bmTxAttr)
        data = bulk_in[12:]
        return data.tostring()

    def write(self,data):
        self.lock.acquire()
        nbytes = self.dev_dep_msg_out(data)
        self.lock.release()
        return (0,nbytes)

    def transaction(self,data):
        (err,reason,ret) = (0,0,None)
        self.lock.acquire()
        self.dev_dep_msg_out(data)
        ret = self.request_dev_dep_msg_in(2**20)
        self.lock.release()
        return (err,reason,ret)

    def info(self):
        print "Device has %d configurations" % self.dev.bNumConfigurations
        for cfg in self.dev:
            print "Configuration %d" % cfg.bConfigurationValue
            print "  Configuration has %d interfaces" % cfg.bNumInterfaces
            for intf in cfg:
                print "    Interface has %d endpoints" % intf.bNumEndpoints
                for ep in intf:
                    print "      Endpoint address %d" % ep.bEndpointAddress
                    print "        Attributes %d" % ep.bmAttributes
                    if ep.bmAttributes == 0: print "        Control Transfer"
                    elif ep.bmAttributes == 1: print "        Isochronous"
                    elif ep.bmAttributes == 2: print "        Bulk"
                    elif ep.bmAttributes == 3: print "        Interrupt"
                    print "        Max Packet Size %d" % (ep.wMaxPacketSize)
                    print "        Interval %d" % (ep.bInterval)
                    if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                        print "        Endpoint out"
                    if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                        print "        Endpoint in"            
