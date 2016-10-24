# -*- coding: utf-8 -*-

# Transform Marmot MultExt East "English" annotation to usable.

import argparse
import os.path
import sys
import gzip
import re

ME_MAP = dict([
#  ('N1c', 'commmon'),
#  ('N1p', 'proper'),
#  ('N2m', 'masc'),
#  ('N2f', 'fem'),
#  ('N2n', 'neut'),
  ('N3s', 'sg'),
  ('N3p', 'pl'),
#  ('V1m', 'lex'),
#  ('V1a', 'aux'),
#  ('V1o', 'modal'),
#  ('V1b', 'base'),
  ('V2i', 'ind'),
  ('V2c', 'cond'),
  ('V2n', 'inf'),
  ('V2p', 'part'),
  ('V3p', 'pres'),
  ('V3s', 'past'),
  ('V41', '1'),
  ('V42', '2'),
  ('V43', '3'),
  ('V5s', 'sg'),
  ('V5p', 'pl'),
#  ('A1f', 'qual'),
  ('A2p', 'pos'),
  ('A2c', 'comp'),
  ('A2s', 'sup'),
#  ('P1p', 'pers'),
#  ('P1s', 'poss'),
#  ('P1q', 'int'),
#  ('P1r', 'rel'),
#  ('P1x', 'refl'),
#  ('P1g', 'gen'),
#  ('P1t', 'there'),
  ('P21', '1'),
  ('P22', '2'),
  ('P23', '3'),
  ('P3m', 'masc'),
  ('P3f', 'fem'),
  ('P3n', 'neut'),
  ('P4s', 'sg'),
  ('P4p', 'pl'),
  ('P5n', 'nom'),
  ('P5a', 'acc'),
#  ('P6s', 'posssg'),
#  ('P6p', 'posspl'),
#  ('P7m', 'possm'),
#  ('P7f', 'possf'),
#  ('P17r', 'rel'),
#  ('P17q', 'q'),
#  ('D1d', 'dem'),
#  ('D1i', 'ind'),
#  ('D1s', 'poss'),
#  ('D1g', 'gen'),
  ('D21', '1'),
  ('D22', '2'),
  ('D23', '3'),
  ('D4s', 'sg'),
  ('D4p', 'pl'),
#  ('D6s', 'ownersg'),
#  ('D6p', 'ownerpl'),
#  ('D7m', 'ownerm'),
#  ('D7f', 'ownerf'),
#  ('D10r', 'rel'),
#  ('D10q', 'q'),
#  ('R1m', 'mod'),
#  ('R1s', 'spec'),
  ('R2p', 'pos'),
  ('R2c', 'comp'),
  ('R2s', 'sup'),
#  ('R6r', 'rel'),
#  ('R6q', 'q'),
#  ('S1p', 'pre'),
#  ('S1t', 'post'),
#  ('C1c', 'coord'),
#  ('C1s', 'subord'),
#  ('C3i', 'init'),
#  ('C3n', 'noninit')
#  ('M1c', 'card'),
#  ('M1o', 'ord')
  ])


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
    annos = fs[7].split('|')
    annos = [ ME_MAP.get(a) for a in annos if a in ME_MAP.keys() ]

    if len(annos) > 0:
      anno = '|'+ '|'.join(annos)  +'|'
    else:
      anno = '|'  
    ofh.write( ("\t".join([ fs[1], fs[5], anno ])).encode('utf-8') + '\n' )

  ofh.close()
  ifh.close()

if __name__ == "__main__":
    main()
