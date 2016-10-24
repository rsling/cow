# -*- coding: utf-8 -*-

# Extract pure sentences from COW-XML.

import os
import argparse
import sys
import gzip


def entity_decode(s):
    s = s.replace(u'&lt;', '<').replace(u'&gt;', '>').replace(u'&quot;', '"').replace(u'&apos;', "'")
    s = s.replace(u'&amp;', '&')
    return s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='input DECOW XML file (gzip)')
    parser.add_argument('outfile', help='output file name (gzip)')
    parser.add_argument('fields', help='comma-separated list of VRT fields to extract (0-based!)')
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

    outfile_sent = gzip.open(args.outfile, 'wb')

    fields = [int(i) for i in args.fields.split(',')]
    if len(fields) < 1:
      sys.exit("Not a well-formed VRT index list: " + args.fields)

    # State variable: Reading sentence or not.
    insentence = False   

    # Read line by line.
    f = gzip.open(args.infile, 'r')
    for l in f:
      l = l.decode('utf-8')
      l = l.strip()
      if not l:
        continue

      # IN sentence.
      if insentence:

        if (l == '</s>'):
          insentence = False
          outfile_sent.write('\n')
        elif (not l[0] == '<'):
          annos = l.split('\t')
          outfile_sent.write('\t'.join([entity_decode(annos[i]) for i in fields]).encode('utf-8') + '\n')

      # NOT in sentence.
      elif (l == '<s>'):
          insentence = True

    f.close()
    outfile_sent.close()

if __name__ == "__main__":
    main()

