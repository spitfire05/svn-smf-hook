#!/usr/bin/env python

# Copyright (c) 2014 Michal Borejszo michal@traal.eu
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# svn-smf-hook.py
#
# You can use this script as post-commit hook of your svn repo,
# and it'll announce each commit as new topic on selected boards,
# designed to work with Simple Machines Forums.
#
# Tested with SMF 2.0.6

import sys, os, urllib, urllib2, cookielib, time, fnmatch, urlparse, re, threading
import htmlentitydefs as entities
from xml.dom.minidom import parseString

###########
VERSION = 2
###########

# Default config values

USER = 'user'
PASSWORD = 'password'
FORUM_URL = 'http://example.com/index.php'
SVN_URL = 'svn://example.com/repo'
BOARD_MAIN = None
BOARD_SPEC = None
SPEC_CHAR = '!'
TIMEOUT = 60
MAX_LEN = 20000
EMPTY_MESSAGE = '[i]User did not write any message[/i]'
LOG_STDOUT = None
LOG_STDERR = None
PMS = None
PMS_URL = None

# Parse config
try:
    execfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'svn-smf-hook.conf'), globals())
except Exception, e:
    print >>sys.stderr, 'Failed to parse config file: ' + str(e)
    sys.exit(1)
if 'TRAC_URL' in globals() and PMS in (None, ''): # compatibility with older versions
    PMS = 'trac'
    PMS_URL = TRAC_URL

if LOG_STDOUT:
    try:
        sys.stdout = open(LOG_STDOUT, 'a')
    except Exception, e:
        print 'Failed to start stdout log at %s - %s' % (LOG_STDOUT, e)
if LOG_STDERR:
    try:
        sys.stderr = open(LOG_STDERR, 'a')
    except Exception, e:
        print 'Failed to start stderr log at %s - %s' % (LOG_STDERR, e)

actions = {
  'D': 'deleted ',
  'M': 'modified',
  'A': 'added   ',
  'R': 'replaced'
}

phpsessid = None
headers = None

class poster(threading.Thread):
    def set(self, bbcode, subject, is_beta):
        self.bbcode = bbcode
        self.subject = subject
        self.is_beta = is_beta
        
    def run(self):
        post_bbcode(self.bbcode, self.subject, self.is_beta)

def replace(org, rep, start, end):
    """
    Injects rep into org replacing characters from start to end.
    """
    org = org[:start] + rep + org[end:]
    return org
        
def fix_unicode(s):
    s = list(s)
    out = []
    for x in s:
      if ord(x) in entities.codepoint2name:
        out += [ '&' + entities.codepoint2name[ord(x)] + ';' ]
      else:
        out += x
    return ''.join(out)

def ticketBB(ticket):
    if PMS == 'trac':
        return '[url=' + PMS_URL + '/ticket/%s]%s[/url]' % (ticket[1:], ticket)
    elif PMS == 'redmine':
        return '[url=' + PMS_URL + '/issue/%s]%s[/url]' % (ticket[1:], ticket)
    else:
        return ticket

def actionBB(path, revision):
    if PMS == 'trac':
        return '  [url=' + PMS_URL + '/browser' + path.childNodes[0].nodeValue + '?rev=' + str(revision) + ']' + path.childNodes[0].nodeValue + '[/url]'
    elif PMS == 'redmine':
        return '  [url=' + PMS_URL + '/repository/changes' + path.childNodes[0].nodeValue + '?rev=' + str(revision) + ']' + path.childNodes[0].nodeValue + '[/url]'
    else:
        return path.childNodes[0].nodeValue

def post_bbcode(bbcode, subject, is_changelog_item):
    global phpsessid
    username = USER
    password = PASSWORD
    url_login = FORUM_URL
    url_post = FORUM_URL
    
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    
    def get_phpsessid():
        global phpsessid
        for c in cj:
            if c.name == 'PHPSESSID':
                phpsessid = c.value
    
    def login():
        global headers
        # First, GET request
        out = urllib2.urlopen(url_login + '?action=login')
        get_phpsessid()

        # POST request to login2
        host = urlparse.urlparse(FORUM_URL)[1]
        data = urllib.urlencode(
            {
                'user': username,
                'passwrd': password,
                'cookielength': '-1',
                'cookieneverexp': 'on'
            }
        )
        headers = {
            'Host': host,
            'Accept': "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
            'Accept-Charset': "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
            'Accept-Language': 'en-us;q=0.7,en;q=0.3',
            'Accept-Encoding': 'none',
            'Keep-Alive': '115',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11',
            'Referer': url_login + '?action=login',
            'DNT': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            };
        req = urllib2.Request(
            url_login + '?PHPSESSID=' + phpsessid + '&action=login2',
            data = data,
            headers = headers
        )
        out = urllib2.urlopen(req)
        assert '<span>%s</span>' % username in out.read(), 'login probably failed'
    
    def post_thread(forumid):
        def _do_post():
            global headers
            data = {
                'subject': subject,
                'message': bbcode,
                'topic': '0',
                'notify': '0',
                'lock': '0',
                'additional_options': '0',
                'icon': 'xx',
                'message_mode': '0',
                'goback': '1',
                'seqnum': seqnum,
            }
            data.update(sc)
            data = urllib.urlencode(data)
            headers['Referer'] = url_post + '?action=post;board=' + forumid
            req = urllib2.Request(
                url_post + '?action=post2;start=0;board=' + forumid, data = data,
                headers = headers
            )
            out = urllib2.urlopen(req)
            content = out.read()
            if 'Your session timed out while posting.' in content:
                # Try till it works, or till script time-out...
                _do_post()        

        # GET New topic page
        out = urllib2.urlopen(url_post + '?PHPSESSID=' + phpsessid + '&action=post;board=' + forumid)

        seqnum = None
        last = None
        sc = {}
        for line in out.readlines():
            if seqnum: break
            line = line.strip()
            if last and fnmatch.fnmatch(last, '<input type="hidden" *name="additional_options"*/>'):
                # we have sc here
                for x in line.split():
                    if x.startswith('value'):
                        v = x.replace('value=', '').replace('"', '')
                    if x.startswith('name'):
                        n = x.replace('name=', '').replace('"', '')
                sc[n] = v
            if fnmatch.fnmatch(line, '<input *name="seqnum" *value="*"*/>'):
                for x in line.split():
                    if x.startswith('value'):
                        seqnum = x.replace('value=', '').replace('"', '')
            last = line
        _do_post()
    
    login()
    if BOARD_MAIN:
        post_thread(BOARD_MAIN)
    if is_changelog_item and BOARD_SPEC:
        time.sleep(3) # sleep to by-pass SMF spambot detection
        post_thread(BOARD_SPEC)

