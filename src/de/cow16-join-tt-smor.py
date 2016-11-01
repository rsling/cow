# -*- coding: utf-8 -*-

# This script zips SMOR innotations into TT annotations.

import gzip
import re
import argparse
import os.path
import sys


NO_ANNO=['_', '_', '|', '|']

# For ENCOW outside <s></s>.
def fix_entities(s):
  return s.replace('&amp;lt;', '&lt;').replace('&amp;gt;', '&gt;')#.replace('&amp;quot;', '&quot;').replace('&amp;apos;', '&apos;').replace('&amp;amp;', '&amp;')

def entity_encode(s):
  s = s.replace('&', '&amp;')
  s = s.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
  return s

def advance(h):
  s = ''
  while not s:
    s = h.readline().decode('utf-8')

    # Skip if "word joiner" tokens are in input. TAB-WORDJOINER-TAB is for Malt files.
    if re.match(u'^[\u00a0\u2060\u200b]+\t', s, re.UNICODE) or re.match(u'^[0-9]+\t(?:[\u00a0\u2060\u200b]+|)\t', s, re.UNICODE) :
      s = ''
      continue

    s = s.strip()
    s = s.replace(u'\u00a0', '').replace(u'\u2060', '').replace(u'\u200b', '')
    s = entity_encode(s)
  return s


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("tt", help="TreeTagger file (gzip)")
  parser.add_argument("smor", help="SMOR file (gzip)")
  parser.add_argument("output", help="output file (gzip)")
  parser.add_argument("--erase", action='store_true', help="erase outout files if present")
  args = parser.parse_args()

  # Check input files.
  infiles = [args.tt, args.smor]
  for fn in infiles:
      if not os.path.exists(fn):
          sys.exit("Input file does not exist: " + fn)

  # Check (potentially erase) output files.
  outfiles = [args.output]
  for fn in outfiles:
      if fn is not None and os.path.exists(fn):
          if args.erase:
              try:
                  os.remove(fn)
              except:
                  sys.exit("Cannot delete pre-existing output file: " + fn)
          else:
              sys.exit("Output file already exists: " + fn)

  fh_tt = gzip.open(args.tt, 'r')
  fh_smor = gzip.open(args.smor, 'r')
  fh_out = gzip.open(args.output, 'wb')

  counter = 0
  for l in fh_tt:
    counter = counter + 1
    l = l.decode('utf-8')

    # Skip if "word joiner" tokens are in input.
    if re.match(u'^[\u00a0\u2060\u200b]+\t', l, re.UNICODE):
      continue

    l = l.strip()
    l = l.replace(u'\u00a0', '').replace(u'\u2060', '').replace(u'\u200b', '')

    if not l:
      continue

    smors = advance(fh_smor).split('\t')
    tts = entity_encode(l).split('\t')
    if smors[0] == tts[0]:
      if tts[1] == u'NN':
        fh_out.write('\t'.join(tts + smors[1:]).encode('utf-8') + '\n')
      else:
        fh_out.write('\t'.join(tts + NO_ANNO).encode('utf-8') + '\n')
    else:
      prob='[' + str(counter) + '] Inconsistency: ' + ' '.join([tts[0], u' => ', smors[0]]).encode('utf-8')
      raise Exception(prob)


  fh_tt.close()
  fh_smor.close()
  fh_out.close()

if __name__ == "__main__":
    main()

