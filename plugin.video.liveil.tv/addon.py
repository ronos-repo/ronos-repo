#!/usr/bin/python
#/*
#!/usr/bin/python
#/*
# *      Copyright (C) 2010-2015 LiveIL.tv Team
# *
# *  This Program is free software; Nevertheless you can not redistribute
# *  it and/or modify it under any Term.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *

import xbmcaddon, string, xbmc, xbmcgui, xbmcplugin, os
PLUGIN_ID = 'plugin.video.liveil.tv'
VERSION = '1.3.8'
__base_url__ = 'http://iptv.liveil.tv%s'
addon = xbmcaddon.Addon(id=PLUGIN_ID)
sys.path.append(os.path.join(addon.getAddonInfo('path'), 'resources', 'lib'))

import iptv

import datetime, time
import urllib, threading, re

__settings__ = xbmcaddon.Addon(id=PLUGIN_ID)
__language__ = __settings__.getLocalizedString
__thumbpath__ = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'icons')
USERNAME = __settings__.getSetting('username')
USERPASS = __settings__.getSetting('password')
PARENTALCODE = __settings__.getSetting('parental_code')
LANGUAGE = __settings__.getSetting('language')
handle = int(sys.argv[1])
fanart = os.path.join(__settings__.getAddonInfo('path'), 'fanart.jpg')
xbmcplugin.setPluginFanart(handle, fanart, color2='0xFFFF3300')

PLUGIN_NAME = 'LiveIL.TV'
PLUGIN_CORE = None
TRANSSID = ''

thumb = os.path.join( addon.getAddonInfo('path'), "icon.png" )

def get_params():
	param=[]
	paramstring=sys.argv[2]
	xbmc.log('[%s] parsing params from %s' % (PLUGIN_NAME, paramstring))
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param

def resetAlarms(plugin, mode):
	refreshAlarmId = '%s_refresh_list' % PLUGIN_ID
	xbmc.executebuiltin("XBMC.CancelAlarm(%s,True)" % refreshAlarmId)
	resetInfoTimers()

def ShowRoot(plugin,token):
	uri = sys.argv[0] + '?mode=%s&token=%s'
	application_list=plugin.app_list()
	for app in application_list['data']['channels']:
		if int(app['status']) == 1:
			item=xbmcgui.ListItem(app['name'],iconImage='DefaultVideo.png', thumbnailImage=os.path.join(__thumbpath__, app['id']+'.png'))
			item.setLabel(app['name'])
			item.setInfo( type='video', infoLabels={'title': app['name']})
			item.setProperty('IsPlayable', 'false')
			xbmcplugin.addDirectoryItem(handle,uri % (app['name'],token),item,True)
		else:
			item=xbmcgui.ListItem(app['name'],iconImage='DefaultVideo.png', thumbnailImage=os.path.join(__thumbpath__, app['id']+'lock.png'))
			item.setLabel(app['name'])
			item.setInfo( type='video', infoLabels={'title': app['name']})
			item.setProperty('IsPlayable', 'false')
			xbmcplugin.addDirectoryItem(handle,sys.argv[0],item,True)

	item=xbmcgui.ListItem('recorded',iconImage='DefaultVideo.png', thumbnailImage=os.path.join(__thumbpath__, '5.png'))
	item.setLabel('recorded')
	item.setInfo( type='video', infoLabels={'title': 'recorded'})
	item.setProperty('IsPlayable', 'false')
	xbmcplugin.addDirectoryItem(handle,uri % ('recorded',token),item,True)

	xbmcplugin.endOfDirectory(handle,True,True)
	xbmc.executebuiltin('Container.SetViewMode(500)')

