# -*- coding: utf-8 -*-

# Transform SMOR annotation into usable.

import argparse
import os.path
import sys
import gzip
import re


def resubstitute(s):
  s = re.sub(u'([a-zA-Z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df]):([a-zA-Z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df])', r'\1', s)
  s = re.sub(u'[a-zA-Z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df]:<>', r'', s)
  s = s.replace(':<>', '')
  return s



def nounalize(s):

  # Preprocess characteristic suffixes.
#  s = re.sub(u'([a-zA-Z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df]+)(<+NN>|<NN>):<>([a-z\u00e4\u00f6\u00fc\u00df]+)<SUFF>', u'\1\3\2<<<', s)

  # Make TRUNCs split properly.
  nouns = s.replace('<TRUNC>', '<TRUNC><NN>').replace('<NPROP>', '<NN>')
  nouns = nouns.split('<NN>')
  nouns = filter(None, nouns)

  # Rescue ablaut vowels in derivations.
  nouns = [re.sub(u'([^><]*)([aeiou]):([aeiou])([^><]*:<><V>)', r'\1\3\4', x) for x in nouns]

  # Fix ß-ss corrections right away.
  nouns = [re.sub(u'<>:s\u00df:s', u'\u00df', x) for x in nouns]

  # Mark (pseudo-)suffix defletion.
  nouns = [re.sub(r'(.)(:<>)(.)(:<>)$', r'\1\3\t#\1\3', x) for x in nouns]
  nouns = [re.sub(r'(.)(:<>)$', r'\1\t#\1', x) for x in nouns]

  # Fix double suffixation which is essentially one.
  nouns = [re.sub(u'<>:([a-zA-Z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df])<>:([a-zA-Z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df])', r'<>:\1\2', x) for x in nouns[:-1]] + [nouns[-1]]
  nouns = [re.sub(u'<>:([a-zA-Z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df])<>:([a-zA-Z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df])', r'<>:\1\2', x) for x in nouns[:-1]] + [nouns[-1]]

  # Fix umlauts in non-final compound elements and get rid of <+NN>.
  nouns = [re.sub(u'([aou]):[\u00e4\u00f6\u00fc]([^<]*)<>:', r'\1\2\t"', x) for x in nouns[:-1]] + [resubstitute(nouns[-1][:-5])]

  # Fix non-umlaut LEs.
  nouns = [re.sub(r'<>:(\w+)$', r'\t=\1', x) for x in nouns[:-1]] + [nouns[-1]]

  # Remaning substitutes.
  nouns = [resubstitute(x) for x in nouns]

  # Fix TRUNCs and ORDs.
  nouns = [re.sub(u'{(.+)}-<TRUNC>', r'\1+++\t', x) for x in nouns]
  nouns = [re.sub(u'}-<TRUNC>{', r'+++\t', x) for x in nouns]
  nouns = [re.sub(r'<ORD>', '~~~~\t', x) for x in nouns]

  # Mark plain Suffixes.
  nouns = [re.sub(u'^([a-zA-Z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df]+)<SUFF>', r'<<<\1', x) for x in nouns]

  # Fix leading <SUFF>
  nouns = [re.sub(r'^<SUFF>', r'', x) for x in nouns]

  # Mark prefixes.
  nouns = [re.sub(r'<PREF>', r'~~~\t', x) for x in nouns]

  # Cleanup.
  nouns = [re.sub(r'<[^>]+>', r'', x) for x in nouns]

  # TODO: Make mixed case

  return nouns

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('infile', help='input from SMOR (gzip)')
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
  ifh = gzip.open(args.infile, 'r')

  c_analyses  = list()
  c_token     = ''

  for l in ifh:
    l = l.decode('utf-8')
    l = l.strip()

    if not l:
      continue

    # Start new word.
    if re.match(r'^> ', l) or l == '>':

      # Save full analyses for later.
      cdata = '<![CDATA[' + '|+|'.join(c_analyses) + ']]>'

      # Remove trailing inflection analysis
      c_analyses = [re.sub(r'(<\+[^>]+>).*$', r'\1', x).replace('<NEWORTH>','').replace('OLDORTH','') for x in c_analyses] 

      # Only get analyses for this as noun.
      nounalyses = [nounalize(x) for x in c_analyses if '<+NN>' in x]

      #print
      #print ' === ' + c_token.encode('utf-8')
      #print
      #print cdata.encode('utf-8')
      #print
      if len(nounalyses) > 0:
        for n in nounalyses:
          if len(n) > 1:
            print ('\t'.join(n)).encode('utf-8')

      # Fresh start.
      c_analyses = list()
      c_token    = re.sub(r'^> ', r'', l)

    else:

      # Only add non-empty analyses.
      if not l == 'no result for':
        c_analyses = c_analyses + [l]

  ofh.close()
  ifh.close()

if __name__ == "__main__":
    main()
