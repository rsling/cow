#!/bin/env python

# Read in corpus 1 in COW-XML format and corpus 2, both one-token-per-line.
# The tokens in corpus 1 and corpus 2 are identical, corpus 1 doesn't have any
# XML tags embedded within <s> ... </s> regions, corpus 2 contains none of 
# the XML-markup of corpus 1 but has additional XML-tags at the sentence-level.
# This script combines XML markup of corpus 1 and corpus 2.
# (Useful for topological field annotation in corpus 2, and <doc>, <div> and <s>
# tags in corpus 1, for example.) 

import sys
import codecs
import re

cowxml = codecs.open(sys.argv[1], "r", "utf-8")
topoxml = codecs.open(sys.argv[2], "r", "utf-8")

openingtag = re.compile('<[^/]')
squarebracket = re.compile('.*[)(].*')

stack = []

cowxml_counter = 0
topoxml_counter = 0

while True:
  cowxml_line = cowxml.readline() # read a line from corpus 1
  if len(cowxml_line) == 0:
      break
  else:
	# if line from COW-XML file is an XML-tag, read and print as many lines from corpus 2
      	# as there are elements on the stack (these are the closing XML-tags from corpus 2), 
	# then print line from COW-XML file
      cowxml_counter += 1
      if  cowxml_line.startswith('<'):
		for i in range(0,len(stack)):
			l = topoxml.readline()
			topoxml_counter += 1
			print(l.strip().encode("utf-8"))
			stack.pop()
	  	print(cowxml_line.strip().encode('utf-8'))
      else:
      # if the line from corpus 1 is not an XML-tag, start reading from corpus 2
	  cowxml_word = cowxml_line.split("\t")[0].strip()
          for topo_line in topoxml:
		topoxml_counter += 1
                # if we have an opening XML-tag, print it and put it on the stack
		if openingtag.match(topo_line):
			l = topo_line.strip()
			stack.append(l)
			print(l.encode("utf-8"))
                elif topo_line.startswith('</'):
                # if we have a closing XML-tag, print it and pop it from the stack
			l = topo_line.strip()
                        stack.pop()
			print(l.encode("utf-8"))
                # '~~#~END~#~~\n' marks sentence boundaries in corpus 2; ignore them
                elif topo_line == '~~#~END~#~~\n':
			pass
		else:
                # if we have a word token, compare with word token from corpus 1;
			topo_word = topo_line.strip()
		# if they match, print the entire line from corpus 1 (token plus annotations)
              		if topo_word == cowxml_word and topo_word != '~~#~END~#~~':
				print(cowxml_line.strip().encode("utf-8"))
                # and return to reading the next line from corpus 1
                                break
			# allow for mismatch between '(' (cow-xml) and '[' (topo-xml):
			else:
				#if topo_word in ['[',']']:
				if squarebracket.match(topo_word):
					dummy = topo_word.replace('[','(').replace(']',')')      
					if dummy == cowxml_word and dummy != '~~#~END~#~~':
						print(cowxml_line.strip().encode("utf-8"))
						break
                # if they don't match, something must have gone wrong; print error message and quit:
				else:   
					sys.stderr.write("\nTokens don't match.\n")
					sys.stderr.write("Token: '" + cowxml_word + "'\t\t(line " + str(cowxml_counter) + ", file " + sys.argv[1] + ")\n")
                               		sys.stderr.write("Token: '" + topo_word + "'\t\t(line " + str(topoxml_counter) + ", file " + sys.argv[2] + ")\n")
                                	sys.exit(1)

