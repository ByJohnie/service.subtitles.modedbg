# -*- coding: utf-8 -*-

from nsub import log_my, savetofile, list_key
from common import *

values = {'search': ''}
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'en-US,en;q=0.9,bg-BG;q=0.8,bg;q=0.7,ru;q=0.6',
'Connection': 'keep-alive',
'Host': 'bukvi.bg',
'Referer': 'http://bukvi.bg/',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}

url = 'http://bukvi.bg/index.php?'

def get_id_url_n(txt, list):
  soup = BeautifulSoup(txt, 'html5lib')
  # dump_src(soup, 'src.html')
  for links in soup.find_all("td", {"style": ["text-align: left;"]}):
    link = links.find('a', href=True)
    info = link.text#.split('/')[0]
    print info.encode('utf-8', 'replace')
    print link.text.encode('utf-8', 'replace')
    #yr = re.search('.*\((\d+)',link.text).group(1)
    
    list.append({'url': link['href'].encode('utf-8', 'replace'),
              'info': info.encode('utf-8', 'replace'),
              'year': '',
              'cds': '',
              'fps': '',
              'rating': '0.0',
              'id': __name__})
  return

def get_data(l, key):
  out = []
  for d in l:
    out.append(d[key])
  return out

def read_sub (mov):
  list = []

  values['search'] = mov
  #values['y'] = year

  enc_values = urllib.urlencode(values)
  log_my('Url: ', (url) +enc_values, 'Headers: ', (headers))

  request = urllib2.Request(url + enc_values.replace('%20','+'), None, headers)

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
  #if run_from_xbmc == False:
  for k in list_key:
      d = get_data(list, k)
      log_my(d)

  return list

def get_sub(id, sub_url, filename):
  s = {}
  headers['Referer'] = url
  request = urllib2.Request( 'http://bukvi.mmcenter.bg/load/0-0-0-' + sub_url.split("/")[-1] + '-20' , None, headers)
  response = urllib2.urlopen(request)
  log_my(response.code, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.code][0])
  s['data'] = response.read()
  s['fname'] = response.geturl().split("/")[-1]
  return s
