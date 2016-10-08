"""
Script to Demonstrate Some Attacks Against OWASP WebGoat App
"""
import io
import json
import urllib2
from urlparse import urlparse
import requests
import argparse
import sys
import datetime

DOMAIN = '127.0.0.1:8080'
SESSION_COOKIE = ''

def recurse_lessons(menu, lessons, domain):
    for rec in menu:
        if "children" in rec:
            recurse_lessons(rec["children"], lessons, domain)
        if rec["type"] == 'LESSON':
            parts = rec["link"].split("/")
            rec["screen"] = parts[1]
            rec["menu"] = parts[2]
            rec["prime_url"] = "http://{domain}/WebGoat/attack?Screen={screen}&menu={menu}".format(
                domain = domain, screen = parts[1], menu = parts[2]
            )
            lessons.append(rec)

def get_lesson_urls(domain, cookie):
    lessons = []
    menu_json = priming('http://'+domain+'/WebGoat/service/lessonmenu.mvc', 'undefined', cookie)
    menu = json.loads(menu_json)
    print menu
    recurse_lessons(menu, lessons, domain)
    return lessons

def find_lesson(name, lessons):
    for lesson in lessons:
        if lesson["name"] == name:
            return lesson

def get_cookie(domain):
    """Get Session Cookie"""
    headers = {'Content-type': 'application/x-www-form-urlencoded',
               'User-Agent': 'Mozilla/5.0'
              }
    url = 'http://'+domain+'/WebGoat/j_spring_security_check'
    form_data = {'username':'guest', 'password':'guest'}
    print "[INFO] Authenticating with Guest Credentials..."
    print "[INFO] Login URL: "+ url
    req = requests.post(url, headers=headers, data=form_data, allow_redirects=False)
    print req.headers['Set-Cookie']
    set_cookie = req.headers['Set-Cookie'].split(";")[0]
    print "[INFO] Got Cookie: " + set_cookie
    # send one last request. For some reason we need to do this to fix the session
    priming('http://'+DOMAIN+'/WebGoat/attack?Screen=500&menu=200', "undefined", set_cookie)

    return set_cookie

def upload_file(url, filename, cookie):
    """Upload File"""
    print("[INFO] " + url)
    cookie = cookie.split("=")
    cookies = {cookie[0]: cookie[1]}
    files = {'file': (filename, open('skynet.jpg', 'rb'), 'image/jpeg', {'Expires': '0'})}
    req = requests.post(url, files=files, cookies=cookies)

def priming(url, data, cookie, count=1):
    """Make Request"""
    for i in range(0, count):
        print("[INFO] " + url)
        if data == "undefined":
            request = urllib2.Request(url)
        else:
            request = urllib2.Request(url, data)
        request.add_header('User-Agent', 'Mozilla/5.0')
        request.add_header('Referer', url)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
        request.add_header('Cookie', cookie)
        contents = urllib2.urlopen(request).read()
        #print contents[0:500]
    return contents

parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='.')
parser.add_argument('-d', '--domain', help='The domain and port of the WebGoat instance to prime.')
parser.add_argument('-s', '--session', help='Optional JSESSIONID.')
args = parser.parse_args()
if args.domain:
    DOMAIN = args.domain
if args.session:
    SESSION_COOKIE = args.session
    SESSION_COOKIE = 'JSESSIONID=' + args.session

if SESSION_COOKIE == '':
    # Load all the lesson content
    SESSION_COOKIE = get_cookie(DOMAIN)

LESSONS = get_lesson_urls(DOMAIN, SESSION_COOKIE)

# Suspicious HTTP Header
url = "http://{domain}/WebGoat/".format(
    domain = DOMAIN,
)
cookie = SESSION_COOKIE.split("=")
cookies = {cookie[0]: cookie[1]}
# we look for a variety of suspicious header names and values. This is an example
headers = {"Acunetix-Product": "Acunetix vulnerability scanner"}
req = requests.get(url, files=files, cookies=cookies, headers=headers)

# Shellshock
headers = {"Shellshock-Example": "() { :; }; Shellshock"}
req = requests.get(url, files=files, cookies=cookies, headers=headers)

# Method Tampering
# We actually build a whitelist of VERBS that are OK for an application.
# However we never allow TRACE / TRACK as they are a known vuln in HTTP
req=requests.request('TRACE', url)

print "\n[INFO] Attacks Completed!"
