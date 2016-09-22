"""
Script to Prime OWASP WebGoat App
"""
import io
import json
import urllib2
from urlparse import urlparse
import requests

def get_prime_url(request_file):
    """GET Domain"""
    req_dat = []
    with io.open(request_file, mode='r', encoding="utf8", errors="ignore") as filp:
        req_line = filp.readline()
    req_dat = json.loads(req_line)
    parsed_uri = urlparse(req_dat["url"])
    return '{uri.netloc}'.format(uri=parsed_uri)

def get_cookie(domain):
    """Get Session Cookie"""
    headers = {'Content-type': 'application/x-www-form-urlencoded',
               'User-Agent': 'Mozilla/5.0'
              }
    url = 'http://'+domain+'/WebGoat/j_spring_security_check'
    form_data = {'username':'guest', 'password':'guest'}
    print "\n[INFO] Authenticating with Guest Credentials..."
    print "\n[INFO] Login URL: "+ url
    req = requests.post(url, headers=headers, data=form_data, allow_redirects=False)
    set_cookie = req.headers['Set-Cookie'].split(";")[0]
    return set_cookie

def upload_file(url, cookie):
    """Upload File"""
    cookie = cookie.split("=")
    cookies = {cookie[0]: cookie[1]}
    files = {'file': ('skynet.jpg', open('skynet.jpg', 'rb'), 'image/jpeg', {'Expires': '0'})}
    req = requests.post(url, files=files, cookies=cookies)
    print req.text

def priming(url, data, cookie):
    """Make Request"""
    if data == "undefined":
        request = urllib2.Request(url)
    else:
        request = urllib2.Request(url, data)
    request.add_header('User-Agent', 'Mozilla/5.0')
    request.add_header('Referer', url)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    request.add_header('Cookie', cookie)
    contents = urllib2.urlopen(request).read()
    print contents[0:500]

REQUESTS_FILE = 'prime.json'
DOMAIN = get_prime_url(REQUESTS_FILE)
SESSION_COOKIE = get_cookie(DOMAIN)

#Prime File Upload
FILE_UPLOAD_URL = 'http://'+DOMAIN+'/WebGoat/attack?Screen=2027530490&menu=1600'
upload_file(FILE_UPLOAD_URL, SESSION_COOKIE)

#Prime POST Requests
REQS = []
with io.open(REQUESTS_FILE, mode='r', encoding="utf8", errors="ignore") as f:
    REQS = f.readlines()
for req_data in REQS:
    json_req = json.loads(req_data)
    priming(json_req["url"], json_req["body"], SESSION_COOKIE)
print "\n[INFO] Priming Completed!"
