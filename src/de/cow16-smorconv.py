# -*- coding: utf-8 -*-

# Transform SMOR annotation into usable.

import argparse
import os.path
import sys
import gzip
import re

def substitute_nulls(s):
  s = re.sub(u'(?:\w|<[^>]+>):#0#', r'', s, re.UNICODE)
  s = re.sub(u'#0#:(\w)', r'\1', s, re.UNICODE)

  # Some initial :#0# garbage.
  s = re.sub(u'^:#0#', r'', s)
  return s

def fix_fes(s):

  # Unfortunately represented in more complex way (vowel substitution + suffix): Marienbild.
  s = re.sub(u'([a-z]):([a-z])#0#:([a-z])', r'\1\t-\1\t+\2\3', s, re.UNICODE)

  # Pure umlaut, "Mütter".
  s = re.sub(u'([aou]):([äöü])([^#0:]*\w$)', r'\1\3\t+=', s, re.UNICODE)

  # Suffixation with umlaut.
  s = re.sub(u'([aou]):([äöü])(.*)#0#:([a-z])#0#:([a-z])#0#:([a-z])$', r'\1\3\t+=\4\5\6', s, re.UNICODE)
  s = re.sub(u'([aou]):([äöü])(.*)#0#:([a-z])#0#:([a-z])$', r'\1\3\t+=\4\5', s, re.UNICODE)
  s = re.sub(u'([aou]):([äöü])(.*)#0#:([a-z])$', r'\1\3\t+=\4', s, re.UNICODE)

  # Suffixation without umlaut.
  s = re.sub(u'#0#:([a-z])#0#:([a-z])#0#:([a-z])$', r'\t+\1\2\3', s, re.UNICODE)
  s = re.sub(u'#0#:([a-z])#0#:([a-z])$', r'\t+\1\2', s, re.UNICODE)
  s = re.sub(u'#0#:([a-z])$', r'\t+\1', s, re.UNICODE)

  # Deletions.
  s = re.sub(u'([a-zäöü]):#0#([a-zäöü]):#0#([a-zäöü]):#0#(\t|$)', r'\1\2\3\t-\1\2\3\4', s, re.UNICODE)
  s = re.sub(u'([a-zäöü]):#0#([a-zäöü]):#0#(\t|$)', r'\1\2\t-\1\2\3', s, re.UNICODE)
  s = re.sub(u'([a-zäöü]):#0#(\t|$)', r'\1\t-\1\2', s, re.UNICODE)
  return s

def fix_cap(s):
  if '+KAP+' in s:
    s = re.sub(r'\+KAP\+', r'', s).title()
  elif '-KAP-' in s:
    s = re.sub(r'-KAP-', r'', s).lower()
  return s


