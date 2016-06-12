#!/usr/bin/python

# Takes as input a COW-XML file with sentences delimited by <s> ... </s>
# Delets all XML-tags, produces a one-sentence-per-line format,
# appropriate as input for the Berkeley parser.
# (Also puts non-sentence material on a single line.)

import sys
import codecs
import re

infile = codecs.open(sys.argv[1])
tag = re.compile(' *</?[^>]+> *')


def ospl(buf):
	out = " ".join(buf)
	out = re.sub(tag, '', out) 
	out = out.strip()
	return(out)

def readsentence(infile, stopstring):
	for line in infile:
		sline = line.split("\t")
		token = sline[0].strip()
		b.append(token)
		if token.startswith(stopstring):
			out = ospl(b)
			print(out)
			break


	
for line in infile:
	sline = line.split("\t")
	token = sline[0].strip()
	if token == ('<s>'):
		b = []
		readsentence(infile, '</s>')
        else:
		if not token.startswith('<'):
			b = [token]
			readsentence(infile, '<')			

						

		





