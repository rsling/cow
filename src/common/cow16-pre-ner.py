# -*- coding: utf-8 -*-

# Extract pure sentences from COW-XML.

import os
import argparse
import sys
import gzip

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='input COW sentence file')
    args = parser.parse_args()

    # Check input files.
    infiles = [args.infile]
    for fn in infiles:
        if not os.path.exists(fn):
            sys.exit("Input file does not exist: " + fn)

    # Read line by line.
    f = gzip.open(args.infile, 'r')
    for l in f:
      l = l.decode('utf-8')
      l = l.strip()

      if not l:
        sys.stdout.write('\n')
        sys.stdout.flush()
      else:
        s = l.split('\t')[0]
        s = s.replace(u'\u00a0', '').replace(u'\u2060', '').replace(u'\u200b', '')
        sys.stdout.write(s.encode('utf-8') + ' ')

    f.close()

if __name__ == "__main__":
    main()






