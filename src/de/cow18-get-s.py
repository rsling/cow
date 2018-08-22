# -*- coding: utf-8 -*-

# Takes as input a COW-XML file with sentences delimited by <s> ... </s>
# Delets all XML-tags, produces input appropriate for the Berkeley parser
# as modified by COW. Output is to stdout.

# With poscolumn < 0, it generates output for Mate parser.

import sys
import codecs
import re
import gzip
import argparse
import os

def cleanup(s, nobrackets):
  s = re.sub(u' +', r' ', s, re.UNICODE)
  if not nobrackets:
    s = s.replace('(', '[').replace(')', ']')
  s = s.replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>').replace('&apos;', "'")
  s = s.replace('&amp;', '&')
  return s


def main():  
  parser = argparse.ArgumentParser()
  parser.add_argument('infile', help='gzipped COW XML file')
  parser.add_argument('poscolumn', type=int, help='which column contains gold POS; -1 for NONE')
  parser.add_argument('--conll', action='store_true', help="add CoNLL columns")
  parser.add_argument('--nobrackets', action='store_true', help="do NOT change bracktes; do not use for Berekely preparation")
  args = parser.parse_args()

  # Check input files.
  infiles = [args.infile]
  for fn in infiles:
      if not os.path.exists(fn):
          sys.exit("Input file does not exist: " + fn)

  in_s = False
  if args.poscolumn >= 0:
    indices = [0, args.poscolumn]
  else:
    indices = [0]

  idx=1

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
          idx = 1
        elif not re.search(r'^<', l):
          if not args.conll:
            print('\t'.join([cleanup(l.split('\t')[i], args.nobrackets) for i in indices]).encode('utf8'))
          else:
            if args.poscolumn < 0:
              fields=l.split('\t')
              print('\t'.join([str(idx), cleanup(fields[0], args.nobrackets)] + ['_']*11).encode('utf-8'))
            else:
              print('\t'.join([str(idx), cleanup(fields[0], args.nobrackets)] + ['_']*2 + cleanup(fields[args.poscolumn], args.nobrackets) + ['_']*8).encode('utf-8'))
            idx=idx+1

      # Not within sentence.
      else:
        if re.search(r'<s[ >]', l):
          in_s = True

if __name__ == "__main__":
    main()

