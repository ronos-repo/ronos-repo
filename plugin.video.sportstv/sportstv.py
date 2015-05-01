# -*- coding: utf-8 -*-
import urllib,urllib2,sys,re,os,base64,datetime,json
import xbmcaddon, xbmc, xbmcplugin, xbmcgui



def OPEN_URL(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    
    response = urllib2.urlopen(req,timeout=100)
    link=response.read()
    response.close()
    return link
def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty("IsPlayable","true")
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok
def addLink(name,url,iconimage,description):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
        liz.setProperty("IsPlayable","true")
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=False)

def INDEXpage(url,name):
	print url
	link=OPEN_URL(url)
	match=re.compile('embed.?(.*?)\?').findall(link)
	if match:
		match=match[-1]
		print str(match) + 'blabla'
		firstlink='http://youcloud.tv/player?streamname='+str(match)
		link=OPEN_URL(firstlink)
		
		match=re.compile('var a = (.*?);.*?var b = (.*?);.*?var c = (.*?);.*?var d = (.*?);.*?var f = (.*?);.*?var v_part = \'(.*?)\';',re.I+re.M+re.U+re.S).findall(link)
		print "winners are: " + str(match)
		match=match[0]
		a=int(match[0])/int(match[4])
		b=int(match[1])/int(match[4])
		c=int(match[2])/int(match[4])
		d=int(match[3])/int(match[4])
		v_part=match[5]
		final='rtmp://'+str(a)+'.'+str(b)+'.'+str(c)+'.'+str(d)+str(v_part)+' swfUrl=http://cdn.youcloud.tv/jwplayer.flash.swf live=1 timeout=15 swfVfy=1 pageUrl=http://youcloud.tv'
		print "winners are: " + str(match)
		listItem = xbmcgui.ListItem(name, iconImage = '', thumbnailImage = '', path=final)
		listItem.setInfo(type='Video',infoLabels={ "Title":name})
		listItem.setProperty('IsPlayable', 'true')
		xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listItem)
	else :
		dialog = xbmcgui.Dialog()
		ok = dialog.ok('sportTV', 'No SIGNAL ',"אין שידור באתר")
def INDEXmain():
	addDir('ספורט 1','http://www.goalim4u.me/p/blog-page_32.html',2,'http://msc.walla.co.il/w/w-248/354987-18.jpg')
	addDir('ספורט 2','http://www.goalim4u.me/p/2_9.html',2,'http://www.ynondigital.co.il/image/users/75596/ftp/my_files/LOGO/sport2.jpg?id=3463743')
	addDir('שידור משתנה','http://www.goalim4u.me/p/blog-page_19.html',2,'http://3.bp.blogspot.com/_gmZvC22iPv8/S_YIs9EbhHI/AAAAAAAAACM/8XtZc_AtrAo/s1600/football_logo.jpg')
	addDir('ONE','http://www.goalim4u.me/p/one.html',2,'http://images.one.co.il/images/MSites/2012/11/06/1415/onelogofb.jpg')
	addDir('ספורט 5','http://www.goalim4u.me/p/5_40.html',2,'http://www.sport5.co.il/Sip_Storage/FILES/7/size475x318/393677.jpg')
	addDir('5 GOLD','http://www.goalim4u.me/p/6_13.html',2,'http://www.the7eye.org.il/wp-content/uploads/2014/02/342342341.jpg')
	addDir('5+','http://www.goalim4u.me/p/5_96.html',2,'http://www.hot.net.il/UploadedImages//09_2013/5_Plus1.jpg')
	addDir('5 LIVE','http://www.goalim4u.me/p/5_13.html',2,'http://www.hot.net.il/UploadedImages/08_2010/5live_strip_1.jpg')
	addDir('Castv','http://youcloud.tv/castv1',2,'http://castv.net/images/logo.png')
	addDir('Nivdal 1','http://hd.nivdal.info/2014/04/s1.html',2,'http://i.vimeocdn.com/video/313173294_640.jpg')
	addDir('Nivdal 2','http://hd.nivdal.info/2014/04/s2.html',2,'http://i.vimeocdn.com/video/313173294_640.jpg')
	

def get_params():
        param=[]
        paramstring=sys.argv[2]
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
  
    
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "checkMode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
if mode==None or url==None or len(url)<1:
	INDEXmain()
elif mode==2:
	INDEXpage(url,name)
xbmcplugin.endOfDirectory(int(sys.argv[1]))