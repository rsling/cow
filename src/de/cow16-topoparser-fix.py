# -*- coding: utf-8 -*-

import sys
import re
import gzip
import argparse
import os


# Get token sequence from parsed sentence.
def get_tokens(line):
  pt = re.findall(r'\(([^ ]+ (?:[^ )]+|\)))\)', line, re.UNICODE)
  if pt:
    pt = [i.split(" ") for i in pt]
    t = [i[1] for i in pt]
    s = " ".join(t)
  else:
    s = ''
  return s


def chars2xmlentities(line):
  line = line.replace('&','&amp;').replace('"','&quot;').replace("'","&apos;").replace('<', '&lt;').replace('>', '&gt;')
  return line


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('original', help='parser input (gzip)')
  parser.add_argument('parsed', help='parser output (gzip)')
  parser.add_argument('outfile', help='output file name (gzip)')
  parser.add_argument("--erase", action='store_true', help="erase outout files if present")
  args = parser.parse_args()

  # Check input files.
  infiles = [args.original, args.parsed]
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

  original = gzip.open(args.original, 'r')
  parsed = gzip.open(args.parsed, 'r')
  outfile = gzip.open(args.outfile, 'wb')

  for l in original:
    l = l.decode('utf-8')    
    l = l.strip() 

    p = parsed.readline()
    p = p.decode('utf-8')
    p = p.strip()
    p_tokens = get_tokens(p)

    if l == p_tokens:
      outfile.write(p.encode('utf-8') + '\n')
    else:  
      outfile.write(chars2xmlentities(l).encode('utf-8') + '\n')

  
  original.close()
  parsed.close()
  outfile.close()



if __name__ == "__main__":
    main()
