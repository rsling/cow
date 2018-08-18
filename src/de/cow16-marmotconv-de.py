# -*- coding: utf-8 -*-

# Transform Marmot German annotation into usable.

import argparse
import os.path
import sys
import gzip
import re

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
  ifh = open(args.infile, 'r')

  for l in ifh:
    l = l.decode('utf-8')
    l = l.strip()

    if not l:
      ofh.write('\n')
      continue

    fs = l.split('\t')
    anno = re.sub( r'[^|]+=', r'', re.sub(r'(case|gender|number)=\*', r'u\1', fs[7]) )
    pos = re.sub(r'^.+\|', r'', fs[5])

    if not (len(anno) > 0) and (not anno == '_'):
      anno = '|'  
    ofh.write( ("\t".join([ fs[1], pos, anno ])).encode('utf-8') + '\n' )

  ofh.close()
  ifh.close()

if __name__ == "__main__":
    main()
