# -*- coding: utf-8 -*-

from nsub import log_my, savetofile, list_key
from common import *

values = {'q': '','type': 'downloads_file','search_and_or': 'or','search_in': 'titles','sortby': 'relevancy', 'csrfKey': ''}

headers = {
    'Upgrade-Insecure-Requests' : '1',
    'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
    'Content-Type' : 'application/x-www-form-urlencoded',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate',
    'Referer' : 'http://www.easternspirit.org/forum/index.php?/files/',
    'Accept-Language' : 'en-US,en;q=0.8'
}

url = 'http://www.easternspirit.org/forum'


def get_id_url_n(txt, list):
  soup = BeautifulSoup(txt, 'html5lib')
  for link in soup.find_all("span", class_="ipsContained ipsType_break"):
    #print link
    href = link.find('a', href=True)
    title = link.getText()
    title = re.sub('[\r\n]+','',title)
    yr =  re.search('.*\((\d+)',title).group(1)
    title = re.sub(' \(.*\s+','',title)
    
    list.append({'url': href['href'].encode('utf-8', 'replace'),
              'info': title.encode('utf-8', 'replace'),
              'year': yr.encode('utf-8', 'replace'),
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

  values['q'] = mov

  request = urllib2.Request(url, None, headers)
  response = urllib2.urlopen(request)
  if response.info().get('Content-Encoding') == 'gzip':
    buf = StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    data = f.read()
    f.close()
    buf.close()
  else:  
    data = response.read()
    response.close()
  csrfKey = re.search('input type="hidden" name="csrfKey" value="(.+?)"',data).group(1)
  values['csrfKey'] = csrfKey

  enc_values = urllib.urlencode(values)
  log_my('Url: ', (url)+ '/index.php?/search/&', 'Headers: ', (headers), 'Values: ', (enc_values))
  request = urllib2.Request(url + '/index.php?/search/&'+enc_values.replace('+','%20'), None, headers)

  response = urllib2.urlopen(request)
  log_my(response.code)


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
  request = urllib2.Request(sub_url, None, headers)
  response = urllib2.urlopen(request)
  mycook = response.info().get('Set-Cookie')
  if response.info().get('Content-Encoding') == 'gzip':
    buf = StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    data = f.read()
    f.close()
    buf.close()
  else:
    data = response.read()
    log_my('Error: ', response.info().get('Content-Encoding'))
  match = re.findall("<a href='(.+?)' class='ipsButton ipsButton_fullWidth", data)
  log_my(response.code, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.code][0])
  nexturl = match[0].replace('&amp;','&')
  dheaders = {
    'Upgrade-Insecure-Requests' : '1',
    'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
    'Content-Type' : 'application/x-www-form-urlencoded',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Referer' : 'http://www.easternspirit.org/forum/index.php?/files/',
    'Accept-Encoding' : 'gzip, deflate',
    'Accept-Language' : 'en-US,en;q=0.8',
    'Cookie': mycook,
    'Connection': 'keep-alive',
    'Referer': nexturl,
    'Host': 'www.easternspirit.org'
}
  s = {} 
  request = urllib2.Request(nexturl, None, dheaders)
  log_my(response.code, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.code][0])
  response = urllib2.urlopen(request)
  checker = response.info()['Content-Type']
  if checker == 'application/x-rar-compressed':
      s['data'] = response.read()
      s['fname'] = response.info()['Content-Disposition'].split('filename=')[1].strip('"')
  else:
    if response.info().get('Content-Encoding') == 'gzip':
      buf = StringIO(response.read())
      f = gzip.GzipFile(fileobj=buf)
      data = f.read()
      f.close()
      buf.close()
    else:
      data = response.read()
    data =  re.sub('[\r\n]+','',data)
    match = re.findall("'ipsType_break ipsContained'>[^<>]+<.+?a href='([^']+)'", data)
    for link in match:
        link = link.replace('&amp;','&')
        dheaders['Referer'] = link
        request = urllib2.Request(link, None, dheaders)
        log_my(response.code, BaseHTTPServer.BaseHTTPRequestHandler.responses[response.code][0])
        s['data'] = response.read()
        s['fname'] = response.info()['Content-Disposition'].split('filename=')[1].strip('"')   
  return s
