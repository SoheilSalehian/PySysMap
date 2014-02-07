#! /usr/bin/env python
"""
This module provides classes for querying Google Scholar and parsing
returned results. It currently *only* processes the first results
page. It is not a recursive crawler.
"""
# ChangeLog
# ---------
#
# 1.7:  Python 3 and BeautifulSoup 4 compatibility, as well as printing
#       of usage info when no options are given. Thanks to Pablo
#       Oliveira (https://github.com/pablooliveira)!
#
#       Also a bunch of pylinting and code cleanups.
#
# 1.6:  Cookie support, from Matej Smid (https://github.com/palmstrom).
#
# 1.5:  A few changes:
#
#       - Tweak suggested by Tobias Isenberg: use unicode during CSV
#         formatting.
#
#       - The option -c|--count now understands numbers up to 100 as
#         well. Likewise suggested by Tobias.
#
#       - By default, text rendering mode is now active. This avoids
#         confusion when playing with the script, as it used to report
#         nothing when the user didn't select an explicit output mode.
#
# 1.4:  Updates to reflect changes in Scholar's page rendering,
#       contributed by Amanda Hay at Tufts -- thanks!
#
# 1.3:  Updates to reflect changes in Scholar's page rendering.
#
# 1.2:  Minor tweaks, mostly thanks to helpful feedback from Dan Bolser.
#       Thanks Dan!
#
# 1.1:  Made author field explicit, added --author option.
#
# Don't complain about missing docstrings: pylint: disable-msg=C0111
#
# Copyright 2010--2013 Christian Kreibich. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Deprecated version of argparse
# @TODO: change to argparser at some point
import optparse
import sys
import re
from HTMLParser import HTMLParser

# For randomizing query wait times
from random import randint, choice
# For sleeping during queries
import time

# Global variable to keep track of start citations in order to parse the next page
nextStart = 0

try:
    # Try importing for Python 3
    # WWW fetch high level interface module
    from urllib.request import HTTPCookieProcessor, Request, build_opener
    from urllib.parse import quote
    # Cookie handling library
    from http.cookiejar import CookieJar
except ImportError:
    # Fallback for Python 2
    from urllib2 import Request, build_opener, HTTPCookieProcessor
    from urllib import quote
    from cookielib import CookieJar

# Import BeautifulSoup -- try 4 first, fall back to older
try:
    from bs4 import BeautifulSoup
except ImportError:
    try:
        from BeautifulSoup import BeautifulSoup
    except:
        print('We need BeautifulSoup, sorry...')
        sys.exit(1)

# Support unicode in both Python 2 and 3. In Python 3, unicode is str.
if sys.version_info[0] == 3:
    unicode = str # pylint: disable-msg=W0622
    encode = lambda s: s # pylint: disable-msg=C0103
else:
    encode = lambda s: s.encode('utf-8') # pylint: disable-msg=C0103

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


