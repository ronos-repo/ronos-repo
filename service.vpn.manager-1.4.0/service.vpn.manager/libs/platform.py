#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2016 Zomboided
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#    Platform specific calls used by VPN Manager for OpenVPN add-on.

import os
import shlex
import subprocess
import sys
import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
from libs.utility import debugTrace, errorTrace, infoTrace, enum
from sys import platform


# **** ADD MORE PLATFORMS HERE ****
platforms = enum(UNKNOWN=0, WINDOWS=1, LINUX=2, RPI=3, ANDROID=4, MAC=5)  
platforms_str = ("Unknown", "Windows", "Linux, openvpn installed", "Linux, openvpn plugin", "Android", "Apple")


def fakeConnection():
    # Return True to fake out any calls to openVPN to change the network
    return False

    
def getPlatform():
    # Work out which platform is being used.
    build = xbmc.getInfoLabel('System.BuildVersion')
    build_number = int(build[0:2])
    if sys.platform == "win32": return platforms.WINDOWS
    if sys.platform == "linux" or sys.platform == "linux2":
        if build_number == 15 and getAddonPath(True, "").startswith("/storage/.kodi/"):
            # For OE 6.0.0 (Kodi 15), openvpn is a separate install             
            return platforms.RPI
        else:
            # Other OE versions and other Linux installs use the openvpn installed in usr/sbin
            return platforms.LINUX
            
    # **** ADD MORE PLATFORMS HERE ****
    
    #if sys.platform == "?": return platforms.ANDROID
    #if sys.platform == "darwin": return platforms.MAC
    return platforms.UNKNOWN    
        

def useSudo():
    sudo_setting = xbmcaddon.Addon("service.vpn.manager").getSetting("openvpn_sudo")
    if sudo_setting == "Always": return True
    if sudo_setting == "Never": return False
    if getPlatform() == platforms.LINUX:
        # For non-OpenELEC Linux (based on the path name...) we don't need to use sudo
        if not getAddonPath(True, "").startswith("/storage/.kodi/"): return True
    return False


def useBigHammer():
    hammer = xbmcaddon.Addon("service.vpn.manager").getSetting("openvpn_killall")
    if hammer == "true": 
        return True
    else:
        return False
    
    
def getPlatformString():
    p = getPlatform()
    return platforms_str[p]


def getVPNLogFilePath():
    # Return the full filename for the VPN log file
    # It's platform dependent, but can be forced to the Kodi log location
    use_kodi_dir = xbmcaddon.Addon("service.vpn.manager").getSetting("openvpn_log_location")
    p = getPlatform()
    if p == platforms.WINDOWS or use_kodi_dir == "true" :
        # Putting this with the other logs on Windows
        return xbmc.translatePath("special://logpath/openvpn.log")
    if p == platforms.LINUX or p == platforms.RPI:
        # This should be a RAM drive so doesn't wear the media
        return "/run/openvpn.log"
        
    # **** ADD MORE PLATFORMS HERE ****
    
    return ""
    

def stopVPN():
    # Little hammer
    stopVPNn("15")
    return
    
    
def stopVPN9():
    # Big hammer
    stopVPNn("9")
    return

    
def stopVPNn(n):
    # Stop the platform VPN task.
    if not fakeConnection():
        p = getPlatform()
        if p == platforms.LINUX or p == platforms.RPI:
            if useBigHammer(): n = "9"
            command = "killall -" + n + " openvpn"
            if useSudo(): command = "sudo " + command
            debugTrace("(Linux) Stopping VPN with " + command)
            os.system(command)
        if p == platforms.WINDOWS:
            # This call doesn't pay any attention to the size of the hammer.
            # Probably for Windows, if n is 15, then I should omit the /F but
            # I've not noticed any problems using /F so the n is ignored
            command = "taskkill /F /T /IM openvpn*"
            debugTrace("(Windows) Stopping VPN with " + command)
            args = shlex.split(command)
            proc = subprocess.Popen(args, creationflags=subprocess.SW_HIDE, shell=True)
            
        # **** ADD MORE PLATFORMS HERE ****
        
    return
        
    
