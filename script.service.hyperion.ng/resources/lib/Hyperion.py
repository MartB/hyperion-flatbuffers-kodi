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
from proto.ImageRequest import *
from proto.ClearRequest import *
from proto.HyperionRequest import *
from proto.Command import Command
from proto.Type import Type

from misc import log, notify
class Hyperion(object):
    '''Hyperion connection class
    
    A Hyperion object will connect to the Hyperion server and provide
    easy to use functions to send requests
    
    Note that the function will block until a reply has been received
    from the Hyperion server (or the call has timed out)
    '''
    
    def __init__(self, server, port):
        '''Constructor
        - server : server address of Hyperion
        - port   : port number of Hyperion
        '''
        self.host = server
        self.port = port
        self.reconnectTries = 0
        self.connected = False
       
    def connect(self):
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.__socket.settimeout(2)
            self.__socket.connect((self.host, self.port))
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

    def sendColor(self, color, priority, duration = -1):
        '''Send a static color to Hyperion
        - color    : integer value with the color as 0x00RRGGBB
        - priority : the priority channel to use
        - duration : duration the leds should be set
        ''' 
        builder = flatbuffers.Builder(0)
        ColorRequestStart(builder)
        ColorRequestAddDuration(builder, duration)
        ColorRequestAddPriority(builder, priority)
        ColorRequestAddRgbColor(builder, color)
        colorReqData = ColorRequestEnd(builder)

        HyperionRequestStart(builder)
        HyperionRequestAddCommand(builder, Command.COLOR) 
        HyperionRequestAddColorRequest(builder, colorReqData)
        builder.Finish(HyperionRequestEnd(builder))

        return self.__sendMessage(builder.Output())
        
    def sendImage(self, width, height, data, priority, duration = -1):
        '''Send an image to Hyperion
        - width    : width of the image
        - height   : height of the image
        - data     : image data (byte string containing 0xRRGGBB pixel values)
        - priority : the priority channel to use
        - duration : duration the leds should be set
        ''' 
        builder = flatbuffers.Builder(width * height * 3)

        imgBytes = builder.CreateByteVector(data)
        ImageRequestStart(builder)
        ImageRequestAddDuration(builder, duration)
        ImageRequestAddImageheight(builder, height)
        ImageRequestAddImagewidth(builder, width)
        ImageRequestAddPriority(builder, priority)
        ImageRequestAddImagedata(builder, imgBytes)
        imgReqData = ImageRequestEnd(builder)

        HyperionRequestStart(builder)
        HyperionRequestAddCommand(builder, Command.IMAGE) 
        HyperionRequestAddImageRequest(builder, imgReqData)
        builder.Finish(HyperionRequestEnd(builder))

        return self.__sendMessage(builder.Output())
        
    def clear(self, priority):
        '''Clear the given priority channel
        - priority : the priority channel to clear
        '''
        builder = flatbuffers.Builder(0)

        ClearRequestStart(builder)
        ClearRequestAddPriority(builder,priority)
        clearReqData = ClearRequestEnd(builder)

        HyperionRequestStart(builder)
        HyperionRequestAddCommand(builder, Command.CLEAR) 
        HyperionRequestAddClearRequest(builder, clearReqData)
        builder.Finish(HyperionRequestEnd(builder))

        print "clearing ..."
    
        return self.__sendMessage(builder.Output())
    
    def clearall(self):
        '''Clear all active priority channels
        '''
        builder = flatbuffers.Builder(0)

        HyperionRequestStart(builder)
        HyperionRequestAddCommand(builder, Command.CLEARALL) 
        builder.Finish(HyperionRequestEnd(builder))

        return self.__sendMessage(builder.Output())
        
    def __sendMessage(self, msg):
        '''Send the given flatbuffers message to Hyperion. 
        - message : flatbuffers request to send
        '''
        try:
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