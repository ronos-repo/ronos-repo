# -*- coding: utf-8 -*-
import requests,re,urllib2,xbmcvfs,os,xbmc,xbmcaddon
from bs4 import BeautifulSoup
from net import Net


# Net
addon_id = xbmcaddon.Addon().getAddonInfo('id')
addon_profile_path = xbmc.translatePath(os.path.join(xbmc.translatePath('special://profile'), 'addon_data', addon_id))
if not os.path.exists(addon_profile_path):
    try: xbmcvfs.mkdirs(addon_profile_path)
    except: os.mkdir(addon_profile_path)
_cookie_file = xbmc.translatePath(os.path.join(xbmc.translatePath(addon_profile_path), 'cookies.txt'))

def _is_cookie_file(the_file):
    exists = os.path.exists(the_file)
    if not exists:
        return False
    else:
        try:
            tmp = xbmcvfs.File(the_file).read()
            if tmp.startswith('#LWP-Cookies-2.0'):
                return True
            return False
        except:
            with open(the_file, 'r') as f:
                tmp = f.readline()
                if tmp == '#LWP-Cookies-2.0\n':
                    return True
                return False


def _create_cookie(the_file):
    try:
        if xbmcvfs.exists(the_file):
            xbmcvfs.delete(the_file)
        _file = xbmcvfs.File(the_file, 'w')
        _file.write('#LWP-Cookies-2.0\n')
        _file.close()
        return the_file
    except:
        try:
            _file = open(the_file, 'w')
            _file.write('#LWP-Cookies-2.0\n')
            _file.close()
            return the_file
        except:
            return ''

if not _is_cookie_file(_cookie_file):
    _cookie_file = _create_cookie(_cookie_file)

net = Net(_cookie_file, cloudflare=True)

def myfile(url):
    r = requests.get(url)
    return re.compile("href=\\\(.*)onclick=").findall(r.text)[0].replace("'",'').replace('\\','').replace(' ','')

def linkbucksResolver(url):
    s = requests.session()
    s.headers = {'Host':'www.sasontnwc.net',
                 'Connection':'keep-alive',
                 'Referer':'http://www.sasontnwc.net/gunH',
                'Upgrade-Insecure-Requests':'1',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36'}
    r = s.get(url)
    r.encoding = 'utf-8'
    print r.text
    adurl = re.compile("Lbjs.TargetUrl \= '([^']+)'").findall(r.text)[0]
    token = re.compile("Token: '(.*)',").findall(r.text)[0]
    authKey = re.compile("'thKey'] = (.*);").findall(r.text)[0]
    print authKey
    preresolveurl = 'http://www.linkbucks.com/intermission/loadTargetUrl?t='+token+'&aK='+authKey+'&a_b=false'
    print preresolveurl
    print adurl
    r = s.get(preresolveurl)
    print r.text
  

        
def getSources(url):
    r =net.http_GET(url).content
    soup = BeautifulSoup(r,'html.parser')
    entry = soup.find('div',{'class':'entry'})
    links = entry.findAll('a')
    sourceList = []
    for link in links:
        linktext = link.text.lower()
        if 'myfile' in linktext or 'myflie' in linktext or 'videomega' in linktext or 'vidzi' in linktext:
            sourceList.append({'title':link.text,'url':link.get('href')})
    return sourceList
    
def getPosts(url):
    r = net.http_GET(url).content
    soup = BeautifulSoup(r,'html.parser')
    
    content = soup.find('div',{'id':'content'})
    posts = content.findAll('div',id=lambda x: x and x.startswith('post'))
    
    postList = []
    

    for post in posts:
        link = post.find('a')
        title = link.get('title').replace(u'להורדה','')
        url = link.get('href')
        image = net.url_with_headers(link.find('img').get('src').replace('-325x150',''))
        plot = post.find('p').text
        postList.append({'title':title,'url':url,'thumbnail':image,'plot':plot})
    

    try:
        next = content.find('div',{'class':'alignleft'}).find('a').get('href')
        if next != None:
            postList.append({'title':u'עמוד הבא','url':next})
    except:
        pass
    return postList

def getCategories():
    r = net.http_GET('http://www.multidown.me/').content
    soup = BeautifulSoup(r,'html.parser')
    cat = soup.find('li',{'class':'cat-item cat-item-1'})
    catSeries = soup.find('li',{'class':'cat-item cat-item-56'})
    catList = []
    for link in cat.findAll('a'):
        catList.append({'title':link.text,'url':link.get('href')})
    for link in catSeries.findAll('a'):
        catList.append({'title':link.text,'url':link.get('href')})
    return catList
