# -*- coding: utf-8 -*
# (c) oWakef
# support@liveil.tv
#
# liveil tv XML/json api

import urllib2

from time import time
import datetime

import re, os, sys

__author__ = 'oWakef <support@liveil.tv>'
__version__ = '1.00'

IPTV_DOMAIN = 'iptv.liveil.tv'
IPTV_API = 'http://%s/api/v1/' % IPTV_DOMAIN
token = ''

try:
	import xbmc, xbmcaddon
except ImportError:
	class xbmc_boo:
		
		def __init__(self):
			self.nonXBMC = True
			self.LOGDEBUG = 1
			self.LOGWARNING = 2
		
		def output(self, data, level = 0):
			print ("xbmc.log is depricated. use xbmc.log instead")
			self.log(data, level)
		
		def log(self, data, level = 0):
			print (data)
		
		def getInfoLabel(self, param):
			return '%s unknown' % param
		
		def translatePath(self, param):
			return './'
		
		def getVersion(self):
			xbmc_version = xbmc.getInfoLabel( "System.BuildVersion" )
			return xbmc_version[:2]
		
	
	class xbmcaddon_foo:
		def __init__(self, id):
			self.id = id
		
		def getAddonInfo(self, param):
			if param == 'version':
				return __version__
			elif param == 'id':
				return self.id + '/%s (by %s) ' % (__version__, __author__)
			else:
				return '%s unknown' % param
	
	class xbmcaddon_boo:
		def Addon(self, id = ''):
			if not id:
				id = os.path.basename(__file__)
			return xbmcaddon_foo(id)
	
	xbmc = xbmc_boo()
	xbmcaddon = xbmcaddon_boo()


#
# platform package usage disabled as
# cousing problems with x64 platforms
#
#try:
#	import platform
#except ImportError:
class platform_boo:
	
	def system(self):
		return os.name
	
	def release(self):
		plat = sys.platform
		return plat
		
	def processor(self):
		return ""
	
	def machine(self):
		return ""
		
	def python_version(self):
		ver = sys.version_info
		return '%s.%s.%s' % (ver[0], ver[1], ver[2])

platform = platform_boo()

try:
	import json
except ImportError:
	xbmc.log('[LiveIL.TV] module json is not available')
else:
	JSONDECODE = json.loads
	JSONENCODE = json.dumps


