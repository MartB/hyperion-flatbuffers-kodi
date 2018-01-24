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
import xbmc
import xbmcaddon

from misc import log

class Settings:
    def __init__(self):
        self.rev = 0
        self.readSettings()

    def readSettings(self):
        log("Loading settings")
        addon = xbmcaddon.Addon()
        self.enable = bool(addon.getSetting("hyperion_enable"))
        self.enableScreensaver = bool(addon.getSetting("screensaver_enable"))
        self.address = addon.getSetting("hyperion_ip")
        self.port = int(addon.getSetting("hyperion_port"))
        self.priority = int(addon.getSetting("hyperion_priority"))
        self.timeout = int(addon.getSetting("reconnect_timeout"))
        self.capture_width = int(addon.getSetting("capture_width"))
        self.capture_height = int(addon.getSetting("capture_height"))
        
        # Hack around Kodi's settings readout limitations
        self.useDefaultDelay = addon.getSetting('use_default_delay').lower() == 'true'
        
        self.delay = int(addon.getSetting("delay"))
        self.delay24 = int(addon.getSetting("delay24"))
        self.delay25 = int(addon.getSetting("delay25"))
        self.delay50 = int(addon.getSetting("delay50"))
        self.delay59 = int(addon.getSetting("delay59"))
        self.delay60 = int(addon.getSetting("delay60"))
        
        self.showErrorMessage = True
        self.rev += 1
        
    def isEnabled(self):
        return self.enable