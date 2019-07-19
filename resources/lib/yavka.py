# -*- coding: utf-8 -*-

from nsub import log_my, savetofile, list_key
from common import *

values = {'s': '','y': '','u':'', 'l': 'BG','g': '', 'i': ''}

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'en-US,en;q=0.9,bg-BG;q=0.8,bg;q=0.7,ru;q=0.6',
'Connection': 'keep-alive',
'Host': 'yavka.net',
'Referer': 'http://yavka.net/subtitles.php',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}

url = 'http://yavka.net/'

def get_id_url_n(txt, list):
  soup = BeautifulSoup(txt, 'html5lib')
  # dump_src(soup, 'src.html')
  for link in soup.findAll("a", {"class": "selector"}): 
    info = link.text
    yr = link.find_next_sibling('span', text=True)
    yr = yr.text.replace('(','').replace(')','')
    fps = link.find_next_sibling('div', {"class": "right"}).getText()
    fps = fps[:7]
    fps = fps.replace(' ','').replace('\n','').replace('\t','')
    list.append({'url': link['href'].encode('utf-8', 'replace'),
              'info': info.encode('utf-8', 'replace'),
              'year': yr.encode('utf-8', 'replace'),
              'cds': '',
              'fps': fps.encode('utf-8', 'replace'),
              'rating': '0.0',
              'id': __name__})
  return

def get_data(l, key):
  out = []
  for d in l:
    out.append(d[key])
  return out

def read_sub (mov, year):
  list = []
  log_my(mov, year)

  values['s'] = mov
  values['y'] = year

  enc_values = urllib.urlencode(values)
  log_my('Url: ', (url), 'Headers: ', (headers), 'Values: ', (enc_values))

  request = urllib2.Request(url + 'subtitles.php?'+enc_values, enc_values, headers)

  response = urllib2.urlopen(request)
  log_my(response.code, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.code][0])

  if response.info().get('Content-Encoding') == 'gzip':
    buf = StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    data = f.read()
    f.close()
    buf.close()
  else:
    log_my('Error: ', response.info().get('Content-Encoding'))
    return None

  get_id_url_n(data, list)
  if run_from_xbmc == False:
    for k in list_key:
      d = get_data(list, k)
      log_my(d)

  return list

def get_sub(id, sub_url, filename):
  s = {}
  enc_values = urllib.urlencode(values)
  headers['Referer'] = url + '/subtitles.php'
  request = urllib2.Request(url + sub_url, enc_values, headers)
  response = urllib2.urlopen(request)
  log_my(response.code, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.code][0])
  s['data'] = response.read()
  s['fname'] = response.info()['Content-Disposition'].split('filename=')[1].strip('"')
  return s
