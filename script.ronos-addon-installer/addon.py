import xbmcaddon
import xbmcgui
 
addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')

text = "Updated Plugins! new plugins:\nhot kodi kipi itzik"

xbmcgui.Dialog().ok(addonname, line1)