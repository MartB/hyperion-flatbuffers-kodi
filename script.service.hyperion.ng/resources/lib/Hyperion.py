'''
    Kodi video capturer for Hyperion

	Copyright (c) 2013-2016 Hyperion Team

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in
	all copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
	THE SOFTWARE.
'''
import socket
import struct
import time
import io

# flatbuffers message includes
from hyperionnet.Clear import *
from hyperionnet.Color import *
from hyperionnet.Image import *
from hyperionnet.RawImage import *
from hyperionnet.Register import *
from hyperionnet.Reply import *
from hyperionnet.Request import *

from hyperionnet.Command import Command
from hyperionnet.ImageType import ImageType

from misc import log, notify
class Hyperion(object):
    '''Hyperion connection class
    
    A Hyperion object will connect to the Hyperion server and provide
    easy to use functions to send requests
    
    Note that the function will block until a reply has been received
    from the Hyperion server (or the call has timed out)
    '''
    
    def __init__(self, config):
        self.reconnectTries = 0
        self.connected = False
        self.config = config
       
    def connect(self):
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.__socket.settimeout(2)
            self.__socket.connect((self.config.address, self.config.port))
            self.Register("HyperionKodiAddon v2", 1);

            self.connected = True
            return True
        except socket.error, e:
            log("connect failed: %s" % e)
            self.enterFailureState();
            return False

    def isConnected(self):
        return self.connected

    def enterFailureState(self):
        self.connected = False
        self.__socket = None

    def __del__(self):
        '''Destructor
        '''
        self.__socket.close()

    def Register(self, friendlyName, priority):
        builder = flatbuffers.Builder(0)
        name = builder.CreateString(friendlyName);

        RegisterStart(builder)
        RegisterAddOrigin(builder, name)
        RegisterAddPriority(builder, priority)

        return self.__sendMessage(builder, Command.Register, RegisterEnd(builder))

    def sendColor(self, color, duration = -1):
        '''Send a static color to Hyperion
        - color    : integer value with the color as 0x00RRGGBB
        - duration : duration the leds should be set
        ''' 
        builder = flatbuffers.Builder(0)
        ColorStart(builder)
        ColorAddRgbColor(builder, color)
        ColorAddDuration(builder, duration)
        return self.__sendMessage(builder, Command.Color, ColorEnd(builder))
        
    def sendImage(self, width, height, data, duration = -1):
        '''Send an image to Hyperion
        - width    : width of the image
        - height   : height of the image
        - data     : image data (byte string containing 0xRRGGBB pixel values)
        - duration : duration the leds should be set
        ''' 
        builder = flatbuffers.Builder(width * height * 3)

        buffer = builder.CreateByteVector(data);
        RawImageStart(builder)
        RawImageAddData(builder, buffer)
        RawImageAddHeight(builder,height)
        RawImageAddWidth(builder,width)
        rawImageData = RawImageEnd(builder);

        ImageStart(builder)
        ImageAddDuration(builder, duration)
        ImageAddDataType(builder, ImageType.RawImage)
        ImageAddData(builder, rawImageData)

        return self.__sendMessage(builder, Command.Image, ImageEnd(builder))
        
    def clear(self, priority):
        '''Clear the given priority channel
        - priority : the priority channel to clear
        '''

        log("Clear blocked, conflicting implementation")
        return;

        builder = flatbuffers.Builder(0)

        ClearStart(builder)

        if priority != -1:
            ClearAddPriority(builder,priority)

        return self.__sendMessage(builder, Command.Clear, ClearEnd(builder))
    
    def clearall(self):
        '''Clear all active priority channels
        '''
        return clear(-1)
        
    def __sendMessage(self, builder, commandType, command):
        '''Send the given flatbuffers message to Hyperion. 
        - message : flatbuffers request to send
        '''
        try:
            RequestStart(builder)
            RequestAddCommandType(builder, commandType) 
            RequestAddCommand(builder, command)
            builder.Finish(RequestEnd(builder))

            msg = builder.Output()
            self.__socket.sendall(struct.pack(">I", len(msg)) + msg)
            return True;
        except Exception, e:
            self.enterFailureState()
            log("__sendMessage: %s" % e)
            return False;

    def __sendMessageCompressed(self, message): 
        '''Sends a compressed proto message to Hyperion.
        - message : proto request to send
        '''
        log("__sendMessageCompressed - not implemented")
        pass
        # import zlib
        # send message to Hyperion"
        # compressor = zlib.compressobj(1, zlib.DEFLATED, -15)
        # binaryRequest = message.SerializeToString()
        # import datetime
        # a = datetime.datetime.now()
        # binaryGzip = compressor.compress(binaryRequest) + compressor.flush()
        # b = datetime.datetime.now()
        # c = b - a
        # print (c.total_seconds() * 1000)
        # 
        # binarySize = struct.pack(">I", len(binaryRequest))
        # gzipSize = struct.pack(">I", len(binaryGzip))
        # 
        # self.__socket.sendall(gzipSize + binarySize + binaryGzip)