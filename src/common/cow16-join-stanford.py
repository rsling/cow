# -*- coding: utf-8 -*-

# This script zips SMOR innotations into TT annotations.

import gzip
import re
import argparse
import os.path
import sys


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
    #s = entity_encode(s)
  return s


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("xml", help="COW XML file (gzip)")
  parser.add_argument("stanford", help="Stanford CONLL file (gzip)")
  parser.add_argument("output", help="output file (gzip)")
  parser.add_argument("fields", type=str, help="comma-separated list of columns (0-based) to import from CONLL")
  parser.add_argument("--blanks", type=str, help="bank string to be used outside <s/>, else all fields _")
  parser.add_argument("--erase", action='store_true', help="erase outout files if present")
  args = parser.parse_args()

  # Check input files.
  infiles = [args.xml, args.stanford]
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

  # Decompose and implicitly check index arg.
  indices = [int(x.strip()) for x in args.fields.split(",")]

  # Make blank string.
  if args.blanks:
    blanks = args.blanks
  else:
    blanks = '\t'.join('_' * len(indices))

  fh_xml      = gzip.open(args.xml, 'r')
  fh_stanford = gzip.open(args.stanford, 'r')
  fh_out      = gzip.open(args.output, 'wb')

  counter     = 0
  is_sentence = False

  for l in fh_xml:
    counter = counter + 1
    l = l.decode('utf-8')

    # Skip if "word joiner" tokens are in input.
    if re.match(u'^[\u00a0\u2060\u200b]+\t', l, re.UNICODE):
      continue

    l = l.strip()
    l = l.replace(u'\u00a0', '').replace(u'\u2060', '').replace(u'\u200b', '')

    if not l:
      continue

    if not is_sentence:
      if re.match(r'^<s[> ]', l, re.UNICODE):
        is_sentence = True
      if l[0] == '<':
        fh_out.write((l + '\n').encode('utf-8'))
      else:
        fh_out.write((l + '\t' + blanks + '\n').encode('utf-8'))

    else:  # is_sentence
      if re.match(r'^<\/s>', l, re.UNICODE):
        is_sentence = False
        fh_out.write((l + '\n').encode('utf-8'))
      else: # is_sentence and not end of sentence
        xmls      = l.split('\t')
        stanfords = advance(fh_stanford).split('\t')
        if not xmls[0] == entity_encode(stanfords[1]):
          prob='[' + str(counter) + '] Inconsistency: "' + xmls[0].encode('utf-8') + '"!="' + stanfords[1].encode('utf-8') + '"'
          raise Exception(prob)
        else:
          fh_out.write((l + '\t' + '\t'.join([stanfords[i] for i in indices]) + '\n').encode('utf-8'))

  fh_xml.close()
  fh_stanford.close()
  fh_out.close()

if __name__ == "__main__":
    main()