## @class Article
#  @brief A class representing articles listed on Google Scholar.  
#  The class provides basic dictionary-like behavior
class Article(object):
    
    ## @fn __init__(self)
    #  @brief default behavior of the article object
    #  @TODO: Add abstract as part of the default behavior 
    def __init__(self):
        self.attrs = {'title':         [None, 'Title',          0],
                      'url':           [None, 'URL',            1],
                      'num_citations': [0,    'Citations',      2],
                      'num_versions':  [0,    'Versions',       3],
                      'url_citations': [None, 'Citations list', 4],
                      'url_versions':  [None, 'Versions list',  5],
                      'abstract':      [None, 'Abstract',       6],
                      'year':          [None, 'Year',           6]}                      
    
    ## @fn __getitem__(self,key)
    #  @brief accessor function for the article class
    def __getitem__(self, key):
        if key in self.attrs:
            return self.attrs[key][0]
        return None
    
    ## @fn __len__(self,key)
    #  @brief accessor function to get the length of the attributes of the article class
    def __len__(self):
        return len(self.attrs)

    ## @fn __setitem__(self,key)
    #  @brief mutator function to change value for existing key or add key in case it's not in the attribute dictionary
    def __setitem__(self, key, item):
        if key in self.attrs:
            self.attrs[key][0] = item
        else:
            self.attrs[key] = [item, key, len(self.attrs)]
    
    ## @fn __setitem__(self,key)
    #  @brief mutator function to remove value for existing keys in the attricute dictionary 
    def __delitem__(self, key):
        if key in self.attrs:
            del self.attrs[key]
    
    ## @fn as_txt(self)
    #  @brief outputs the scrape results in txt format
    def as_txt(self):
        # Get items sorted in specified order:
        items = sorted(list(self.attrs.values()), key=lambda item: item[2])
        # Find largest label length:
        max_label_len = max([len(str(item[1])) for item in items])
        fmt = '%%%ds %%s' % max_label_len
        return '\n'.join([fmt % (item[1], item[0]) for item in items])

    ## @fn as_csv(self)
    #  @brief outputs the scrape results in csv format
    def as_csv(self, header=False, sep='|'):
        # Get keys sorted in specified order:
        keys = [pair[0] for pair in \
                sorted([(key, val[2]) for key, val in list(self.attrs.items())],
                       key=lambda pair: pair[1])]
        res = []
        if header:
            res.append(sep.join(keys))
        res.append(sep.join([unicode(self.attrs[key][0]) for key in keys]))
        return '\n'.join(res)

# @class ScholarParser
# @brief Class representing all the parser activities and attributes
# ScholarParser can parse HTML document strings obtained from Google Scholar. It invokes the handle_article() callback on each article
# that was parsed successfully.
class ScholarParser(object):
    # Site to envoke parsing activties on
    SCHOLAR_SITE = 'http://scholar.google.com'

    # @fn __init__(self,site)
    # @brief Default behaviors of the parser class
    def __init__(self, site=None):
        self.soup = None
        self.article = None
        self.site = site or self.SCHOLAR_SITE
        self.year_re = re.compile(r'\b(?:20|19)\d{2}\b')

    # @fn handle_article(self,art)
    # @brief base method that does nothing
    def handle_article(self, art):
        return
    
    # @fn parse(self,html)
    # @brief Main method that initiates the parsing of HTML content
    def parse(self, html):
        # instantiate the wrapper class for html parsing using the BeatifulSoup library..num..num!
        self.soup = BeautifulSoup(html)
        for div in self.soup.findAll(ScholarParser._tag_checker):
            self._parse_article(div)
            self._parse_abstract(div)

    def _parse_article(self, div):
        self.article = Article()

        for tag in div:
            if not hasattr(tag, 'name'):
                continue

            if tag.name == 'div' and self._tag_has_class(tag, 'gs_rt') and \
                    tag.h3 and tag.h3.a:
                self.article['title'] = ''.join(tag.h3.a.findAll(text=True))
                self.article['url'] = self._path2url(tag.h3.a['href'])
                


            if tag.name == 'font':
                for tag2 in tag:
                    if not hasattr(tag2, 'name'):
                        continue
                    if tag2.name == 'span' and self._tag_has_class(tag2, 'gs_fl'):
                        self._parse_links(tag2)

        if self.article['title']:
            self.handle_article(self.article)
    
    
    ## @fn _parse_links(self, span)
    ## @brief This function does the actual parsing of the html code at the low level for the links 
    def _parse_links(self, span):
        for tag in span:
            if not hasattr(tag, 'name'):
                continue
            if tag.name != 'a' or tag.get('href') == None:
                continue

            # Look into the citation link
            if tag.get('href').startswith('/scholar?cites'):
                if hasattr(tag, 'string') and tag.string.startswith('Cited by'):
                    # Parse the number of citations with some string casting to int
                    self.article['num_citations'] = \
                        self._as_int(tag.string.split()[-1])
                # Parse the url citations
                self.article['url_citations'] = self._path2url(tag.get('href'))
            
            # Look into the versions link
            if tag.get('href').startswith('/scholar?cluster'):
                if hasattr(tag, 'string') and tag.string.startswith('All '):
                    # Parse the number of versions
                    self.article['num_versions'] = \
                        self._as_int(tag.string.split()[1])
                # Parse the url path 
                # TODO: Later download scheme for the smaller window
                self.article['url_versions'] = self._path2url(tag.get('href'))
            
            

    ## @fn _tag_ has_class
    #  @brief A predicate static function that checks if tag instance has a class attribute
    @staticmethod
    def _tag_has_class(tag, klass):
        res = tag.get('class') or []
        if type(res) != list:
            # BeautifulSoup 3 can return e.g. 'gs_md_wp gs_ttss',
            # so split -- conveniently produces a list in any case
            res = res.split()
        return klass in res

    ## @fn _tag_checker
    #  @brief A static method to allow checking of tags without passing any arguments implicitely
    #  The method looks at the div tag 
    @staticmethod
    def _tag_checker(tag):
        return tag.name == 'div' and ScholarParser._tag_has_class(tag, 'gs_r')

    @staticmethod
    def _as_int(obj):
        try:
            return int(obj)
        except ValueError:
            return None

    def _path2url(self, path):
        if path.startswith('http://'):
            return path
        if not path.startswith('/'):
            path = '/' + path
        return self.site + path


