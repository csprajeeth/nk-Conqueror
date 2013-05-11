from init import *
from gamedata import *
from gameurls import *
from activity import *
from townhall import *
from diet import *
from character import Character
from home import Home
from gameplay import L0to1 as play_logic
from threading import Thread
from bs4 import BeautifulSoup

import market
import travel
import mechanize
import traceback
import urllib, urllib2, cookielib
import sys, time
import socks, socket


#call this first to patch a bug in mechanize 0.2.5 and below
monkeypatch_mechanize()


class NoHistory(object):
    def add(self, *a, **k): pass
    def clear(self): pass


def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
# patch the socket module
socket.socket = socks.socksocket
socket.create_connection = create_connection


def run(char, home):
    while True:
        try:
            play_logic(char,home)
            char.sleep_till_next_event()
        except:
            char.logger.write("\n"+log())
            traceback.print_exc(file = char.logger)
            time.sleep(10)
            char.login()


file = open("training_program")

for line in file.readlines():
    arr = line.strip().split(":")
    username = arr[0]
    if len(username) == 0 or username[0] == '#':
        continue
    password = arr[1]
    login_data =  urllib.urlencode({'login' : username, 'password' : password})
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    br = mechanize.Browser(factory=mechanize.RobustFactory(), history=NoHistory())
    br.set_cookiejar( mechanize.LWPCookieJar() )
    br.set_handle_refresh(False) 
    br.addheaders = [ ('User-agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'),
                      ('Accept-Language', 'en-US,en;q=0.8'),]
    logger = open('./logs/'+username, 'a', 0)
    print "Launching: " + username
    initialized = False
    while initialized == False:
        try:
            char = Character(username, password, br, opener, login_data, logger)
            home = Home(username, password, br,  opener, login_data, logger)
            initialized = True
        except:
            time.sleep(10)
    Thread(name = username, target = run, args = [char, home]).start()

    print "Waiting for 10 minutes"
    time.sleep(60*10)#for logging in using different TOR Exit nodes(IPs) wait for 10 minutes 

