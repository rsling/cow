#!/usr/bin/python

# NOT FULLY REFACTORED! Only minimal adaptation to handle gzip. -RS

# This script takes the input file (one-sentence-per-line) for the 
# the Berkeleyparser (topological fields model) and compares it to the
# parser's output file. Sentences missing in the parser output (unparsables)
# in the output are inserted from the parsers input file, one-sentence-per-line)
#   
 
import sys
import codecs
import re
import gzip

original = codecs.getreader('utf-8')(gzip.open(sys.argv[1], 'r'))
parsed = codecs.getreader('utf-8')(gzip.open(sys.argv[2], 'r'))
outfile = codecs.getreader('utf-8')(gzip.open(sys.argv[3], 'wb'))

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


def chars2xmlentities(line):
  line = line.replace('&','&amp;') 
  line = line.replace('"','&quot;') 
  line = line.replace("'","&apos;") 
  line = line.replace('<', '&lt;')
  line = line.replace('>', '&gt;')
  return(line)


for oline in original:
  oline = oline.strip()  
  pline = parsed.readline().strip()
  pline_tokens = get_tokens(pline)
  if oline == pline_tokens:
    outfile.write(pline.encode('utf-8') + '\n')
  else:  
    outfile.write(chars2xmlentities(oline).encode('utf-8') + '\n')
    if not pline_tokens =="":
      for ooline in original:
        ooline = ooline.strip()
        if not ooline == pline_tokens:
          outfile.write(chars2xmlentities(ooline).encode('utf-8') + '\n')
        else:
          outfile.write(pline.encode('utf-8'), + '\n')
          break

original.close()
parsed.close()
outfile.close()
