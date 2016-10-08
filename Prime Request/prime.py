"""
Script to Prime OWASP WebGoat App
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
parser = argparse.ArgumentParser(description='IMMUNIO WebGoat Priming Script.')
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
LESSON_N_REQUESTS = 2
INJECTION_N_REQUESTS = 50

for j in range(0,3):
    # Do basic request priming
    # For java we do more requests than necessary due to JIT compilation.
    # When the JIT kicks in it can alter stacks and context_keys, if we hit a route a couple of times
    # we cover the JIT and non-JIT cases.
    for lesson in LESSONS:
        priming(lesson['prime_url'], "undefined", SESSION_COOKIE, LESSON_N_REQUESTS)
    # Special case for the reflected XSS lesson
    lesson = find_lesson("Reflected XSS Attacks", LESSONS)
    url = "http://{domain}/WebGoat/attack?Screen={screen}&menu={menu}&QTY1=1&QTY2=1&QTY3=1&QTY4=1&field2=4128+3214+0002+1999&field1=script&SUBMIT=Purchase".format(
        domain = DOMAIN,
        screen = lesson["screen"],
        menu = lesson["menu"]
    )
    priming(url, "undefined", SESSION_COOKIE, INJECTION_N_REQUESTS)

    # Run all the lesson SQL queries

    # Numeric
    lesson = find_lesson("Numeric SQL Injection", LESSONS)
    url = "http://{domain}/WebGoat/attack?Screen={screen}&menu={menu}&station=101&SUBMIT=Go!".format(
        domain = DOMAIN,
        screen = lesson["screen"],
        menu = lesson["menu"]
    )
    priming(url, "undefined", SESSION_COOKIE, INJECTION_N_REQUESTS)

    # String
    lesson = find_lesson("String SQL Injection", LESSONS)
    url = "http://{domain}/WebGoat/attack?Screen={screen}&menu={menu}&account_name=Your+Name&SUBMIT=Go!".format(
        domain = DOMAIN,
        screen = lesson["screen"],
        menu = lesson["menu"]
    )
    priming(url, "undefined", SESSION_COOKIE, INJECTION_N_REQUESTS)

    # Blind Numeric
    lesson = find_lesson("Blind Numeric SQL Injection", LESSONS)
    url = "http://{domain}/WebGoat/attack?Screen={screen}&menu={menu}&account_number=101&SUBMIT=Go!".format(
        domain = DOMAIN,
        screen = lesson["screen"],
        menu = lesson["menu"]
    )
    priming(url, "undefined", SESSION_COOKIE, INJECTION_N_REQUESTS)

    # Blind String
    lesson = find_lesson("Blind String SQL Injection", LESSONS)
    url = "http://{domain}/WebGoat/attack?Screen={screen}&menu={menu}&account_number=101&SUBMIT=Go!".format(
        domain = DOMAIN,
        screen = lesson["screen"],
        menu = lesson["menu"]
    )
    priming(url, "undefined", SESSION_COOKIE, INJECTION_N_REQUESTS)

    # Command Injection
    lesson = find_lesson("Command Injection", LESSONS)
    url = "http://{domain}/WebGoat/attack?Screen={screen}&menu={menu}&HelpFile=AccessControlMatrix.help&SUBMIT=View".format(
        domain = DOMAIN,
        screen = lesson["screen"],
        menu = lesson["menu"]
    )
    priming(url, "undefined", SESSION_COOKIE, INJECTION_N_REQUESTS)

    # Special cases for lessons involving file access

    # "Bypass a Path Based Access Control Scheme"
    lesson = find_lesson("Bypass a Path Based Access Control Scheme", LESSONS)
    # prime with three files
    url1 = "http://{domain}/WebGoat/attack?Screen={screen}&menu={menu}&File=WeakSessionID.html&SUBMIT=View+File".format(
        domain = DOMAIN, screen = lesson["screen"], menu = lesson["menu"])
    url2 = "http://{domain}/WebGoat/attack?Screen={screen}&menu={menu}&File=DOMXSS.html&SUBMIT=View+File".format(
        domain = DOMAIN, screen = lesson["screen"], menu = lesson["menu"])
    url3 = "http://{domain}/WebGoat/attack?Screen={screen}&menu={menu}&File=Phishing.html&SUBMIT=View+File".format(
        domain = DOMAIN, screen = lesson["screen"], menu = lesson["menu"])
    for i in range(0,110):  # >300 requests
        priming(url1, "undefined", SESSION_COOKIE)
        priming(url2, "undefined", SESSION_COOKIE)
        priming(url3, "undefined", SESSION_COOKIE)

    # "Malicious File Execution"
    lesson = find_lesson("Malicious File Execution", LESSONS)
    url = "http://{domain}/WebGoat/attack?Screen={screen}&menu={menu}&myfile=prime.jpg&SUBMIT=Start+Upload&_={time}".format(
        domain = DOMAIN,
        screen = lesson["screen"],
        menu = lesson["menu"],
        time = str(datetime.datetime.now()).split('.')[0]
    )
    for i in range(0,400):  # >300 requests
        upload_file(url, "foo.html", SESSION_COOKIE)
        upload_file(url, "skynet.jpg", SESSION_COOKIE)

    # "ZipBomb"
    # lesson = find_lesson("ZipBomb", LESSONS)
    # url = "http://{domain}/WebGoat/attack?Screen={screen}&menu={menu}&myfile=prime.zip&SUBMIT=Start+Upload&_={time}".format(
    #     domain = DOMAIN,
    #     screen = lesson["screen"],
    #     menu = lesson["menu"],
    #     time = str(datetime.datetime.now()).split('.')[0]
    # )
    # for i in range(0,300):  # 300 requests
    #     upload_file(url, "foo.zip", SESSION_COOKIE)

print "\n[INFO] Priming Completed!"