def startVPN(vpn_profile):
    # Call the platform VPN to start the VPN
    if not fakeConnection():
        p = getPlatform()
        if p == platforms.RPI or p == platforms.LINUX:
            command=getOpenVPNPath() + " \"" + vpn_profile + "\" > " + getVPNLogFilePath() + " &"
            if useSudo() : command = "sudo " + command            
            debugTrace("(Linux) Starting VPN with " + command)
            os.system(command)
        if p == platforms.WINDOWS:   
            command=getOpenVPNPath() + " \"" + vpn_profile + "\""
            debugTrace("(Windows) Starting VPN with " + command)
            args = shlex.split(command)
            outfile = open(getVPNLogFilePath(),'w')
            proc = subprocess.Popen(args, stdout=outfile, creationflags=subprocess.SW_HIDE, shell=True)
            
        # **** ADD MORE PLATFORMS HERE ****
        
    else:
        # This bit is just to help with debug during development.
        command=getOpenVPNPath() + " \"" + vpn_profile + "\" > " + getVPNLogFilePath()
        debugTrace("Faking starting VPN with " + command)
    return


def getOpenVPNPath():
    # Call the platform VPN to start the VPN
    if fakeConnection():
        p = platforms.RPI
    else:
        p = getPlatform()
        
    if p == platforms.RPI:
        return getAddonPath(False, "network.openvpn/bin/openvpn")
    if p == platforms.LINUX:            
        return "/usr/sbin/openvpn"
    if p == platforms.WINDOWS:
        # No path specified as install will update command path
        return "openvpn"
        
    # **** ADD MORE PLATFORMS HERE ****
    
    return


def checkPlatform(addon):
    if not fakeConnection():
        p = getPlatform()
        dialog_msg = ""
        if p == platforms.UNKNOWN:
            dialog_msg = addon.getAddonInfo("name") + " is not currently supported on this hardware platform."
            xbmcgui.Dialog().ok(addon.getAddonInfo("name"), dialog_msg)
            return False
    return True

    
def checkVPNInstall(addon):
    # Check that openvpn plugin exists (this was an issue with OE6), there's
    # another check below that validates that the command actually works
    if not fakeConnection():
        p = getPlatform()
        dialog_msg = ""
        if p == platforms.RPI:
            command_path = getAddonPath(False, "network.openvpn/bin/openvpn")
            if xbmcvfs.exists(command_path):
                # Check the version that's installed
                vpn_addon = xbmcaddon.Addon("network.openvpn")
                version =  vpn_addon.getAddonInfo("version")
                version = version.replace(".", "")
                if int(version) >= 600: return True
            dialog_msg = "OpenVPN executable not available.  Install the openvpn plugin, version 6.0.1 or greater from the OpenELEC unofficial repo."
            # Display error message
            xbmcgui.Dialog().ok(addon.getAddonInfo("name"), dialog_msg)
    return True

    
def checkVPNCommand(addon):
    # Issue the openvpn command and see if the output is a bunch of commands
    if not fakeConnection():
        p = getPlatform()
        # Issue the openvpn command, expecting to get the options screen back
        if p == platforms.RPI or p == platforms.LINUX:
            # Issue Linux command
            command = getOpenVPNPath() + " > " + getVPNLogFilePath() + " &"
            if useSudo() : command = "sudo " + command
            infoTrace("platform.py", "Testing openvpn with : " + command)
            os.system(command)
        elif p == platforms.WINDOWS:
            # Issue Windows command
            command=getOpenVPNPath()
            infoTrace("platform.py", "Testing openvpn with : " + command)
            args = shlex.split(command)
            outfile = open(getVPNLogFilePath(),'w')
            proc = subprocess.Popen(args, stdout=outfile, creationflags=subprocess.SW_HIDE, shell=True)
        else:
            errorTrace("platform.py", "Unsupported platform " + str(p))
            
        # **** ADD MORE PLATFORMS HERE ****
                
        # Waiting for the log file to appear            
        xbmc.sleep(1000)
        i = 0
        while not xbmcvfs.exists(getVPNLogFilePath()) and i < 10:
            xbmc.sleep(1000)
            i = i + 1
        # If the log file appears, check it's what we expect
        if xbmcvfs.exists(getVPNLogFilePath()):
            log_file = open(getVPNLogFilePath(), 'r')
            log_file_lines = log_file.readlines()
            log_file.close()
            # Look for a phrase we'd expect to see if the call
            # worked and the list of options was displayed
            for line in log_file_lines:
                if "General Options" in line:
                    return True
            # Write the log file in case there's something in it
            errorTrace("platform.py", "Ran openvpn command and it failed")            
            writeVPNLog()
            dialog_msg = "The OpenVPN executable isn't working.  Check the log, then from a command line prompt type 'openvpn' and fix any problems reported."
        else:
            errorTrace("platform.py", "Ran openvpn command and VPN log didn't appear")
            dialog_msg = "The OpenVPN executable isn't writing out a log.  Try changing the Kodi log directory setting in Settings-Debug menu and retry."
        
        # Display an error message
        xbmcgui.Dialog().ok(addon.getAddonInfo("name"), dialog_msg)
        return False
        
    else: return True

    
