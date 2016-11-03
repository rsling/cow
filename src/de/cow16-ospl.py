# -*- coding: utf-8 -*-

# Takes as input a COW-XML file with sentences delimited by <s> ... </s>
# Delets all XML-tags, produces a one-sentence-per-line format,
# appropriate as input for the Berkeley parser.
# (Also puts non-sentence material on a single line.)

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
  parser.add_argument('outfile', help='output file name (gzip)')
  parser.add_argument("--erase", action='store_true', help="erase outout files if present")
  args = parser.parse_args()

  # Check input files.
  infiles = [args.infile]
  for fn in infiles:
      if not os.path.exists(fn):
          sys.exit("Input file does not exist: " + fn)

  # Check (potentially erase) output files.
  outfiles = [args.outfile]
  for fn in outfiles:
      if fn is not None and os.path.exists(fn):
          if args.erase:
              try:
                  os.remove(fn)
              except:
                  sys.exit("Cannot delete pre-existing output file: " + fn)
          else:
              sys.exit("Output file already exists: " + fn)

  ofh = gzip.open(args.outfile, 'wb')
  ifh = gzip.open(args.infile, 'r')

  c_sent = list()
  while True:
    l = ifh.readline()
    if not l:
      if len(c_sent) > 0:
        ofh.write(cleanup(" ".join(c_sent)).encode('utf-8') + '\n')
        c_sent = list()
      break

    l = l.decode('utf-8')
    l = l.strip()
    if not l:
      if len(c_sent) > 0:
        ofh.write(cleanup(" ".join(c_sent)).encode('utf-8') + '\n')
        c_sent = list()
    else:
      c_sent = c_sent + [l]

  ofh.close()
  ifh.close()

if __name__ == "__main__":
    main()

