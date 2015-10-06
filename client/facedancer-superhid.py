#!/usr/bin/env python3
#
# facedancer-tablet.py

from Facedancer import *
from MAXUSBApp import *
from USBSuperHID import *

sp = GoodFETSerialPort()
fd = Facedancer(sp, verbose=1)
u = MAXUSBApp(fd, verbose=1)

d = USBSuperHIDDevice(u, verbose=4)

d.connect()

try:
    d.run()
# SIGINT raises KeyboardInterrupt
except KeyboardInterrupt:
    d.disconnect()