def isVPNTaskRunning():
    # Return True if the VPN task is still running, or the VPN connection is still active
    # Return False if the VPN task is no longer running and the connection is not active
    
    if fakeConnection(): return True
    
    p = getPlatform()
    if p == platforms.LINUX or p == platforms.RPI:
        try:
            command = "pidof openvpn"
            if useSudo() : command = "sudo " + command
            debugTrace("(Linux) Checking VPN task with " + command)
            pid = os.system(command)
            # This horrible call returns 0 if it finds a process, it's not returning the PID number
            if pid == 0 : return True
            return False
        except:
            errorTrace("platform.py", "VPN task list failed")
            return False
    if p == platforms.WINDOWS:
        try:
            command = 'tasklist /FI "IMAGENAME eq OPENVPN.EXE"'
            debugTrace("(Windows) Checking VPN task with " + command)
            args = shlex.split(command)
            out = subprocess.check_output(args, creationflags=subprocess.SW_HIDE, shell=True).strip()
            if "openvpn.exe" in out:
                return True
            else:
                return False
        except:
            errorTrace("platform.py", "VPN task list failed")
            return False

    # **** ADD MORE PLATFORMS HERE ****
    
    return False


connection_status = enum(UNKNOWN=0, CONNECTED=1, AUTH_FAILED=2, NETWORK_FAILED=3, TIMEOUT=4, ROUTE_FAILED=5, ACCESS_DENIED=6, ERROR=7) 
    
def getVPNConnectionStatus():
    # Open the openvpn output file and parse it for known phrases
    # Return 'connected', 'auth failed', 'network failed', 'error' or ''

    if fakeConnection(): return connection_status.UNKNOWN

    # **** ADD MORE PLATFORMS HERE ****
    # Might not need to mess with this too much if the log output from different platform openvpns are the same
    
    p = getPlatform()
    if p == platforms.LINUX or p == platforms.RPI or p == platforms.WINDOWS:
        path = getVPNLogFilePath()
        state = connection_status.UNKNOWN
        if xbmcvfs.exists(path):
            debugTrace("Reading log file")
            log = open(path,'r')
            lines = log.readlines()
            for line in lines:
                if "Initialization Sequence Completed" in line:
                    state = connection_status.CONNECTED
                    break
                if "AUTH_FAILED" in line:
                    state = connection_status.AUTH_FAILED
                if "private key password verification failed" in line:
                    state = connection_status.AUTH_FAILED
                if "TLS Error" in line:
                    state = connection_status.NETWORK_FAILED
                if "Connection timed out" in line:
                    state = connection_status.TIMEOUT
                if p == platforms.WINDOWS and "ROUTE" in line and "Access is denied" in line:
                    # This is a Windows, not running Kodi as administrator error
                    state = connection_status.ACCESS_DENIED
                    break
                #if "ERROR: Linux route" in line:
                    # state = connection_status.ROUTE_FAILED
                    # This tests for a Linux route failure, only it's commented out as
                    # it can legitimately fail if the route already exists.  If it fails
                    # for other reasons, I can't tell the different just yet.
                    # break
            log.close()
            # Haven't found what's expected so return an empty stream
            if not state == connection_status.UNKNOWN: debugTrace("VPN connection status is " + str(state))
            return state
        else:
            errorTrace("platform.py", "Tried to get VPN connection status but log file didn't exist")
            return connection_status.ERROR

            
def writeVPNLog():
    # Write the openvpn output log to the error file
    try:
        log_file = open(getVPNLogFilePath(), 'r')
        log_output = log_file.readlines()
        log_file.close()
        infoTrace("platform.py", "VPN log file start >>>")
        for line in log_output:
            print line
        infoTrace("platform.py", "<<< VPN log file end")
    except:
        errorTrace("platform.py", "Couldn't write VPN error log")


def getSeparator():
    if getPlatform() == platforms.WINDOWS:
        return "\\"
    else:
        return "/"
        
    
def getAddonPath(this_addon, path):
    # Return the URL of the addon directory, plus any addition path/file name.
    if this_addon:
        return xbmc.translatePath("special://home/addons/service.vpn.manager/" + path)
    else:
        return xbmc.translatePath("special://home/addons/" + path)
        

def getUserDataPath(path):
    return xbmc.translatePath("special://userdata/addon_data/service.vpn.manager/" + path)
    
    
def getLogPath():    
    return xbmc.translatePath("special://logpath/kodi.log")
        
        
        