def ShowChannelsList(plugin, token):

	channels = plugin.full_channel_list(token);
	xbmc.PlayList(xbmc.PLAYLIST_VIDEO).clear()
	total_items = len(channels['data']['channels'])
	for channel in channels['data']['channels']:
		#if __settings__.getSetting('show_protected') == 'false':
		#	if channel['erotic'] == 1:
		#		continue
		uri = sys.argv[0] + '?mode=play&id=%s&title=%s&token=%s' % (channel['id'],channel['name'],token)
		xbmc.log('VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV LANGUAGE IS : %s' % LANGUAGE)
		if LANGUAGE == '1':
			channel_information = '[B]%s[/B]\r\n %s' % (channel['name'],channel['title_en'])
		else:
			channel_information = '[B]%s[/B]\r\n %s' % (channel['name'],channel['title_he'])
		if channel['status'] == 1:
			item=xbmcgui.ListItem(channel_information,iconImage='DefaultVideo.png', thumbnailImage=os.path.join(__thumbpath__, 'channels',channel['id']+'.png'))
		else:
			item=xbmcgui.ListItem(channel_information,iconImage='DefaultVideo.png', thumbnailImage=os.path.join(__thumbpath__, 'channels',channel['id']+'lock.png'))
		item.setProperty('IsPlayable', 'true')
		item.setProperty('channelId', channel['id'])
		item.setProperty('channelIcon', channel['icon'])
		item.setProperty('channelName', channel['name'])
		item.setInfo( type='video', infoLabels={'status' : 'LiveTV', 'title': channel['title_en'], 'plot': channel['desc_en'], 'overlay': channel['desc_en'], 'ChannelNumber': channel['id'], 'ChannelName': channel['name'], 'StartTime': '00:00', 'EndTime': '11:00'})
		if 'aspect_ratio' in channel and channel['aspect_ratio']:
			item.setProperty('AspectRatio', channel['aspect_ratio'])

		xbmcplugin.addDirectoryItem(handle,uri,item, False)

	xbmcplugin.setContent(handle, 'Movies')
	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin("Container.SetViewMode(51)")

def SelectGenresMovies(plugin, params, token):
	xbmc.log('Select genres screen initiated')
	glist = plugin.genres(token);

	for genre in glist['data']['genres']:
		item=xbmcgui.ListItem(genre['name'],iconImage='DefaultVideo.png', thumbnailImage=os.path.join(__thumbpath__, 'genres',genre['id']+'.png'))
		uri = sys.argv[0] + '?mode=movie_list&genre=%s&token=%s' % (genre['id'],token)
		xbmcplugin.addDirectoryItem(handle,uri,item,True)

	# add the option for search in Movies genre
	item=xbmcgui.ListItem(__language__(30049).encode('utf8'),iconImage='DefaultVideo.png', thumbnailImage=os.path.join(__thumbpath__, 'genres','79.png'))
	uri = sys.argv[0] + '?mode=search_keywords&app=movies&token=%s' % (token)
	xbmcplugin.addDirectoryItem(handle,uri,item,False)

	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin('Container.SetViewMode(500)')

def SelectGenresSeries(plugin, params, token):
	xbmc.log('Select genres screen initiated')
	glist = plugin.genres(token);

	for genre in glist['data']['genres']:
		item=xbmcgui.ListItem(genre['name'],iconImage='DefaultVideo.png', thumbnailImage=os.path.join(__thumbpath__, 'genres',genre['id']+'.png'))
		if int(genre['id']) == 1:
			uri = sys.argv[0] + '?mode=new_series&genre=%s&token=%s' % (1,token)
		else:
			uri = sys.argv[0] + '?mode=series_list&genre=%s&token=%s' % (genre['id'],token)
		xbmcplugin.addDirectoryItem(handle,uri,item,True)

	# add the option for search in Series genre
	item=xbmcgui.ListItem(__language__(30049).encode('utf8'),iconImage='DefaultVideo.png', thumbnailImage=os.path.join(__thumbpath__, 'genres','79.png'))
	uri = sys.argv[0] + '?mode=search_keywords&app=series&token=%s' % (token)
	xbmcplugin.addDirectoryItem(handle,uri,item,False)

	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin('Container.SetViewMode(500)')

