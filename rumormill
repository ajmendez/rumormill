#!/usr/bin/env python

import os
import sys
import copy 
import mill
import twill
import urllib
import requests
import cookielib
from pprint import pprint
from bs4 import BeautifulSoup
from dateutil import parser
from operator import itemgetter
from pymendez.auth import auth


FACULTY = ('faculty' in sys.argv)
FULL = ('full' in sys.argv)
DEBUG = ('debug' in sys.argv)


PAGE_URL = 'http://www.astrobetter.com/wiki/tiki-pagehistory.php'
PARAMS = dict(
    page=r'Rumor+Mill',
    # diff_style='sidediff',
    diff_style='unidiff',
    compare='Compare',
    newver=0,
    oldver=0,
    paginate='off',
    history_offset=0,
    history_pagesize=25,
    show_all_versions='y',
)

DIRECTORY = os.path.expanduser('~/data/rumormill/')
if not os.path.exists(DIRECTORY):
    DIRECTORY = './'

NAME = 'postdoc_2014.json'
if FACULTY:
    NAME = 'faculty_2014.json'
    PARAMS['page'] = r'Rumor+Mill+Faculty-Staff'
FILENAME = os.path.join(DIRECTORY, NAME)


USERNAME,PASSWORD = auth('astrobetter',['username','password'])
# COOKIEFILE = os.path.expanduser('~/.limited/astrobetter_cookies.txt')
# COOKIES = cookielib.MozillaCookieJar(COOKIEFILE)
# COOKIES.load()
def login_cookies(username=USERNAME, password=PASSWORD):
    twill.commands.go(PAGE_URL)
    twill.commands.formaction('1', 'http://www.astrobetter.com/wiki/tiki-login.php')
    twill.commands.formclear('1')
    twill.commands.fv('1', 'user', username)
    twill.commands.fv('1', 'pass', password)
    twill.commands.submit('1')
    browser = twill.commands.get_browser()
    return browser._session.cookies
COOKIES = login_cookies()

def urlencode_withoutplus(query):
    '''Needed to encode the parameters safely for web url'''
    if hasattr(query, 'items'):
        query = query.items()
    l = []
    for k, v in query:
        k = urllib.quote(str(k), safe=' /+')
        v = urllib.quote(str(v), safe=' /+')
        l.append(k + '=' + v)
    return '?'+'&'.join(l)



def get_page(url=PAGE_URL, params=PARAMS, cookies=COOKIES):
    '''Grab the page with the global parameters'''
    result = requests.get(url+urlencode_withoutplus(params), cookies=cookies)
    result.soup = BeautifulSoup(result.text)
    print result.url
    return result

def get_version():
    '''Get the current version from the website.'''
    result = get_page()

    for item in result.soup.find_all('strong'):
        if 'Current' in item.text:
            for x in item.find_all('br'):
                x.insert_after('\n')
                x.extract()
            return int(item.text.split()[0])
    raise ValueError('Could not find version')

def setup_version():
    version = get_version()
    PARAMS['newver'] = version
    PARAMS['oldver'] = version - 1
    
def get_source(version):
    params = dict(
        page=PARAMS['page'],
        source=version,
    )
    result = get_page(params=params)
    return BeautifulSoup(result.text).find('textarea', {'id':'page_source'}).prettify()
    

def get_info(result):
    '''Get the info for the change'''
    soup = ( 
        result.soup.find('div', {'style':['text-align:center;']})
                   .find('table',{'class':'normal'})
                   .find('strong').findParents()[1]
    )
    items = [ # ensures ordering
        ['date',    parser.parse],
        ['user',    lambda x: str(x)],
        ['comment', lambda x: str(x)],
        ['version', lambda x: int(x.replace('Current',''))],
    ]
    out = {item:fcn(td.text.strip())
           for td,(item,fcn) in zip(soup.find_all('td'), items)}
    return out


def cleandiv(divstr):
    return (divstr.strip()
                  .replace(u'\xa0','')
                  .replace('\t','') )

def get_delta(result):
    soup = result.soup.find('table', {'class':['normal','diff']})
    out = []
    for bold in soup.find_all('strong'):
        bold.insert_after(u'*{}*'.format(bold.text.strip()))
        bold.extract()
    for div in soup.find_all('ins'):
        div.insert_after(div.text.strip())
        div.extract()
    for div in soup.find_all('del'):
        div.insert_after(div.text.strip())
        div.extract()
    
    for tmp in soup.find_all('td',{'colspan':'4'}):
        for div in tmp.find_all('div'):
            if div['class'][0] in ['diffheader','diffbody','diffdeleted','diffadded']:
                x = cleandiv(div.text)
                out.append(x)
                div.insert_after(x)
                div.extract()
    return out

def get_preview():
    PARAMS['preview'] = PARAMS['newver']
    result = get_page()
    PARAMS.pop('preview')
    return result.soup.find('div', {'class':'wikitext'}).prettify()

def get_change():
    result = get_page()
    if 'Versions are identical' in result.text:
        return 
    out = get_info(result)
    out['newver'] = PARAMS['newver']
    out['oldver'] = PARAMS['oldver']
    out['changes'] = get_delta(result)
    out['preview'] = get_preview()
    out['source'] = get_source(PARAMS['newver'])
    return out
    
def get_data():
    if DEBUG:
        get_change()
        return
    
    k=0
    with mill.Data(FILENAME) as data:
        while PARAMS['oldver'] > 0:
            if k > 3: break
            versions = [x.get('newver', 0) for x in data]
            if (PARAMS['newver'] in versions) and not FULL:
                print 'Done: {0[oldver]} {0[newver]}'.format(PARAMS)
            else:
                tmp = get_change()
                if tmp is None:
                    k += 1
                else:
                    data.data.append(tmp)
            PARAMS['oldver'] -= 1
            PARAMS['newver'] -= 1
        data.data = sorted(data.data, key=itemgetter('version'))
        return data.data



if __name__ == '__main__':
    from pysurvey import util
    util.setup_stop()
    
    setup_version()
    get_data()