def make_bbcode():
    assert len(sys.argv) == 3
    revision = int(sys.argv[2])

    f = os.popen('svn log --non-interactive --xml --verbose --revision ' + str(revision) + ' ' + SVN_URL)
    logxml = f.read()
    f.close()

    try:
      doc = parseString(logxml)
    except Exception, e:
      print 'failed to parse xml: ' + str(e)

    logmsg = doc.getElementsByTagName('logentry')[0]

    author = logmsg.childNodes[1]
    date = logmsg.childNodes[3]
    paths = logmsg.childNodes[5]
    msg = logmsg.childNodes[7]

    assert author.tagName == 'author'
    assert date.tagName == 'date'
    assert paths.tagName == 'paths'
    assert msg.tagName == 'msg'

    is_beta = False

    authortxt = author.childNodes[0].nodeValue

    if len(msg.childNodes) > 0:
      msgtxt = msg.childNodes[0].nodeValue
      lines = msgtxt.split('\n')
      for l in lines:
        if l.startswith(SPEC_CHAR): is_beta = True
      title = '[' + authortxt + '] ' + lines[0]
    else:
      msgtxt = EMPTY_MESSAGE
      title = None
    
    
    regexp = re.compile(r'(#\d+)(?!\[)(?![0-9])')
    m = regexp.search(msgtxt)
    while m:
        ticket = m.groups()[0]
        msgtxt = replace(
                        msgtxt,
                        ticketBB(ticket),
                        m.start(),
                        m.end()
                        )
        m = regexp.search(msgtxt)

    pathmsg = []

    changedfiles = 0
    for path in paths.childNodes:
      if hasattr(path, 'tagName'):
        assert path.tagName == 'path'
        changedfiles += 1
        pathmsg.append(actions[path.getAttribute('action')] + actionBB(path, revision))
    
    length = len('/n'.join(pathmsg))
    if length > MAX_LEN:
        pathmsg = ['[...lots of files...]']
    
    pathmsg.sort()
    
    if title is None:
      title = '[' + authortxt + '] ' + 'created revision ' + str(revision) + ' with ' + str(changedfiles) + ' changes'

    if PMS == 'trac':
        bbcode = """[b]""" + authortxt + """[/b] made revision [b][url=""" + PMS_URL + """/changeset/""" + str(revision) + """]""" + str(revision) + """[/url][/b] changing the following files:

[quote][tt]""" + '\n'.join(pathmsg) + """[/tt][/quote]

with the message:

[quote]""" + msgtxt + """[/quote]"""
    elif PMS == 'redmine':
        bbcode = """[b]""" + authortxt + """[/b] made revision [b][url=""" + PMS_URL + """/repository/revisions/""" + str(revision) + """]""" + str(revision) + """[/url][/b] changing the following files:

[quote][tt]""" + '\n'.join(pathmsg) + """[/tt][/quote]

with the message:

[quote]""" + msgtxt + """[/quote]"""
    else:
        bbcode = """[b]""" + authortxt + """[/b] made revision [b]""" + str(revision) + """[/b] changing the following files:

[quote][tt]""" + '\n'.join(pathmsg) + """[/tt][/quote]

with the message:

[quote]""" + msgtxt + """[/quote]"""
    bbcode = bbcode.encode('ascii', 'replace')
    title = title.encode('ascii', 'replace')
    return bbcode, title, is_beta

if __name__ == '__main__':    
    bbcode, subject, is_beta = make_bbcode()
    t = poster()
    t.daemon = True # daemon thread will be taken down when main thread finishes
    t.set(bbcode, subject, is_beta)
    t.start()
    t.join(TIMEOUT) # wait for maximum of TIMEOUT seconds for thread to finish, then proceed