def WatchTV(plugin, params, token):
	xbmc.log('params :::::: %s' % (params))
	channel_id = int(params['id'])
	url = plugin.get_url(channel_id,token)+'?token='+token
	xbmc.log('url is ::::::: %s' % (url))
	if url:
		xbmc.log('[%s] WatchTV: Opening channel %s as %s' % (PLUGIN_NAME, id, url))
		item=xbmcgui.ListItem(params['title'], path=url)
		item.setInfo( type='video', infoLabels={'title': params['title']})

		doVidInfo = False

		player = xbmc.Player()
		pls = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		xbmcplugin.setContent(handle, 'live')
		pls.clear()

		xbmc.executebuiltin("XBMC.PlayerControl(repeatall)")

		if handle == -1:
			xbmc.log('[%s] WatchTV: handle is -1, starting player' % (PLUGIN_NAME))
			if pls and pls.size():
				player.play(pls)
			else:
				player.play(url, item)
		else:
			xbmc.log('[%s] WatchTV: handle is %s, setting resolved url' % (PLUGIN_NAME, handle))
			xbmcplugin.setResolvedUrl(handle = handle, succeeded=True, listitem=item)

		if __settings__.getSetting('showcurrent') == 'true' and not gmt and doVidInfo:
			SetupInfoTimer()
			#xbmc.sleep(5000)
			#dialog = xbmcgui.Window(10142)
			#dialog.show()
	else:
		xbmc.executebuiltin("XBMC.Notification(" + __language__(30025).encode('utf8') + ", " + __language__(30025).encode('utf8') + ", 8000)");

def ListMovies(plugin, params,token):

	xbmc.log('Select ListMovies screen initiated')
	movielist = plugin.movie_list_genre(params['genre'],token)

	for movie in movielist['data']['genre']:
		icon = __base_url__ % movie['icon']
		item=xbmcgui.ListItem(movie['name'],iconImage=icon, thumbnailImage=icon)
		uri = sys.argv[0] + '?mode=playmovie&id=%s&title=%s&token=%s' % (movie['id'],movie['name'],token)
		xbmcplugin.addDirectoryItem(handle,uri,item,False)

	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin('Container.SetViewMode(500)')

def ListSeries(plugin, params,token):

	xbmc.log('Select ListSeries screen initiated')
	serieslist = plugin.series_list_genre(params['genre'],token)

	for series in serieslist['data']['seriesList']:
		icon = __base_url__ % series['icon']
		item=xbmcgui.ListItem(series['name'],iconImage=icon, thumbnailImage=icon)
		uri = sys.argv[0] + '?mode=season_list&id=%s&title=%s&token=%s' % (series['id'],series['name'],token)
		xbmcplugin.addDirectoryItem(handle,uri,item,True)

	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin('Container.SetViewMode(500)')

def ListnewSeries(plugin, params,token):

	xbmc.log('Select ListnewSeries screen initiated')
	serieslist = plugin.series_list_genre(params['genre'],token)

	for episode in serieslist['data']['seriesList']:

		icon = __base_url__ % episode['icon']
		name = 'S'+episode['season']+'/'+'E'+episode['episode']+' '+episode['name']
		item=xbmcgui.ListItem(name,iconImage=icon, thumbnailImage=icon)
		uri = sys.argv[0] + '?mode=playseries&id=%s&token=%s' % (episode['episode_id'],token)
		xbmcplugin.addDirectoryItem(handle,uri,item,False)

	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin('Container.SetViewMode(500)')

def ListSeasons(plugin, params,token):

	xbmc.log('Select ListSeasons screen initiated')
	seasonslist = plugin.series_seasons(params['id'],token)

	for season in seasonslist['data']['seasones']:
		icon = __base_url__ % season['icon']
		name = __language__(id=30047).encode('utf8')+' '+season['season']
		item=xbmcgui.ListItem(name,iconImage=icon, thumbnailImage=icon)
		uri = sys.argv[0] + '?mode=episode_list&id=%s&sid=%s&title=%s&token=%s' % (season['season'],params['id'],params['title'],token)
		xbmcplugin.addDirectoryItem(handle,uri,item,True)

	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin('Container.SetViewMode(500)')

