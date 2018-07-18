# -*- coding: utf-8 -*-

# Takes as input a COW-XML file with sentences delimited by <s> ... </s>
# Delets all XML-tags, produces input appropriate for the Berkeley parser
# as modified by COW. Output is to stdout.

import sys
import codecs
import re
import gzip
import argparse
import os

def cleanup(s):
  s = re.sub(u' +', r' ', s, re.UNICODE)
  s = s.replace('(', '[').replace(')', ']')
  s = s.replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>').replace('&apos;', "'")
  s = s.replace('&amp;', '&')
  return s


def main():  
  parser = argparse.ArgumentParser()
  parser.add_argument('infile', help='input from Marmot (NO gzip)')
  parser.add_argument('poscolumn', type=int, help='which column contains gold POS')
  args = parser.parse_args()

  # Check input files.
  infiles = [args.infile]
  for fn in infiles:
      if not os.path.exists(fn):
          sys.exit("Input file does not exist: " + fn)

  in_s = False
  indices = [0, args.poscolumn]

  with gzip.open(args.infile, 'r') as ifh:
    for l in ifh:
      l = l.decode('utf-8').strip()
      if not l:
        continue

      # Within sentence.
      if in_s:
        if re.search(r'</s>', l): 
          print
          in_s = False
        elif not re.search(r'^<', l):
          print('\t'.join([cleanup(l.split('\t')[i]) for i in indices]).encode('utf8'))
       
      # Not within sentence.
      else:
        if re.search(r'<s[ >]', l):
          in_s = True

if __name__ == "__main__":
    main()