class ScholarParser120201(ScholarParser):
    """
    This class reflects update to the Scholar results page layout that
    Google recently.
    """
    def _parse_article(self, div):
        self.article = Article()

        for tag in div:
            if not hasattr(tag, 'name'):
                continue

            if tag.name == 'h3' and self._tag_has_class(tag, 'gs_rt') and tag.a:
                self.article['title'] = ''.join(tag.a.findAll(text=True))
                self.article['url'] = self._path2url(tag.a['href'])

            if tag.name == 'div' and self._tag_has_class(tag, 'gs_a'):
                year = self.year_re.findall(tag.text)
                self.article['year'] = year[0] if len(year) > 0 else None

            if tag.name == 'div' and self._tag_has_class(tag, 'gs_fl'):
                self._parse_links(tag)

        if self.article['title']:
            self.handle_article(self.article)

## @class ScholarParser120726(ScholarParser)
#  @brief This class reflects update to the Scholar results page layout that
#         Google made 07/26/12.
class ScholarParser120726(ScholarParser):
    ## @fn _parse_article(self, div)
    #  @brief This method parses the article given its div(section) tag
    def _parse_article(self, div):
        # Instantiate an article class
        self.article = Article()
        
        # Step through the tags
        for tag in div:
            # If it doesn't have a name attribute continue
            if not hasattr(tag, 'name'):
                continue
            # Look for the actual "div" tag with "gs_ri" as google scholar's special div classes
            if tag.name == 'div' and self._tag_has_class(tag, 'gs_ri'):
                # Start parsing into the article, so the fun begins...
                # @TODO: if possible, here parse for the abstract as well
                if tag.a:
                    self.article['title'] = ''.join(tag.a.findAll(text=True))
                    self.article['url'] = self._path2url(tag.a['href'])
                    
                # More html division parsing based on google scholar's div classes
                if tag.find('div', {'class': 'gs_a'}):
                    year = self.year_re.findall(tag.find('div', {'class': 'gs_a'}).text)
                    self.article['year'] = year[0] if len(year) > 0 else None
                    
                # More html division parsing based on google scholar's div classes
                if tag.find('div', {'class': 'gs_fl'}):
                    self._parse_links(tag.find('div', {'class': 'gs_fl'}))
                

                # Parse for the abstract
                self.article['abstract'] = self._parse_abstract(tag)    

        if self.article['title']:
            self.handle_article(self.article)
            
    ## @fn _parse_abstract(self, tag)
    #  @brief This method parses the abstract based on the input with some html tag removal    
    def _parse_abstract(self, tag):
        if tag.find('div', {'class': 'gs_rs'}):
            # Parse the whole html abstract section
            abstract = ''.join(tag.findAll(text=True))
            # Strip the unecessary html tags
            abstract = strip_tags(abstract)
            # Remove unwanted artifacts
            abstract = abstract.replace("...", "")
            abstract = abstract.replace("\n", "")
            return abstract

