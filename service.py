# -*- coding: utf-8 -*-

import os
import sys
import re
import xbmc
import urllib
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import unicodedata
import simplejson as j
import requests

__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__icon__       = unicode(__addon__.getAddonInfo('icon'), 'utf-8')
__language__   = __addon__.getLocalizedString

__cwd__        = unicode(xbmc.translatePath( __addon__.getAddonInfo('path')), 'utf-8')
__profile__    = unicode(xbmc.translatePath( __addon__.getAddonInfo('profile')), 'utf-8')
__resource__   = unicode(xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' )), 'utf-8')
__temp__       = unicode(xbmc.translatePath( os.path.join( __profile__, 'temp', '')), 'utf-8')
__name_dict__  = unicode(xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib', 'dict.json' )), 'utf-8')
player = xbmcaddon.Addon().getSetting('player')
rarfile = unicode(xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib', 'rarfile' )), 'utf-8')
unrar1 = unicode(xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib', 'unrar' )), 'utf-8')
sys.path.append (__resource__)
import nsub
from nsub import list_key, log_my, read_sub, get_sub, get_info, select_1
nsub.path = __temp__

def namesubst(str):
  with open(__name_dict__, 'rb') as fd:
    namesubst = j.loads(fd.read())
    return namesubst.get(str, str)

def Notify (msg1, msg2):
  xbmc.executebuiltin((u'Notification(%s,%s,%s,%s)' % (msg1, msg2, '10000', __icon__)).encode('utf-8'))

def rmtree(path):
  if isinstance(path, unicode):
    path = path.encode('utf-8')

  dirs, files = xbmcvfs.listdir(path)

  for dir in dirs:
    rmtree(os.path.join(path, dir))

  for file in files:
    xbmcvfs.delete(os.path.join(path, file))

  xbmcvfs.rmdir(path)

def Search(item):
  it = []
  _item = dict(item)
  it.append(item)
  _item['title'], _item['year'] = xbmc.getCleanMovieTitle( item['title'] )
  it.append(_item)

  sub_data = read_sub(*it)
  #### Do whats needed to get the list of subtitles from service site
  #### use item["some_property"] that was set earlier
  #### once done, set xbmcgui.ListItem() below and pass it to xbmcplugin.addDirectoryItem()
  if sub_data != None:
    log_my(sub_data)
    for it in sub_data:
      listitem = xbmcgui.ListItem(label="Bulgarian",               # language name for the found subtitle
                                label2=get_info(it),               # file name for the found subtitle
                                iconImage=str(int(round(float(it['rating'])))), # rating for the subtitle, string 0-5
                                thumbnailImage="bg"          # language flag, ISO_639_1 language + gif extention, e.g - "en.gif"
                                )

      listitem.setProperty( "sync",        '{0}'.format("false").lower() )  # set to "true" if subtitle is matched by hash,
                                                                         # indicates that sub is 100 Comaptible

      listitem.setProperty( "hearing_imp", '{0}'.format("false").lower() ) # set to "true" if subtitle is for hearing impared


      ## below arguments are optional, it can be used to pass any info needed in download function
      ## anything after "action=download&" will be sent to addon once user clicks listed subtitle to downlaod
      url = "plugin://%s/?action=download&link=%s&ID=%s&filename=%s" % (__scriptid__,
                                                                      it['url'],
                                                                      it['id'],
                                                                      "filename of the subtitle")
      ## add it to list, this can be done as many times as needed for all subtitles found
      xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)

    Notify('Server', 'ok')
  else:
    Notify('Server', 'error')

def IsSubFile(file):
  exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass" ]
  filename = os.path.basename(file.lower())
  name, ext = os.path.splitext(filename)
  if ext not in exts: return False
  if ext != ".txt": return True
  # Check for README text files
  readme = re.search(ur'subsunacs\.net|subs\.sab\.bz|танете част|прочети|^read ?me|procheti|UNACS|- README|...UNACS|README|READ', name, re.I)
  return readme == None

def appendsubfiles(subtitle_list, basedir, files):
  for file in files:
    file = os.path.join(basedir, file.decode("utf-8"))
    if os.path.isdir(file.encode('utf-8')):
      dirs2, files2 = xbmcvfs.listdir(file.encode('utf-8'))
      files2.extend(dirs2)
      appendsubfiles(subtitle_list, file, files2)
    elif IsSubFile(file):
      subtitle_list.append(file.encode('utf-8'))

def Download(id,url,filename, stack=False):
  subtitle_list = []
  ## Cleanup temp dir, we recomend you download/unzip your subs in temp folder and
  ## pass that to XBMC to copy and activate
  if xbmcvfs.exists(__temp__):
    try:
      rmtree(__temp__)
    except:
      Notify('Error cleanup', 'error')
      pass
  xbmcvfs.mkdirs(__temp__)

  log_my('Download from id', url)
  sub=get_sub(id, url, filename)

  if (sub.has_key('data') and sub.has_key('fname')):
    log_my('{0}'.format(sub['fname']),'saving')
    ff = os.path.join(__temp__, sub['fname'])
    subFile = xbmcvfs.File(ff, 'wb')
    subFile.write(sub['data'])
    subFile.close()
    xbmc.sleep(500)
    if '0' in player:
     kodi_major_version = int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])
     if 'rar' in ff and kodi_major_version >= 18:
      src = 'archive' + '://' + urllib.quote_plus(ff) + '/'
      (cdirs, cfiles) = xbmcvfs.listdir(src)
      for cfile in cfiles:
        fsrc = '%s%s' % (src, cfile)
        xbmcvfs.copy(fsrc, __temp__ + cfile)
     else:
      xbmc.executebuiltin(('XBMC.Extract("%s","%s")' % (ff,__temp__,)).encode('utf-8'), True)
    if '1' in player:
      if 'zip' in ff:
       xbmc.executebuiltin(('XBMC.Extract("%s","%s")' % (ff,__temp__,)).encode('utf-8'), True)
      else:
       app      = 'com.rarlab.rar'
       intent   = 'android.intent.action.VIEW'
       dataType = 'application/rar'
       dataURI  = ff
       arch = 'StartAndroidActivity("%s", "%s", "%s", "%s")' % (app, intent, dataType, dataURI)
       xbmc.executebuiltin(arch)
       #xbmc.executebuiltin('XBMC.StartAndroidActivity("com.rarlab.rar","android.intent.action.SEND","application/rar",ff)')
    if '2' in player:
      import rarfile
      if 'rar' in ff:
       archive = rarfile.RarFile(ff)
       archive.extract(__temp__)
      else:
       xbmc.executebuiltin(('XBMC.Extract("%s","%s")' % (ff,__temp__,)).encode('utf-8'), True)
    if '3' in player:
      import rarfile
      if 'rar' in ff:
       archive = rarfile.RarFile(ff)
       archive.extract(__temp__)
      else:
       xbmc.executebuiltin(('XBMC.Extract("%s","%s")' % (ff,__temp__,)).encode('utf-8'), True)
    if '4' in player:
      if 'rar' in ff:
        if 'subsunacs' in ff:
         xbmcvfs.delete(ff)
         headers = {
            "Host": "subsunacs.net",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
          }
         url = 'https://subsunacs.net' + url + '!'
         print url
         req = requests.get(url, headers=headers)
         match = re.compile('<a href="(.+?)">(.+?)</a></label><label').findall(req.text)
         for suburl, subname in match:
          subname = subname.encode('cp1251', 'ignore').decode('cp1251', 'ignore').encode('utf-8', 'ignore').replace(' ','.')
          #subname = subname.encode('utf-8')
          subtitri = __temp__+subname
          try:
            url2 = 'https://subsunacs.net' + suburl
            req2 = requests.get(url2, headers=headers)
            f = open(subtitri, 'wb')
            f.write(req2.content)
            f.close()
            xbmc.sleep(1000)
          except:
            pass
        if 'subs.sab.bz' in ff:
         kodi_major_version = int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])
         if kodi_major_version >= 18:
          src = 'archive' + '://' + urllib.quote_plus(ff) + '/'
         (cdirs, cfiles) = xbmcvfs.listdir(src)
         for cfile in cfiles:
          fsrc = '%s%s' % (src, cfile)
          xbmcvfs.copy(fsrc, __temp__ + cfile) 
      else:
       xbmc.executebuiltin(('XBMC.Extract("%s","%s")' % (ff,__temp__,)).encode('utf-8'), True) 
    #xbmc.executebuiltin(('XBMC.Extract("%s","%s")' % (ff,__temp__,)).encode('utf-8'), True)
    Notify('{0}'.format(sub['fname']),'load')
    if '1' in player:
      xbmc.sleep(10000)
      dirs, files = xbmcvfs.listdir(__temp__)
      files.extend(dirs)
      appendsubfiles(subtitle_list, __temp__, files)

      if len(subtitle_list) >= 2:
       subtitle_list = select_1(subtitle_list)
      if xbmcvfs.exists(subtitle_list[0]):
       return subtitle_list

    else:
     dirs, files = xbmcvfs.listdir(__temp__)
     files.extend(dirs)
     appendsubfiles(subtitle_list, __temp__, files)

     if len(subtitle_list) >= 2:
       subtitle_list = select_1(subtitle_list)
     if xbmcvfs.exists(subtitle_list[0]):
       return subtitle_list

  else:
    Notify('Error','downlod subtitles')
    return []

