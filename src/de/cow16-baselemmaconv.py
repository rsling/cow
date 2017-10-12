# -*- coding: utf-8 -*-

# Transform SMOR annotation into usable.

import argparse
import os.path
import sys
import gzip
import re


dict_v = set()


def lemmalyze(a):
  a = a.strip()

  # Remove derivational information.
  r = re.sub(u'<(ADJ|V|NN)>(?:<\w+>)+<\+[A-Z]+>', r'<+\1>', a, re.UNICODE)
  r = re.sub(u'(?:<[^>]+>)+(<\+[A-Z]+>)', r'\1', r, re.UNICODE)

  # Get base lemma and POS.
  bl = re.sub(u'(?:^|.*>)([A-ZÄÖÜa-zäöüß]+)<\+[A-Z]+>', r'\1', r, re.UNICODE)
  pos = re.sub(u'.+<\+([A-Z]+)>', r'\1', r, re.UNICODE)
  prf = ''

  if not pos == 'V':
    return None

  # If verb, try to separate prefixes not analyzed by SMOR.
  if pos == 'V':

    # First, get prefixes as analyzed by SMOR.
    ana_smor = re.match(u'^([A-ZÄÖÜa-zäöüß]+)(?:<VPART>|<VPREF>)([a-zäöüß]+)<\+V>$', r, re.UNICODE)
    if ana_smor:
      bl = ana_smor.group(2)
      prf = ana_smor.group(1)

    # Now catch the ones not analyzed by SMOR.
    else:
      ana_heurictics = re.match(u"^(be|ent|er|ge|hinter|miss|miß|ver|zer|durch|über|ueber|um|unter|wider|ab|an|auf|aus|bei|dar|ein|fehl|für|fuer|inne|los|nach|rück|rueck|vor|wieder|zu|zurecht|zwischen)([a-zäöüß]+)$", bl, re.UNICODE)
      if ana_heurictics:
        bl = ana_heurictics.group(2)
        prf = ana_heurictics.group(1)

  return [bl, prf]


def lex_check(a):
  global dict_v
  return a if a and len(a) == 2 and a[0] in dict_v else None


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('infile', help='input from SMOR (gzip)')
  parser.add_argument('outfile', help='output file name (gzip)')
  parser.add_argument('verbs', help='verb dictionary file name (gzip)')
  parser.add_argument("--vlim", type=int, default=7500, help="only use the first <this number> of verbs")
  parser.add_argument("--erase", action='store_true', help="erase outout files if present")
  args = parser.parse_args()


  # Check input files.
  infiles = [args.infile, args.verbs]
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


  # Load the dictionaries.
  global dict_v

  fh_dict = gzip.open(args.verbs)
  counter = 0
  for l in fh_dict:
    counter = counter + 1
    dict_v.add(l.decode('utf-8').strip())
    if args.vlim and counter >= args.vlim:
      break
  fh_dict.close()

  ofh = gzip.open(args.outfile, 'wb')
  ifh = gzip.open(args.infile, 'r')

  c_analyses  = list()
  c_token     = ''

  while True:
    l = ifh.readline().decode('utf-8')

    # Start new word.
    if re.search(r'^> ', l) or l == '>' or not l:

      # If new word starts, analyze all analyses for PREVIOUS word.
      if len(c_analyses) > 0 and c_token:
    
          if c_token == u'GÖTÖBLÄNKK':
            ofh.write(u'>\t|\n'.encode('utf-8'))

          elif not c_token == '>':
            c_analyses = [re.sub(r'(<\+[^>]+>).*$', r'\1', x).replace('<NEWORTH>','').replace('<OLDORTH>','') for x in c_analyses] 
            lemmalyses = [lemmalyze(a) for a in c_analyses]
            lemmalyses = filter(None, [lex_check(a) for a in lemmalyses])
            anastring = "|".join(list(set([",".join(a) for a in lemmalyses]))) + '|' if len(lemmalyses) > 0 else ''
            ofh.write((c_token + "\t|" + anastring + '\n').encode('utf-8'))

      # Fresh start.
      c_analyses = list()
      c_token    = re.sub(r'^> ', r'', l.strip())

    else:

      # Only add non-empty analyses.
      if not l == 'no result for':
        c_analyses = c_analyses + [l]

    if not l:
      break

  ofh.close()
  ifh.close()

if __name__ == "__main__":
    main()