class liveil:
	
	def __init__(self, login, password, code, addonid = '', token = None):
		self.token = token
		self.channels = []
		self.expires = 0
		self.login = login
		self.code = code
		self.password = password
		self.addonid = addonid
		self.AUTH_OK = False
		
		self.last_list = None
		
	
	def genUa(self):
		osname = '%s %s; %s' % (platform.system(), platform.release(), platform.python_version())
		
		__settings__ = xbmcaddon.Addon(self.addonid)
		
		isXBMC = 'LIVEIL-XBMC'
	#	if getattr(xbmc, "nonXBMC", None) is not None:
	#		isXBMC = 'LIVEIL-nonXBMC' 
		
		ua = '%s %s [%s] Addon/(%s;%s)' % (isXBMC, xbmc.getInfoLabel('System.BuildVersion'), osname, __settings__.getAddonInfo('id'), __settings__.getAddonInfo('version'))
		xbmc.log('[LiveIL.TV] UA: %s' % ua)
		return ua
	
	def _request(self, cmd, parameters):
		
		url = IPTV_API + cmd + '.json?' + parameters 
		
		#log.info('Requesting %s' % url)
		xbmc.log('[LiveIL.TV] REQUESTING: %s' % url)
		
		ua = self.genUa()
		
		#req = urllib2.Request(url, postparams, {'User-agent': ua, 'Connection': 'Close', 'Accept': 'application/json, text/javascript, */*', 'X-Requested-With': 'XMLHttpRequest'})
		req = urllib2.Request(url)
		req.add_header('User-agent', ua)
		req.add_header('Connection', 'Close')
		req.add_header('Accept', 'application/json, text/javascript, */*')
		req.add_header('X-Requested-With', 'XMLHttpRequest')
		if token == None and getattr(xbmc, "nonXBMC", None) is not None:
			path = cmd+"?"+params
			extra = {}
			extra['screen'] = xbmc.getInfoLabel('System.ScreenMode')
		
		rez = urllib2.urlopen(req).read()
		xbmc.log('[LiveIL.TV] Got %s' % rez, level=xbmc.LOGDEBUG)
		
		try:
			res = JSONDECODE(rez)
		except:
			xbmc.log('[LiveIL.TV] Error.. :(')
			
		self._errors_check(res)
		
		return res
	
	def _auth(self, user, password, code): 
		self.AUTH_OK = False
		response = self._request('login', 'client_id=%s&pass=%s&response_type=token&code=%s' % (user, password, code))
		if response['code'] == 200:
			self.token = response['data']['authorization']['item']['access_token']
			self.AUTH_OK = True
			xbmc.log('[LiveIL.TV] I got the following token [%s]' % (self.token))
	
	def app_list(self):
		response = self._request('app_list', 'token=%s' % (self.token))
		
		return response	
	
	def info(self):
		response = self.request('info', 'token=%s' % (self.token))
		
		return response	
	
	def channel_list(self,token):
		response = self._request('channel_list', 'token=%s' % (token))
		
		return response
		
	def full_channel_list(self,token):	
		response = self._request('full_channel_list', 'token=%s' % (token))
		
		return response	
		
	def radio(self):
		response = self.request('radio', 'token=%s' % (self.token))
			
		return response	
		
	def get_url(self,cid,token):
		response = self._request('get_url', 'token=%s&cid=%s&device=stb' % (token,cid))
		#url = response['data']['url']+'&token='+self.token
		
		url =  response['data']['url']
		return url		
	
	def get_ndvr(self,cid,dvr_time):
		response = self.request('get_ndvr', 'token=%s&cid=%s&time=%s&device=stb' % (self.token,sid,dvr_time))
			
		return response	
		
	def epg(self,cid,date,lang,token):	
		response = self._request('epg', 'token=%s&cid=%s&date=%s&lang=%s' % (token,cid,date,lang))
		
		return response	
		
	def epg7(self,token):
		response = self._request('epg7', 'token=%s' % (token))

		return response		
		
	def epg24(self,cid,dtime):
		response = self.request('epg24', 'token=%s&cid=%s&dtime=%s' % (self.token,cid,dtime))
			
		return response		
		
	def recorded_url (self,id,token):
		response = self._request('recorded_url', 'token=%s&id=%s&device=stb' % (token,id))
		
		url =  response['data']['url']
		return url	
		
	def genres (self,token):
		response = self._request('genres', 'token=%s' % (token))
		
		return response
		
	def movie_list(self,token):
		response = self._request('movie_list', 'token=%s' % (token))
		
		return response	
		
	def movie_list_genre(self,gid,token):
		response = self._request('movie_list', 'token=%s&gid=%s' % (token,gid))	
		
		return response	
		
	def movie_info(self,mid,token):
		response = self._request('movie_info', 'token=%s&mid=%s' % (token,mid))
		
		info =  response['data']['movie'][0]
		return info
	
	def movie_url(self,mid,token):
		response = self._request('movie_url', 'token=%s&mid=%s&device=stb' % (token,mid))
		
		url =  response['data']['url']
		return url	
		
	def series_list(self):
		response = self.request('series_list', 'token=%s' % (self.token))
		
		return response	
			
	def series_list_genre(self,gid,token):
		response = self._request('series_list', 'token=%s&gid=%s' % (token,gid))
		
		return response	
		
	def series_list_series_id(self,sid,token):
		response = self._request('series_list', 'token=%s&sid=%s' % (token,sid))
		
		return response		
	
	def series_list_season(self,sid,season,token):
		response = self._request('series_list', 'token=%s&sid=%s&season=%s' % (token,sid,season))
		
		return response	
	
	def series_seasons(self,sid,token):
		response = self._request('series_seasons', 'token=%s&sid=%s' % (token,sid))
		
		return response	
	
	def series_info_series_id(self,sid):
		response = self.request('series_info', 'token=%s&sid=%s' % (self.token,sid))
		
		return response	
		
	def series_info_episode_id(self,eid,token):
		response = self._request('series_info', 'token=%s&eid=%s' % (token,eid))
		
		info =  response['data']['episode']
		return info
	
	def series_url(self,id,token):
		response = self._request('series_url', 'token=%s&eid=%s&device=stb' % (token,id))
		
		url =  response['data']['url']
		return url	
		
	def radio_list(self,token):
		response = self._request('radio_list', 'token=%s' % (token))
		
		return response	
	
	def radio_info(self,rid,token):
		response = self._request('radio_info', 'token=%s&rid=%s' % (token,rid))
		
		url =  response['data']['radio']
		return url	
		
	def radio_url(self,rid,token):
		response = self._request('radio_url', 'token=%s&rid=%s&device=stb' % (token,rid))
		
		url =  response['data']['url']
		return url
	
	
	def moviesSearch(self,name,token):
		response = self._request('moviesSearch', 'token=%s&name=%s' % (token,name))
		
		return response	
		
	def seriesSearch(self,name,token):
		response = self._request('seriesSearch', 'token=%s&name=%s' % (token,name))
		
		return response	

	def _errors_check(self, json):
		if 'error' in json:
			err = json['error']['message'].encode('utf8')
			xbmc.log('[LiveIL.TV] ERROR: %s' % err)
			self.error_message = err
			self.AUTH_OK = False
	
	def test(self):
		
		print(self.getCurrentInfo(7))
	
	def testAuth(self):
		if self.token == None:
			self._auth(self.login, self.password, self.code)
		
		return self.token
	
	def error_message(self):
	
		#return self.error_message
		return 1