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

def advance(h, encode=True):
  s = ''
  while not s:
    s = h.readline().decode('utf-8')

    # Skip if "word joiner" tokens are in input. TAB-WORDJOINER-TAB is for Malt files.
    if re.match(u'^[\u00a0\u2060\u200b]+\t', s, re.UNICODE) or re.match(u'^[0-9]+\t(?:[\u00a0\u2060\u200b]+|)\t', s, re.UNICODE) :
      s = ''
      continue

    s = s.strip()
    s = s.replace(u'\u00a0', '').replace(u'\u2060', '').replace(u'\u200b', '')
    if encode:
      s = entity_encode(s)
  return s


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("outfile", help="COW-XML output (gzip)")
  parser.add_argument("xml", help="COW-XML input file (gzip)")
  parser.add_argument("blank", help="this string will be appended to tokens outside <s></s>; don't forget initial '\t'")
  parser.add_argument("annotations", nargs='+', help="genric VRT annotation file(s) to be merged at token level (gzip)")
  parser.add_argument("--malt", help="use this to pass an UNPROCESSED Malt parser file (CONLL layout) (gzip)")
  parser.add_argument("--tt", help="use this to pass an UNPROCESSED TT tagger file (lemma not well-formed set attribute) (gzip)")
  parser.add_argument("--smor", help="use this to pass a SMOR compound analysis file (gzip)")
  parser.add_argument("--bas", help="use this to pass a SMOR verb base lemma file (gzip)")
  parser.add_argument("--tag", type=int, help="where is POS info (req. for --bas and --smor)")
  parser.add_argument("--lem", type=int, help="where is lemma info (req. for --bas and --smor)")
  parser.add_argument("--check", type=int, help="how many columns expected in the end? (for tesing)")
  parser.add_argument("--erase", action='store_true', help="erase outout files if present")
  args = parser.parse_args()

  if (args.bas or args.smor) and not args.tag:
    sys.exit("--bas option requires --tag option to be set.")

  # Check input files.
  infiles = [args.xml] + args.annotations
  if args.malt:
    infiles = infiles + [args.malt]
  if args.tt:
    infiles = infiles + [args.tt]
  if args.smor:
    infiles = infiles + [args.smor]
  if args.bas:
    infiles = infiles + [args.bas]
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
  if args.tt:
    fh_tt = gzip.open(args.tt, 'r')
  if args.smor:
    fh_smor = gzip.open(args.smor, 'r')
  if args.bas:
    fh_bas = gzip.open(args.bas, 'r')
  fh_annos = list()
  for s in args.annotations:
    fh_annos = fh_annos + [gzip.open(s, 'r')]

  blank = args.blank.decode('utf-8').decode('string-escape')

  in_sentence = False
  counter = 0
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

    if not in_sentence:
      if re.match(r'^<s>', l, re.UNICODE):
        in_sentence = True
      elif not l[0] == '<':
        l = fix_entities(l.split('\t')[0] + blank)
    elif in_sentence:
      if not l[0] == '<':

        fs = l.split('\t')   # The master token + annotations. 
        for h in fh_annos:
          fsa = advance(h).split('\t')
          if fsa[0] == fs[0]:
            fs = fs + fsa[1:]
          else:
            prob='[' + str(counter) + '] Inconsistent annotations (generic): ' + ' '.join([fs[0]] + [fsa[1]]).encode('utf-8')
            raise Exception(prob)

        # Unprocessed TT files, where lemma needs to be converted into set.
        if args.tt:
          fsa = advance(fh_tt).split('\t')
          if fsa[0] == fs[0]:
            fs = fs + [fsa[1]] + [u'|' if fsa[2] == u'|' else u'|'+fsa[2]+u'|']
          else:
            prob='[' + str(counter) + '] Inconsistent annotations (TT): ' + ' '.join([fs[0]] + [fsa[0]]).encode('utf-8')
            raise Exception(prob)



        # Annos which create BASE LEMMA and ELEMENTS.
        if args.smor or args.bas:

          # No if/elif here because we still need to advance input files!
          v_or_n = False

          # SMOR compound files.
          if args.smor:
            fsa = advance(fh_smor).split('\t')
            if fs[0] == fsa[0]:
              if fs[args.tag] == u"NN" and not fsa[1] == u'_':
                v_or_n = True
                fs = fs + [fsa[1]] + [u'|' + fsa[2] + u'|'] + fsa[3:5]
            else:
              prob='[' + str(counter) + '] Inconsistent annotations (SMOR): ' + ' '.join([fs[0]] + [fsa[0]]).encode('utf-8')
              raise Exception(prob)
  
          # Verb base lemma files -- REQUIRES TAG!
          if args.bas:
            fsa = advance(fh_bas).split('\t')
            if fs[0] == fsa[0]:
              if re.search(u"^VV", fs[args.tag], re.UNICODE):
                analyses = [x.split(u',') for x in fsa[1].split(u'|')]
                baseverbs = "|".join(filter(None, list(set([x[0] for x in analyses]))))
                prefixes = "|".join(filter(None, list(set([x[1] for x in analyses  if len(x)>1]))))

                # Unless we have BOTH from SMOR, use TT verb lemma as base lemma.
                if baseverbs and prefixes:
                  v_or_n = True
                  baseverbs = u'|'+baseverbs+u'|' 
                  prefixes = u'|'+prefixes+u'|' if prefixes else u'|'
                  fs = fs + [u'_', baseverbs, u'_', prefixes]
            else:
              prob='[' + str(counter) + '] Inconsistent annotations (Verb base lemma): ' + ' '.join([fs[0]] + [fsa[0]]).encode('utf-8')
              raise Exception(prob)

          # If neither, add lemma as baselemma and make emty elements. 
          if not v_or_n:
            fs = fs + [u'_', fs[args.lem], u'|', u'|']
  

        # Unprocessed Malt files have different layout (CONLL).
        if args.malt:
          fsa = advance(fh_malt).split('\t')
          if fsa[1] == fs[0]:
            fs = fs + [fsa[i] for i in [0,6,7,3]] 
          else:
            prob='[' + str(counter) + '] Inconsistent annotations (Malt): ' + ' '.join([fs[0]] + [fsa[1]]).encode('utf-8')
            raise Exception(prob)

        if args.check and not len(fs) == args.check:
          sys.exit( (u'Length not ' + str(args.check) + u': ' + u' '.join(fs)).encode('utf-8') )

        l = '\t'.join(fs)

      elif re.match(r'</s>', l, re.UNICODE):
        in_sentence = False

    fh_out.write(l.encode('utf-8') + '\n')

  fh_xml.close()
  fh_out.close()
  if args.malt:
    fh_malt.close()
  if args.tt:
    fh_tt.close()
  if args.smor:
    fh_smor.close()
  if args.bas:
    fh_bas.close()
  for h in fh_annos:
    h.close()

if __name__ == "__main__":
    main()

