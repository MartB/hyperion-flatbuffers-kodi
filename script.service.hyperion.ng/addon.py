'''
	Kodi video capturer for Hyperion
	Copyright (c) 2017 MartB

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

import xbmc
import xbmcaddon
import xbmcgui
import os

# Add the library path before loading Hyperion
__addon__	=	xbmcaddon.Addon()
__cwd__ 	=	__addon__.getAddonInfo('path')
sys.path.append(xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')))
		
from settings import Settings
from Hyperion import Hyperion
from misc import log, notify

settings = Settings()

main = None
playerMonitor = None
xbmcMonitor = None

class HyperionMonitor( xbmc.Monitor ):
  def __init__( self, *args, **kwargs ):
    xbmc.Monitor.__init__( self )
    self.abortRequested = xbmc.abortRequested
        
  def onSettingsChanged( self ):
    settings.readSettings()
    # <todo> We should probably reset the connection here if any connection relevant setting changed

  def onAbortRequested(self):
    self.abortRequested = True

  def onScreensaverDeactivated( self ):
    settings.setScreensaver(False)
      
  def onScreensaverActivated( self ):    
    settings.setScreensaver(True)

class HyperionPlayer( xbmc.Player ):
    GRABBING_START = 0
    GRABBING_STOP = 1
    GRABBING_PAUSE = 2

    def __init__( self, *args, **kwargs ):
        if xbmc.Player().isPlaying():
            if xbmc.getCondVisibility("Player.Paused"):
                self.setGrabbingState(self.GRABBING_PAUSED)
            else:
                self.setGrabbingState(self.GRABBING_START)
        else:
            self.setGrabbingState(self.GRABBING_STOP)

    def onPlayBackStarted(self):
        log("onPlayBackStarted")
        self.setGrabbingState(self.GRABBING_START)

    def onPlayBackResumed(self):
        log("playbackResumed")
        self.setGrabbingState(self.GRABBING_START)

    def onPlayBackEnded(self):
        log("onPlayBackEnded")
        self.setGrabbingState(self.GRABBING_STOP)

    def onPlayBackStopped(self):
        log("onPlayBackStopped")
        self.setGrabbingState(self.GRABBING_STOP)

    def onPlayBackPaused(self):
        log("onPlayBackPaused")
        self.setGrabbingState(self.GRABBING_PAUSE)

    def setGrabbingState(self, state):
        self.grabbingState = state
        main.playerStateChangedCB(state)

    def getGrabbingState(self):
        return self.grabbingState

class HyperionKodiGrabber():
    def __init__( self, *args, **kwargs ):
        self.hyperion = Hyperion(settings)
        self.reconnectTries = 0
        self.capture = xbmc.RenderCapture()
        self.currentSettingsRev = settings.rev

    def process(self):
        if playerMonitor.getGrabbingState() != HyperionPlayer.GRABBING_START or not xbmc.getCondVisibility("Player.Playing"):
            xbmc.sleep(100)
            return

        rawImgBuf = self.capture.getImage() # lets wait up to 250ms for an image, otherwise we are lagging behind heavily
        rawImgLen = len(rawImgBuf)
        expectedLen = settings.capture_width * settings.capture_height * 4;
        if rawImgLen < expectedLen:
            # Check if we got a null image from the renderer.
            if rawImgLen == 0:
                return
            
            log("Faulty image! Size was: %d expected: %d" % (rawImgLen, expectedLen))
            return


        # Convert image to RGB from BGRA (default after 17)
        del rawImgBuf[3::4]
        rawImgBuf[0::3], rawImgBuf[2::3] = rawImgBuf[2::3],rawImgBuf[0::3]
    
        # If this call fails, it will make us reconnect.
        if not self.hyperion.sendImage(settings.capture_width, settings.capture_height, rawImgBuf, settings.priority, -1):
            notify(xbmcaddon.Addon().getLocalizedString(32101))
            return
 
                
        sleeptime = settings.delay

        if settings.useDefaultDelay == False:
            try:
                videofps = math.ceil(float(xbmc.getInfoLabel('Player.Process(VideoFPS)')))
                if videofps == 24:
                    sleeptime = self.__settings.delay24
                if videofps == 25:
                    sleeptime = self.__settings.delay25
                if videofps == 50:
                    sleeptime = self.__settings.delay50
                if videofps == 59:
                    sleeptime = self.__settings.delay59
                if videofps == 60:
                    sleeptime = self.__settings.delay60
            except ValueError:
                pass

        # Minimum sleep of 1 millisecond otherwise the event processing dies.
        xbmc.sleep(max(1, sleeptime)) 

    def checkAvailability(self):
        lastConnectResult = True
        if not self.hyperion.isConnected():
            self.reconnectTries += 1
            lastConnectResult = self.hyperion.connect()
            if not lastConnectResult:
                if self.reconnectTries > 2:
                    self.modifiedTimeoutSleep()
            else:
                # We got the connection back.
                self.reconnectTries = 0

        return lastConnectResult

    def modifiedTimeoutSleep(self):
        for i in range(0, settings.timeout - 1):
            if xbmcMonitor.abortRequested:
                return
            if settings.rev != self.currentSettingsRev:
                self.currentSettingsRev = settings.rev
                return
            else:
                xbmc.sleep(1000)

    def playerStateChangedCB(self, state):
        if state == HyperionPlayer.GRABBING_START:
            self.capture = xbmc.RenderCapture()
            self.capture.capture(settings.capture_width, settings.capture_height)
        elif state == HyperionPlayer.GRABBING_STOP:
            if not self.hyperion.isConnected():
                log("grabbing stopped but client was not connected")
                return
            xbmc.sleep(100)
            self.hyperion.clear(settings.priority)

def runGrabber():
    global xbmcMonitor, playerMonitor, main
    main = HyperionKodiGrabber()
    xbmcMonitor   = HyperionMonitor()
    playerMonitor = HyperionPlayer()

    while not xbmcMonitor.abortRequested:
        if not settings.isEnabled():
            xbmc.sleep(500)
            continue

        if not main.checkAvailability():
            continue

        main.process()

    del main
    del xbmcMonitor
    del playerMonitor

if  __name__ == "__main__":
	runGrabber()