def nounalize(s):

  # Make zero elements distinguishable from categories.
  s = s.replace(r'<>', r'#0#')

  s = re.sub(u'(?:e:#0#|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>', r'erin+KAP+<+NN>', s, re.UNICODE) # Final "Betreuerin". Needs to be protected before other suffix rules apply.

  # Very specific orthographic ss/ß conversion.
  s = re.sub(u'#0#:sß:s', u'ß', s, re.UNICODE)

  # No distinction between NN and NE.
  s = s.replace(r'<NPROP>', r'<NN>')

  # Rescue original ablaut vowel in V>N derivations. "Annahme(verweigerung)"
  s = re.sub(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w+)n:#0#<V>:#0##0#:n(<\+NN>|<NN>:#0#)<SUFF>:#0#', r'\1\3\4+KAP+\5\t+n\t', s, re.UNICODE) # With LE -n.
  s = re.sub(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w+)n:#0#<V>:#0#(<\+NN>|<NN>:#0#)<SUFF>:#0#', r'\1\3\4+KAP+\5\t', s, re.UNICODE) # Without LE -n.

  # Presevere "missing LE" notification.
  s = re.sub(u'<ADJ>:#0#(\w+)<F>:#0#<NN>:#0#<SUFF>:#0#', r'+KAP+\1\t+0\t', s, re.UNICODE)

  # Undo other suffix analyses.
  s = re.sub(u'<NN>:#0#(?:<SUFF>:#0#|)in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#', r'in+KAP+\t+nen<NN>:#0#', s, re.UNICODE) # "Betreuerinnen"

  #s = re.sub(u'(\w+)<ADJ>:#0#(\w*)<SUFF>:#0#', r'\1\2+KAP+', s, re.UNICODE) # Whatever.

  s = re.sub(u'(?:e:#0#|)n:#0#<V>:#0#(\w+)(#0#:\w+|)<NN>:#0#<SUFF>:#0#', r'\1+KAP+\t+\2\t', s, re.UNICODE)  # "Verlautbarungs" etc. LE gets moved PAST <NN>
  s = re.sub(u'(?:e:#0#|)n:#0#<V>:#0#(\w+)<SUFF>:#0#(?:<NN>|<\+NN>)', r'\1+KAP+\t', s, re.UNICODE) # the same, without LE  

  # This one is critical: there might be more than 'erin'. But it breaks the V compound element detection when (\w+) is used instead of (erin).
  s = re.sub(u'(?:e:#0#|)n:#0#<V>:#0#(erin)', r'\1', s, re.UNICODE) # Leftover: b:Betreue:#0#n:#0#<V>:#0#erin

  s = re.sub(u'(<ADJ>:#0#)(\w+)(#0#:\w+|)<NN>:#0#<SUFF>:#0#', r'\2+KAP+\t+\3\t', s, re.UNICODE)  # "Lieblichkeits" etc. LE gets moved PAST <NN>
  s = re.sub(u'(\w*)([aou]):([äöü])([\w#0:]*)<NN>:#0#(?:<SUFF>:#0#|)(\w+)<SUFF>:#0#', r'\1\3\4\5<NN>:#0#', s, re.UNICODE)      # rescue umlauting suffixes
  s = re.sub(u'<NN>:#0#(?:<SUFF>:#0#|)(\w+)<SUFF>:#0#', r'\1<NN>:#0#', s, re.UNICODE)     # same again w/o umlaut
  s = re.sub(u'<NN>:#0#(\w+)<SUFF>:#0#(<\+NN>|<NN>:#0#)', r'\1\t', s, re.UNICODE)

  s = re.sub(u'(?:e:#0#|)n:#0#<V>:#0#<NN>:#0#<SUFF>:#0#', r'+KAP+\t', s, re.UNICODE) # Satzbau-
  s = re.sub(u'(?:e:#0#|)n:#0#<V>:#0#<SUFF>:#0#<\+NN>', r'+KAP+', s, re.UNICODE)  # The same, final.

  # Remove derivational information which we don't need.
  s = re.sub(u'<VPART>:#0#', u'', s, re.UNICODE)

  # Fix TRUNC.
  s = re.sub(r'{:#0#([^}]+)}:#0#-<TRUNC>:#0#', r'\1\t--\t', s)

  # Separate prefixes and ORD ("Dritt-mittel").
  s = re.sub(u'(\w):(\w)(\w*)(<ORD>|<PREF>):#0#', r'\1\3~\t', s, re.UNICODE)

  # First split. We will join & split again later.
  nouns = re.split(r'<NN>:#0#|\t', s)

  # Separate and mark remaning FEs.
  nouns = [fix_fes(x) for x in nouns]

  # Clean elements containing suffixes.
  nouns = ['+KAP+' + re.sub(u'(?:<[^>]+>|\w):#0#', r'', x, re.UNICODE) if '<SUFF>' in x else x for x in nouns]

  # Split ADJ and V compound elements.
  nouns = [re.sub(u'<ADJ>:#0#', r'-KAP-\t', x, re.UNICODE) for x in nouns]
  nouns = [re.sub(u'e:#0#n:#0#<V>:#0#', r'en-KAP-\t#en\t', x, re.UNICODE) for x in nouns]
  nouns = [re.sub(u'n:#0#<V>:#0#', r'n-KAP-\t#n\t', x, re.UNICODE) for x in nouns]

  # Second split.
  nouns = '\t'.join(nouns).split('\t')

  # Some cleanups.
  nouns = [x.replace('<+NN>', '').strip() if not x == '+' else '' for x in nouns]
  nouns = filter(None, nouns)

  # Do NOT keep umlaut in head noun. Is plural!
  nouns = nouns[:-1] + [re.sub(u'([aou]):([äöü])', r'\1', nouns[-1], re.UNICODE)]

  # Move +KAP+ to end.
  nouns = [re.sub(r'\+KAP\+', r'', x) + '+KAP+' if '+KAP+' in x else x for x in nouns]
  nouns = [re.sub(r'-KAP-', r'', x) + '-KAP-' if '-KAP-' in x else x for x in nouns]

  # Make capitalization substitutions.
  nouns = [re.sub(u'^([a-zäöüA-ZÄÖÜß]):[a-zäöüA-ZÄÖÜß]', r'\1', x, re.UNICODE) for x in nouns]
  nouns = [fix_cap(x) for x in nouns]

  # Clean remaining to/from-NULL substitutions.
  nouns = [substitute_nulls(x) for x in nouns]

  # Make lexicon checks.
  nouns = [x if check_lex(x) else '' for x in nouns]
  nouns = filter(None, nouns)

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
      c_analyses = [re.sub(r'(<\+[^>]+>).*$', r'\1', x).replace('<NEWORTH>','').replace('<OLDORTH>','') for x in c_analyses] 

      # Only get analyses for this as noun.
      nounalyses = [nounalize(x) for x in c_analyses if '<+NN>' in x]

      if len(nounalyses) > 0:
        for n in nounalyses:
          if len(n) > 1:

            # TODO "Disambiguation".

            print c_token.encode('utf-8') + '\t\t',
            print ('\t'.join(n)).encode('utf-8')
            #print ('\t'.join(n)).encode('utf-8') + '\t' + cdata.encode('utf-8')

      # Fresh start.
      c_analyses = list()
      c_token    = re.sub(r'^> ', r'', l)

    else:

      # Only add non-empty analyses.
      if not l == 'no result for':
        c_analyses = c_analyses + [l]

  # TODO Last element is not printed.
  # TODO Also check whether "no analysis" etc. are handled. Consistent Token numbers in in/out.

  ofh.close()
  ifh.close()

if __name__ == "__main__":
    main()
