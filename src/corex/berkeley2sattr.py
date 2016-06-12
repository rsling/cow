#! /usr/bin/python

import sys
import re
import codecs

pos_and_token = re.compile('\(([^ ]+ (?:[^ )]+|\)))\)')
# split on '(ATTR' or on ')' if followed by something other than '~' (lookahead),
# or on ')' if it is the last character on the line:
separator = re.compile('(\([^()~]+|\) *(?=(?:[^~]|$)))') 
noparse = re.compile('^[()]+$')


readfrom = codecs.open(sys.argv[1])
original = codecs.open(sys.argv[2])
	


def sattrify(line):
	stack = []
	for e in line:
		if e.startswith('('):
			tagname = e.lstrip('(').lower()
			optag = '<' + tagname + '>'
			print(optag)
                        stack.append(tagname) 
		elif e == ')':
			try:
				tagname = stack.pop()
				cltag = '</' + tagname + '>'
				print(cltag)
			except IndexError as err:
				raise Exception('Pop from empty stack.')
		else:
			tokenposlist = process_tokens(e)
			for e in tokenposlist: 
				print(e)
	if len(stack) > 0:
		print("Stack: "),
		print(stack)
		raise Exception("Stack not empty.")

def revert_postok(somestring):
	l = somestring.split(' ')
	tokpos = l[1] + '\t' + l[0]
	return(tokpos)
		  
			
def process_tokens(somestring):
	postokens = somestring.split('~#~ ~#~') 
	postokens = [e.replace('~#~','') for e in postokens]

	tokenposes = [revert_postok(e) for e in postokens]
	return(tokenposes)
		
	
for line in readfrom:
	input_sentence = original.readline()
      	line = line.strip()
 	# Sometimes, the Berkeley parser does not yield a parse, only '(())' or similar.
	# In theses cases, retrieve the original line from the input file:
	if noparse.match(line):
		input_words = input_sentence.strip().split(" ")
		for word in input_words:
			print(word)
		print("~~#~END~#~~")

	else:   
		# revert < > to &lt; and &gt;
        	# must be done before xml-attributes are inserted:
		line = line.replace('<', '&lt;')
		line = line.replace('>', '&gt;')
		line = re.sub(pos_and_token, '~#~\g<1>~#~', line)
		line = separator.split(line)
        	line = [e.strip() for e in line if not e == '']
		sattrify(line)
		print("~~#~END~#~~")
	 