def normalizeString(str):
  return unicodedata.normalize(
         'NFKD', unicode(unicode(str, 'utf-8'))
         ).encode('ascii','ignore')

def get_params():
  param=[]
  paramstring=sys.argv[2]
  if len(paramstring)>=2:
    params=paramstring
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

params = get_params()

if params['action'] == 'search' or params['action'] == 'manualsearch':
  item = {}
  item['temp']               = False
  item['rar']                = False
  item['year']               = xbmc.getInfoLabel("VideoPlayer.Year")                           # Year
  item['season']             = str(xbmc.getInfoLabel("VideoPlayer.Season"))                    # Season
  item['episode']            = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                   # Episode
  item['tvshow']             = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))   # Show
  item['title']              = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle")) # try to get original title
  item['file_original_path'] = urllib.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))  # Full path of a playing file
  item['3let_language']      = []

  if 'searchstring' in params:
    item['mansearch'] = True
    item['mansearchstr'] = urllib.unquote(params['searchstring'])
  else:
    item['mansearch'] = False

  for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
    item['3let_language'].append(xbmc.convertLanguage(lang,xbmc.ISO_639_2))

  if item['title'] == "":
    item['title']  = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))

  if item['tvshow']:
    item['tvshow'] = namesubst(item['tvshow'])
    # Remove the year from some tv show titles
    # NOTE: do not use the year for tv shows as it may cause wrong results
    item['year'] = ''
    tvshmatch = re.match(r'(.+) \((\d{4})\)$', item['tvshow'])
    if tvshmatch and len(tvshmatch.groups()) == 2:
      item['tvshow'] = tvshmatch.group(1)

  # Check if season is "Special"
  special_index = item['episode'].lower().find("s")
  if special_index > -1:
    item['season'] = "0"
    item['episode'] = item['episode'][special_index+1:]

  if ( item['file_original_path'].find("http") > -1 ):
    item['temp'] = True

  elif ( item['file_original_path'].find("rar://") > -1 ):
    item['rar']  = True
    item['file_original_path'] = os.path.dirname(item['file_original_path'][6:])

  elif ( item['file_original_path'].find("stack://") > -1 ):
    stackPath = item['file_original_path'].split(" , ")
    item['file_original_path'] = stackPath[0][8:]
  Search(item)

elif params['action'] == 'download':
  ## we pickup all our arguments sent from def Search()
  if '1' in player:
   subs = Download(params["ID"],params["link"],params["filename"])
   xbmc.sleep(5000)
   ## we can return more than one subtitle for multi CD versions, for now we are still working out how to handle that in XBMC core
   for sub in subs:
    listitem = xbmcgui.ListItem(label=sub)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sub,listitem=listitem,isFolder=False)
  else:
    subs = Download(params["ID"],params["link"],params["filename"])
   ## we can return more than one subtitle for multi CD versions, for now we are still working out how to handle that in XBMC core
    for sub in subs:
     listitem = xbmcgui.ListItem(label=sub)
     xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sub,listitem=listitem,isFolder=False)
xbmcplugin.endOfDirectory(int(sys.argv[1])) ## send end of directory to XBMC
