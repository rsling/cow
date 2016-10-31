# -*- coding: utf-8 -*-

# This script zips pure annotations into COW-XML
# Only within <s></s>.

import gzip
import re
import argparse
import os.path
import sys

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
    s = h.readline().decode('utf-8').strip()
    s = s.replace(u'\u00a0', '').replace(u'\u2060', '').replace(u'\u200b', '')
    s = entity_encode(s)
  return s


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("outfile", help="COW-XML output (gzip)")
  parser.add_argument("xml", help="COW-XML input file (gzip)")
  parser.add_argument("blank", help="this string will be appended to tokens outside <s></s>; don't forget initial '\t'")
  parser.add_argument("annotations", nargs='+', help="annotation file(s) to be merged at token level (gzip)")
  parser.add_argument("--malt", help="use this to pass an UNPROCESSED Malt parser file (CONLL layout) (gzip)")
  parser.add_argument("--erase", action='store_true', help="erase outout files if present")
  args = parser.parse_args()

  # Check input files.
  infiles = [args.xml] + args.annotations
  if args.malt:
    infiles = infiles + [args.malt]
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

  fh_xml = gzip.open(args.xml, 'r')
  fh_out = gzip.open(args.outfile, 'wb')
  if args.malt:
    fh_malt = gzip.open(args.malt, 'r')
  fh_annos = list()
  for s in args.annotations:
    fh_annos = fh_annos + [gzip.open(s, 'r')]

  blank = args.blank.decode('utf-8').decode('string-escape')

  in_sentence = False
  for l in fh_xml:
    l = l.decode('utf-8').strip().replace(u'\u00a0', '').replace(u'\u2060', '').replace(u'\u200b', '')

    if not l:
      continue

    if not in_sentence:
      if re.match(r'^<s>', l, re.UNICODE):
        in_sentence = True
      elif not l[0] == '<':
        l = fix_entities(l.split('\t')[0] + blank)
    elif in_sentence:
      if not l[0] == '<':
        # Here, the actual joiner works.

        fs = l.split('\t')   # The master token + annotations. 
        for h in fh_annos:
          fsa = advance(h).split('\t')

          if fsa[0] == fs[0]:
            fs = fs + fsa[1:]
          else:
            prob=' '.join([fs[0]] + [fsa[1]]).encode('utf-8')
            #print '*** G  ' + prob
            raise Exception('Inconsistent annotations (generic): ' + prob)

        # Unprocessed Malt files have different layout (CONLL).
        if args.malt:
          fsa = advance(fh_malt).split('\t')
          if fsa[1] == fs[0]:
            fs = fs + [fsa[i] for i in [0,6,7,3]] 
          else:
            prob=' '.join([fs[0]] + [fsa[1]]).encode('utf-8')
            #print '*** M ' + prob
            raise Exception('Inconsistent annotations (Malt): ' + prob)

        l = '\t'.join(fs)

      elif re.match(r'</s>', l, re.UNICODE):
        in_sentence = False

    #print(l.encode('utf-8'))
    fh_out.write(l.encode('utf-8') + '\n')

  fh_xml.close()
  fh_out.close()
  for h in args.annotations:
    h.close()

if __name__ == "__main__":
    main()

