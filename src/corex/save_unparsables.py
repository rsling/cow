#!/usr/bin/python

# This script takes the input file (one-sentence-per-line) for the 
# the Berkeleyparser (topological fields model) and compares it to the
# parser's output file. Sentences missing in the parser output (unparsables)
# in the output are inserted from the parsers input file, one-sentence-per-line)
#   
 
import sys
import codecs
import re

original = codecs.open(sys.argv[1], 'r', 'utf-8')
parsed = codecs.open(sys.argv[2], 'r', 'utf-8')
pos_and_token = re.compile('\(([^ ]+ (?:[^ )]+|\)))\)')



# This takes a line of the Berkeley topological parser's
# output, returns a string of tokens separated by whitespace

def get_tokens(line):
    pt = pos_and_token.findall(line)
    if len(pt) > 0:
    	pt = [i.split(" ") for i in pt]
    	t = [i[1] for i in pt]
	s = " ".join(t)
    else:
	s = ''
    return(s)




for oline in original:
	oline = oline.strip()	
	pline = parsed.readline().strip()
	pline_tokens = get_tokens(pline)
	if oline == pline_tokens:
		print(pline.encode('utf-8'))
	else:	
		print(oline.encode('utf-8'))
		if not pline_tokens =="":
			for ooline in original:
				ooline = ooline.strip()
				if not ooline == pline_tokens:
					print(ooline.encode('utf-8'))
				else:
					print(pline.encode('utf-8'))
					break
		
	