def EpisodeList(plugin, params,token):

	xbmc.log('Select EpisodeList screen initiated')
	episodelist = plugin.series_list_season(params['sid'],params['id'],token)

	for episode in episodelist['data']['episodes']:
		icon = __base_url__ % episode['icon']
		name = __language__(id=30048).encode('utf8')+' '+episode['episode']
		item=xbmcgui.ListItem(name,iconImage=icon, thumbnailImage=icon)
		uri = sys.argv[0] + '?mode=playseries&id=%s&title=%s&token=%s' % (episode['episode_id'],params['title'],token)
		xbmcplugin.addDirectoryItem(handle,uri,item,False)

	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin('Container.SetViewMode(500)')

def SearchMovies(plugin, params,token):

	xbmc.log('Select SearchMovies screen initiated')
	movielist = plugin.moviesSearch(params['search'],token)
	for movie in movielist['data']['movies']:
		icon = __base_url__ % movie['icon']
		name = movie['name']
		item=xbmcgui.ListItem(name,iconImage=icon, thumbnailImage=icon)
		uri = sys.argv[0] + '?mode=playmovie&id=%s&title=%s&token=%s' % (movie['movie_id'],movie['name'],token)
		xbmcplugin.addDirectoryItem(handle,uri,item,False)

	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin('Container.SetViewMode(500)')

def SearchSeries(plugin, params,token):

	xbmc.log('Select SearchSeries screen initiated')
	serieslist = plugin.seriesSearch(params['search'],token)
	for series in serieslist['data']['series']:
		icon = __base_url__ % series['icon']
		item=xbmcgui.ListItem(series['name'],iconImage=icon, thumbnailImage=icon)
		uri = sys.argv[0] + '?mode=season_list&id=%s&title=%s&token=%s' % (series['id'],series['name'],token)
		xbmcplugin.addDirectoryItem(handle,uri,item,True)

	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin('Container.SetViewMode(500)')

def WatchMovie(plugin, params,token):

	movie_id = int(params['id'])
	url = plugin.movie_url(movie_id,token)+'?token='+token
	info = plugin.movie_info(movie_id,token)
	name = (info['name']).encode('utf-8')
	description = (info['description']).encode('utf-8')
	icon = __base_url__ % info['icon']
	item=xbmcgui.ListItem(name, path=url,iconImage=icon, thumbnailImage=icon)
	item.setIconImage(icon)
	item.setInfo( type='video', infoLabels={'Studio': name, 'title': name, 'plot': description, 'ChannelName': name})
	if handle == -1:
		xbmc.Player().play(url, item)
	else:
		xbmcplugin.setResolvedUrl(handle = handle, succeeded=True, listitem=item)
	xbmc.executebuiltin("XBMC.Notification(%s,%s,%d)" % (name,description,10))

def WatchSeries(plugin, params,token):

	series_id = int(params['id'])
	url = plugin.series_url(series_id,token)+'?token='+token
	info = plugin.series_info_episode_id(series_id,token)
	name = (info['name']).encode('utf-8')
	description = (info['description']).encode('utf-8')
	icon = __base_url__ % info['icon']
	item=xbmcgui.ListItem(params['title'], path=url,iconImage=icon, thumbnailImage=icon)
	item.setInfo( type='video', infoLabels={'Studio': name, 'title': name, 'plot': description, 'ChannelName': name})
	if handle == -1:
		xbmc.Player().play(url, item)
	else:
		xbmcplugin.setResolvedUrl(handle = handle, succeeded=True, listitem=item)
	xbmc.executebuiltin("XBMC.Notification(%s,%s,%d)" % (name,description,10))

def ShowRadioList(plugin, token):

	channels = plugin.radio_list(token);
	xbmc.PlayList(xbmc.PLAYLIST_VIDEO).clear()
	total_items = len(channels['data']['radio'])
	for channel in channels['data']['radio']:
		uri = sys.argv[0] + '?mode=playradio&id=%s&title=%s&token=%s' % (channel['radio_id'],channel['name'],token)
		item=xbmcgui.ListItem(channel['name']+'\n',iconImage='DefaultVideo.png', thumbnailImage=os.path.join(__thumbpath__, 'radio',channel['radio_id']+'.png'))
		item.setProperty('IsPlayable', 'true')
		item.setProperty('channelId', channel['radio_id'])
		item.setProperty('channelIcon', channel['icon'])
		item.setProperty('channelName', channel['name'])
		item.setInfo( type='radio', infoLabels={'status' : 'Radio', 'title': channel['name']})

		xbmcplugin.addDirectoryItem(handle,uri,item, False)

	xbmcplugin.setContent(handle, 'tvshows') # ex Radio
	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin("Container.SetViewMode(500)")

