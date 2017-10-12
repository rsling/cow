# -*- coding: utf-8 -*-

# Extract pure sentences from COW-XML.

import os
import argparse
import sys
import gzip
import re

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='input COW shuffle XML file')
    parser.add_argument('outfile', help='output COW shuffle XML file')
    parser.add_argument('startvalue', type=int, help='first sentence number to assign (integer)')
    parser.add_argument('prefix', help='prefix for index (typically corpus slice number)')
    parser.add_argument('pad', type=int, help='number of digits for zero-padded index')
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
  


    # Read line by line.
    inf  = gzip.open(args.infile, 'r')
    outf = gzip.open(args.outfile, 'w')
    i    = args.startvalue
    print "First index: " + str(i)
    for l in inf:
      l = l.decode('utf-8')
      l = l.strip()

      if l:
        if not l.startswith('<s '):
          outf.write((l + '\n').encode('utf-8'))
        else:
          outf.write(('<s xid="' + args.prefix + '-' + str(i).zfill(args.pad) + '" ' + l[3:] + '\n').encode('utf-8'))
          i = i + 1
          if i % 1000 == 0:
            print('Processed sentences: ' + str(i))

    print("Last index: " + str(i))

    inf.close()
    outf.close()

if __name__ == "__main__":
    main()