## @class ScholarQuerier(object)
#  @brief The class parses the resulting html and returns articles to the article class
#  ScholarQuerier instances can conduct a search on Google Scholar 
#  with subsequent parsing of the resulting HTML content.  The
#  articles found are collected in the articles member, a list of Article instances.
class ScholarQuerier(object):
    SCHOLAR_URL = 'http://scholar.google.com/scholar?hl=en&q=%(query)s+author:%(author)s&btnG=Search&as_subj=eng&as_sdt=1,5&as_ylo=&as_vis=0'
    NOAUTH_URL = 'http://scholar.google.com/scholar?start=%(start)s&q=%(query)s&hl=en&as_sdt=0,5'
    #http://scholar.google.com/scholar?hl=en&q=%(query)s&btnG=Search&as_subj=eng&as_std=1,5&as_ylo=&as_vis=0'
    # Experimental URLs:
    #NOAUTH_URL = 'http://scholar.google.com/scholar?start=10&q=embedded+agile&hl=en&as_sdt=0,5'
    # Older URLs:
    # http://scholar.google.com/scholar?q=%s&hl=en&btnG=Search&as_sdt=2001&as_sdtp=on

    # Use many different agents to avoid being blocked by google
    USER_AGENT = ['Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9',\
                 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',\
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',\
                 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',\
                 'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14']

    ## @class Parser(ScholarParser120726)
    #  @brief The class parses the resulting html with inheritance from the parser class aligned 
    #  with latest version of the google page as of 12/07/26
    class Parser(ScholarParser120726):
        ## @fn __init__
        #  @brief Default behavior based on the default attributes of the parent class (at this point it is the ScholarParser120726)
        def __init__(self, querier):
            ScholarParser120726.__init__(self)
            # Instantiate the querier object
            self.querier = querier
        
        ## @fn handle_article(self,art)
        #  @brief Adds the article to the querier object
        def handle_article(self, art):
            self.querier.add_article(art)

    ## @fn __init__
    #  @brief Default behavior of the quierer class
    def __init__(self, author='', scholar_url=None, count=0):
        self.articles = []
        self.author = author
        # Clip to 100, as Google doesn't support more anyway
        self.count = min(count, 100)

        # If no other is passed on to, use the no author URL needed
        if author == '':
            self.scholar_url = self.NOAUTH_URL
        else:
            self.scholar_url = scholar_url or self.SCHOLAR_URL

        # Add the proper url extension with the count
        if self.count != 0:
            self.scholar_url += '&num=%d' % self.count

        # Instantiate a cookiejar object
        self.cjar = CookieJar()
        # Instantiate an opener object based on the list of handlers provided by the HTTPCookieProcessor class
        self.opener = build_opener(HTTPCookieProcessor(self.cjar))

    ## @fn query(self,search, start)
    #  @brief This method initiates a query with subsequent parsing of the response.
    def query(self, search, start):
        # Flush the articles
        self.clear_articles()
        
        # Construct the proper URL and calcuate the start
        url = self.scholar_url % {'query': quote(encode(search)), 'author': quote(self.author),\
                                  'start': start}
        # Add the agent
        # TODO: need to pick randomly from a list of User-Agents for each query
        req = Request(url=url, headers={'User-Agent': choice(self.USER_AGENT)})
        # Cookie handshake with response from the server
        hdl = self.opener.open(req)
        # Read the contents of the response
        html = hdl.read()
        # Parse the html
        self.parse(html)
    
    ## @fn parse(self,html)
    #  @brief This method allows parsing of existing HTML content
    #  This is done through initiating the parser method of the @class ScholarParser and 
    # the subsequent @fn _parse_article polymorphed instance
    def parse(self, html):
        parser = self.Parser(self)
        parser.parse(html)
    
    ## @fn add_article
    #  @brief Method to append articles
    def add_article(self, art):
        self.articles.append(art)

    ## @fn clear_articles
    #  @brief Clears any existing articles stored from previous queries.
    def clear_articles(self):
        self.articles = []

     
## @fn txt(query, author, count)
#  @brief Function that queries and prints the text format 
def txt(query, author, count):
    global nextStart
    # Instantiate the querier class with author and count as arguments
    querier = ScholarQuerier(author=author, count=count)
    # Make the actual query
    querier.query(query, nextStart)
    # Grab the articles
    articles = querier.articles
    # Setup based on count given to print
    if count > 0:
        articles = articles[:count]
    # Iterate through articles and print them as text
    for art in articles:
        print(art.as_txt() + '\n')

## @fn recursiveQueryTxt(query, author, count, recursiveCount)
#  @brief This function recursively queries and outputs in txt format
#  The function uses @var recursiveCount which translates to the number of pages that will be queried
def recursiveQueryTxt(query, author, count, recursiveCount):
    global nextStart
    # Recursively do the query based on @var recursiveCount provided
    for i in xrange(0,recursiveCount):
        # Txt based query
        txt(query, author, count)
        # Random waits between queries
        time.sleep(randint(4,10))
        # Set up the nextStart for the next query
        nextStart += count
        # Print out messages for future pa
        #print "<scholar> Page:", i+1, "<\scholar>"
        i += 1
        
## @fn csv(query, author, count)
#  @brief Function that queries and prints the csv format 
def csv(query, author, count, header=False, sep='|'):
    global nextStart
    querier = ScholarQuerier(author=author, count=count)
    nextStart += count
    querier.query(query, nextStart)
    articles = querier.articles
    if count > 0:
        articles = articles[:count]
    for art in articles:
        result = art.as_csv(header=header, sep=sep)
        print(encode(result))
        header = False

## @fn recursiveQueryCsv(query, author, count, recursiveCount, header=False)
#  @brief This function recursively queries and outputs in csv format
#  The function uses @var recursiveCount which translates to the number of pages that will be queried
def recursiveQueryCsv(query, author, count, recursiveCount, header=False):
    global nextStart
    # Recursively do the query based on @var recursiveCount provided
    for i in xrange(0,recursiveCount):
        # Txt based query
        csv(query, author, header, count)
        # Random waits between queries
        time.sleep(randint(4,10))
        # Set up the nextStart for the next query
        nextStart += count
        # Print out debug messages 
        #print "<scholar> Page:", i+1, "<\scholar>"
        i += 1

def main():
    usage = """scholar.py [options] <query string>
A command-line interface to Google Scholar.

Example: scholar.py -c 1 --txt --author einstein quantum"""

    fmt = optparse.IndentedHelpFormatter(max_help_position=50, width=100)
    parser = optparse.OptionParser(usage=usage, formatter=fmt)
    parser.add_option('-a', '--author',
                      help='Author name')
    parser.add_option('--csv', action='store_true',
                      help='Print article data in CSV form (separator is "|")')
    parser.add_option('--csv-header', action='store_true',
                      help='Like --csv, but print header with column names')
    parser.add_option('--txt', action='store_true',
                      help='Print article data in text format')
    parser.add_option('-c', '--count', type='int',
                      help='Maximum number of results')
    parser.add_option('-p','--pages', type='int',
                      help='Number of pages to query based')
    parser.set_defaults(count=0, author='')
    options, args = parser.parse_args()

    # Show help if we have neither keyword search nor author name
    if len(args) == 0 and options.author == '':
        parser.print_help()
        return 1

    query = ' '.join(args)

    if options.csv:
        recursiveQueryCsv(query, author=options.author, count=options.count, recursiveCount=options.pages, header=False)
    elif options.csv_header:
        recursiveQueryCsv(query, author=options.author, count=options.count, recursiveCount=options.pages, header=True)
    else:
        recursiveQueryTxt(query, author=options.author, count=options.count, recursiveCount=options.pages)

    return 0

if __name__ == "__main__":
    sys.exit(main())