def PlayRadio(plugin, params,token):

	radio_id = int(params['id'])
	url = plugin.radio_url(radio_id,token)+'?token='+token
	info = plugin.radio_info(radio_id,token)
	name = (info['name']).encode('utf-8')
	description = (info['description']).encode('utf-8')
	icon = __base_url__ % info['icon']
	item=xbmcgui.ListItem(name, path=url, iconImage=icon, thumbnailImage=icon)
	item.setInfo( type='radio', infoLabels={'Studio': name, 'title': name, 'plot': description, 'ChannelName': name})
	if handle == -1:
		xbmc.Player().play(url, item)
	else:
		xbmcplugin.setResolvedUrl(handle = handle, succeeded=True, listitem=item)
	xbmc.executebuiltin("XBMC.Notification(%s,%s,%d)" % (name,description,10))
	xbmc.executebuiltin("Container.SetViewMode(504)")

def ShowRecordedChannelList(plugin, token):

	channels = plugin.channel_list(token);
	total_items = len(channels['data']['channels'])
	for channel in channels['data']['channels']:
		uri = sys.argv[0] + '?mode=channelepg7days&id=%s&token=%s' % (channel['id'],token)
		item=xbmcgui.ListItem(channel['name'],iconImage='DefaultVideo.png', thumbnailImage=os.path.join(__thumbpath__, 'channels',channel['id']+'.png'))
		item.setInfo( type='video', infoLabels={'status' : 'Recorded', 'title': channel['name']})

		xbmcplugin.addDirectoryItem(handle,uri,item, True)

	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin("Container.SetViewMode(500)")

def ChannelEpg7Days(plugin, params,token):

	epglist = plugin.epg7(token)
	for date in epglist['data']['epg']:
		name = '%s  %s' % (date['date_formatted'], date['day'])
		item=xbmcgui.ListItem(name,iconImage='DefaultVideo.png')
		uri = sys.argv[0] + '?mode=epgdatelist&id=%s&date=%s&token=%s' % (params['id'],date['date'],token)
		item.setProperty('IsPlayable', 'false')
		xbmcplugin.addDirectoryItem(handle,uri,item,True)

	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin('Container.SetViewMode(51)')

def EpgDateList(plugin,params,token):

	lang='he'
	if LANGUAGE == '1':
		lang='en'
	channels = plugin.epg(params['id'],params['date'],lang,token);
	xbmc.PlayList(xbmc.PLAYLIST_VIDEO).clear()
	total_items = len(channels['data']['epg'])
	__addon__ = xbmcaddon.Addon()
	__addonname__ = __addon__.getAddonInfo('name')
	for channel in channels['data']['epg']:
		uri = sys.argv[0] + '?mode=playrecorded&id=%s&recorded=%s&title=%s&token=%s' % (channel['id'],channel['recorded'],channel['title'],token)

		channel_information = '%s:%s - %s:%s         [B]%s[/B] \n %s' % (channel['begin'][8:10],channel['begin'][10:12],channel['end'][8:10],channel['end'][10:12],channel['title'].rstrip('\n'), channel['description'].rstrip('\n'))
		item=xbmcgui.ListItem(channel_information,iconImage='DefaultVideo.png', thumbnailImage=os.path.join(__thumbpath__, 'channels',channel['channel_id']+'.png'))
		item.setProperty('IsPlayable', 'true')
		item.setProperty('channelId', channel['id'])
		item.setInfo( type='video', infoLabels={'status' : 'Recorded', 'title': channel['title'],'ChannelNumber': channel['channel_id']})
		#xbmcgui.Dialog().ok(__addonname__, uri)
		xbmcplugin.addDirectoryItem(handle,uri,item, False, total_items)

	xbmcplugin.setContent(handle, 'files') # ex Recorded
	xbmcplugin.endOfDirectory(handle,True,False)
	xbmc.executebuiltin("Container.SetViewMode(51)")

