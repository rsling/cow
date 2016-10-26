#!/usr/bin/python

# This scripts adds document IDs and sentence IDs.
# It also tries to guess if a document is a forum discussion.
# Input format: COW-xml, one token per line, all xml markup on separate lines

import sys
import codecs
import random
import hashlib
import re

id_re = re.compile('.*id="([^"]+)"')
url_re = re.compile('.*url="([^"]+)"')

#forum_re = re.compile('.*(?:forum|/board/|/threads/|showthread|/archive/(?:index.php/)?t-[0-9]+\.html|viewtopic|ftopic|/\?topic=|/(?:[0-9]+-[A-Za-z]+(?:-[A-Za-z]+)+\.html)|(?:/threads/[A-Za-z]+(?:-[A-Za-z]+)+\.[0-9]+/$)|/thread-[0-9]+\.html$|/topic/[0-9]+(?:-[A-Za-z]+)+|/t[0-9]+(?:-[A-Za-z]\+)+\.html)')

# These are not always forums and need double checking:
# grep '/(?:[0-9]+-[A-Za-z]+(?:-[A-Za-z]+)+\.html)'

forum_re = re.compile('.*(?:forum|/board/|/threads/|showthread|/archive/(?:index.php/)?t-[0-9]+\.html|viewtopic|ftopic|/\?topic=|(?:/threads/[A-Za-z]+(?:-[A-Za-z]+)+\.[0-9]+/$)|/thread-[0-9]+\.html$|/topic/[0-9]+(?:-[A-Za-z]+)+|/t[0-9]+(?:-[A-Za-z]\+)+\.html)')


def get_id(docstartstring):
    docid = id_re.match(docstartstring).group(1)
    return(docid)

def checkforum(line):
    url = re.match(url_re, line).group(1)
    if re.match(forum_re, url):
	return("forum")
    else:
	return('unknown')


def mk_new_docstartstring(old_docstartstring, texttype):
    first = re.sub('> *$', ' ', old_docstartstring)
#    first =  old_docstartstring.replace('>', ' ')
    new_docstartstring =  first + 'texttype="' + texttype + '">'
    return(new_docstartstring)




def main():
	UTF8Reader = codecs.getreader('utf8')                                                                                
        sys.stdin = UTF8Reader(sys.stdin)                                                                                                                     
        UTF8Writer = codecs.getwriter('utf8')                                                                                
        sys.stdout = UTF8Writer(sys.stdout) 
	
	#infile = codecs.open(sys.argv[1], 'r', 'utf-8')
	doccounter = 0
	sentcounter = 0

	for line in sys.stdin:
		line = line.strip()
		if not line.startswith('<doc'):
			print(line)
		else:	
			doccounter += 1
			thisDocSentCounter = 0
#			docid = get_id(line)
			texttype = checkforum(line)
			newline = mk_new_docstartstring(line, texttype)
			print(newline)
			for line in sys.stdin:
				line = line.strip()
				if line.startswith('<s>'):
					thisDocSentCounter += 1
				#	line = '<s sid="' + docid + ':' + str(thisDocSentCounter) + '">'
					line = '<s idx="' + str(thisDocSentCounter) + '">'
					print(line)
				elif line.startswith('</doc>'):
					print(line)
					break
				else:
					print(line)
				

				
			

if __name__ == '__main__':
	main()


