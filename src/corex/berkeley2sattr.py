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
      	line = line.strip()
 	# Sometimes, the Berkeley parser does not yield a parse, only '(())' or similar. 
        # The script save_unparsed.py (to be run before this script) will fix this issue
        # (and other cases of unparsable material omitted from the parser output) by inserting
        # the original sentence. The cases are recognizable because the first character is not a '('.
	# Simply write these unparsed sentences to the output, one token per line:
	#if noparse.match(line):
	if not line.startswith('('):
		words = line.strip().split(" ")
		for word in words:
			print(word)
#		print("~~#~END~#~~") # This is for debugging.

	else:   
		# reverting < > to &lt; and &gt; must be done before inserting xml-attributes:
		line = line.replace('<', '&lt;')
		line = line.replace('>', '&gt;')
		line = re.sub(pos_and_token, '~#~\g<1>~#~', line)
		line = separator.split(line)
        	line = [e.strip() for e in line if not e == '']
		sattrify(line)
		print("~~#~END~#~~")
	 

