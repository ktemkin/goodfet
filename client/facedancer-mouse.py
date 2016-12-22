#!/usr/bin/env python3
#
# facedancer-keyboard.py

from Facedancer import *
from MAXUSBApp import *
from USBMouse import *

if os.environ.get('GOODFET') == "spi":
    from Raspdancer import *
    fd = Raspdancer(verbose=1)
else:
    sp = GoodFETSerialPort()
    fd = Facedancer(sp, verbose=1)

u = MAXUSBApp(fd, verbose=1)

d = USBMouseDevice(u, verbose=4)

d.connect()

try:
    d.run()
# SIGINT raises KeyboardInterrupt
except KeyboardInterrupt:
    d.disconnect()