def WatchRecorded(plugin, params,token):

	if params['recorded'] != '2':
		recorded_id = int(params['id'])
		url = plugin.recorded_url(recorded_id,token)+'?token='+token
		name=params['title']
		item=xbmcgui.ListItem(params['title'], path=url)
		item.setInfo( type='video', infoLabels={'title': params['title']})
		if handle == -1:
			xbmc.Player().play(url, item)
		else:
			xbmcplugin.setResolvedUrl(handle = handle, succeeded=True, listitem=item)

def SearchKeyWords(plugin, params,token):

	dialog = xbmcgui.Dialog()
	strActionInfo=dialog.input(__language__(id=30050).encode('utf8'), type=xbmcgui.INPUT_ALPHANUM)
	if params['app'] == 'movies':
		uri = sys.argv[0] + '?mode=search_movies&search=%s&token=%s' % (strActionInfo,token)
	elif params ['app'] == 'series':
		uri = sys.argv[0] + '?mode=search_series&search=%s&token=%s' % (strActionInfo,token)
	else:
		uri = sys.argv[0] + '?mode=%s&token=%s' % ('unknown',token)
	xbmc.executebuiltin('XBMC.Container.Update(%s)' % uri)



xbmc.log('[%s] Loaded' % (PLUGIN_NAME))
params = get_params()
PLUGIN_CORE = iptv.liveil(USERNAME, USERPASS, PARENTALCODE)

if 'mode' in params:
	mode = params['mode']
	token = params['token']

	if mode == 'live':
		ShowChannelsList(PLUGIN_CORE, token)

	elif mode == 'play':
		WatchTV(PLUGIN_CORE, params,token)

	elif mode == 'Settings':
		ProcessSettings(PLUGIN_CORE, params)

	elif mode == 'movies':
		SelectGenresMovies(PLUGIN_CORE, params,token)

	elif mode == 'movie_list':
		ListMovies(PLUGIN_CORE, params,token)

	elif mode == 'playmovie':
		WatchMovie(PLUGIN_CORE, params,token)

	elif mode == 'series':
		SelectGenresSeries(PLUGIN_CORE, params,token)

	elif mode == 'series_list':
		ListSeries(PLUGIN_CORE, params,token)

	elif mode == 'new_series':
		ListnewSeries(PLUGIN_CORE, params,token)

	elif mode == 'season_list':
		ListSeasons(PLUGIN_CORE, params,token)

	elif mode == 'episode_list':
		EpisodeList(PLUGIN_CORE, params,token)

	elif mode == 'playseries':
		WatchSeries(PLUGIN_CORE, params,token)

	elif mode == 'radio':
		ShowRadioList(PLUGIN_CORE, token)

	elif mode == 'playradio':
		PlayRadio(PLUGIN_CORE, params,token)

	elif mode == 'recorded':
		ShowRecordedChannelList(PLUGIN_CORE, token)

	elif mode == 'channelepg7days':
		ChannelEpg7Days(PLUGIN_CORE, params,token)

	elif mode == 'epgdatelist':
		EpgDateList(PLUGIN_CORE, params,token)

	elif mode == 'playrecorded':
		WatchRecorded(PLUGIN_CORE, params,token)

	elif mode == 'search_keywords':
		SearchKeyWords(PLUGIN_CORE, params,token)

	elif mode == 'search_series':
		SearchSeries(PLUGIN_CORE, params,token)

	elif mode == 'search_movies':
		SearchMovies(PLUGIN_CORE, params,token)

	else:
		ShowRoot(PLUGIN_CORE)
else:
	token = PLUGIN_CORE.testAuth()
	if token == None:
		xbmc.log('we DID NOT pass the testAuth')
		error_message = PLUGIN_CORE.error_message
		dialog = xbmcgui.Dialog()
		dialog.ok( __language__(30023), error_message)
		__settings__.openSettings()
	else:
		ShowRoot(PLUGIN_CORE,token)
		#ShowChannelsList(PLUGIN_CORE, token)
