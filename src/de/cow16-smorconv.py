# -*- coding: utf-8 -*-

# Transform SMOR annotation into usable.

import argparse
import os.path
import sys
import gzip
import re


dict_n = set()
dict_pn = set()
dict_rest = set()

NO_ANNO=['_', '_', '|', '|']

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

  # "Suppletions".
  s = re.sub(u'(\w):(\w)$', r'\1\t-\1\t+\2', s, re.UNICODE)

  # Deletions.
  s = re.sub(u'([a-zäöü]):#0#([a-zäöü]):#0#([a-zäöü]):#0#(\t|$)', r'\1\2\3\t-\1\2\3\4', s, re.UNICODE)
  s = re.sub(u'([a-zäöü]):#0#([a-zäöü]):#0#(\t|$)', r'\1\2\t-\1\2\3', s, re.UNICODE)
  s = re.sub(u'([a-zäöü]):#0#(\t|$)', r'\1\t-\1\2', s, re.UNICODE)
  return s


def fix_cap(s):
  if '+KAP+' in s and '-KAP-' in s:
    s = re.sub(r'\+KAP\+|-KAP-', r'', s, re.UNICODE).lower()
  elif '+KAP+' in s:
    s = re.sub(r'\+KAP\+', r'', s).title()
  elif '-KAP-' in s:
    s = re.sub(r'-KAP-', r'', s).lower()
  return s


def check_lex_single(s):
  global dict_n
  global dict_pn
  global dict_rest
  if re.match(u'^[A-ZÄÖÜ][a-zäöüß]+$', s, re.UNICODE):
    return 1 if s in dict_n or s in dict_pn else 0
  elif re.match(u'^[a-zäöüß]+$', s, re.UNICODE):
    return 1 if s in dict_rest else 0
  else:
    return 1


def check_lex(l):
  lex = [e for e in l if re.match(u'^[A-ZÄÖÜ][a-zäöüß]+$|^[a-zäöüß]+$', e, re.UNICODE)]
  chex = [check_lex_single(e) for e in lex]
  if len(chex) > 0:
    return [int(round(sum(chex)/float(len(chex))*100)), len(lex), len(l)]
  else:
    return [-1, 0, len(l)]



def nounalize(s):
  s = s.strip()

  #print '========================================='

  #print '00\t' + s.encode('utf-8')

  # Make zero elements distinguishable from categories.
  s = s.replace(r'<>', r'#0#')

  #print '01\t' + s.encode('utf-8')

  # Get rid of verb prefic information as early as possible
  s = re.sub(u'(?:<VPART>|<VPREF>):#0#', r'', s, re.UNICODE)

  # Final "Betreuerin". Needs to be protected before other suffix rules apply.
  s = re.sub(u'[aeiouäöü]:([aeiouäöü])(\w*)(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>', r'\1\2\3erin+KAP+<+NN>', s, re.UNICODE)  # with umlaut
  s = re.sub(u'(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>', r'\1erin+KAP+<+NN>', s, re.UNICODE)  # w/o
  
  # For some reason, yet another analysis of the same thing.
  s = re.sub(u'[aeiouäöü]:([aeiouäöü])(\w*)(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#', r'\1\2erin+KAP+\t+nen\t', s, re.UNICODE)  # w/o
  s = re.sub(u'(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#', r'\1erin+KAP+\t+nen\t', s, re.UNICODE)  # w/o

  # Also final:
  #a:äng<NN>:<>ler<NN>:<><SUFF>:<>in<SUFF>:<><+NN>

  #print '02\t' + s.encode('utf-8')

  # Very specific orthographic ss/ß conversions.
  s = re.sub(u'#0#:sß:s', u'ß', s, re.UNICODE)
  s = re.sub(u's:#0#s:s', u'ss', s, re.UNICODE)
  s = re.sub(u's:#0#s:ß:#0#', u'ss', s, re.UNICODE)
  s = re.sub(u's:#0#s#0#:s', u'ss', s, re.UNICODE)
  s = re.sub(u's:#0#s:ß', u'ss', s, re.UNICODE)
  s = re.sub(u's:ßs:#0#', u'ss', s, re.UNICODE)

  #print '03\t' + s.encode('utf-8')

  # No distinction between NN and NE.
  s = s.replace(r'<NPROP>', r'<NN>')

  #print '04\t' + s.encode('utf-8')

  # Rescue original ablaut vowel in V>N derivations. "Annahme(verweigerung)"
  s = re.sub(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w+)(e:#0#|)n:#0#<V>:#0##0#:n(<\+NN>|<NN>:#0#)<SUFF>:#0#', r'\1\3\4+KAP+\6\t+n\t', s, re.UNICODE) # With LE -n.
  s = re.sub(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w+)(e:#0#|)n:#0#<V>:#0#(<\+NN>|<NN>:#0#)<SUFF>:#0#', r'\1\3\4+KAP+\6\t', s, re.UNICODE) # Without LE -n.

  # ... final.
  s = re.sub(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w+)(e:#0#|)n:#0#<V>:#0#(\w+)<SUFF>:#0#<\+NN>', r'\1\3\4\6+KAP+', s, re.UNICODE) # Word-final V>N derivations with umlaut

  # "Mitnahme" final.
  s = re.sub(u'([aeiouäöü]):([aeiouäöü])(\w+)n:#0#<V>:#0#<SUFF>:#0#<\+NN>', r'\2\3+KAP+', s, re.UNICODE)

  # "Anfänger" (middle).
  s = re.sub(u'[aeiouäöü]:([aeiouäöü])(\w*)e:#0#(\w|)n:#0#<V>:#0#(\w+)<NN>:#0#<SUFF>:#0#', r'\1\2\3\4+KAP+\t', s, re.UNICODE)
  s = re.sub(u'e:#0#(\w|)n:#0#<V>:#0#(\w+)<NN>:#0#<SUFF>:#0#', r'\1\2+KAP+\t', s, re.UNICODE)

  #print '05\t' + s.encode('utf-8')

  # Presevere "missing LE" notification.
  s = re.sub(u'<ADJ>:#0#(\w+)<F>:#0#<NN>:#0#<SUFF>:#0#', r'+KAP+\1\t+0\t', s, re.UNICODE)

  #print '06\t' + s.encode('utf-8')

  # "Umzug" from "ziehen". Wow!
  s = re.sub(u'\w:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', r'\1\2', s, re.UNICODE) 
  s = re.sub(u'\w:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', r'\1\2', s, re.UNICODE) 
  s = re.sub(u'\w:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', r'\1\2', s, re.UNICODE) 
  s = re.sub(u'\w:#0#([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', r'\1', s, re.UNICODE) 
  s = re.sub(u'\w:#0#([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', r'\1', s, re.UNICODE) 
  s = re.sub(u'\w:#0#([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', r'\1', s, re.UNICODE) 
  s = re.sub(u'#0#:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', r'\1\2', s, re.UNICODE) 
  s = re.sub(u'#0#:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', r'\1\2', s, re.UNICODE) 
  s = re.sub(u'#0#:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', r'\1\2', s, re.UNICODE) 
  s = re.sub(u'([^<>#]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', r'+KAP+\1', s, re.UNICODE) 

  # The same, final.
  # e:ii:ege:<>n:<><V>:<><SUFF>:<><+NN>
  s = re.sub(u'\w:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', r'\1\2', s, re.UNICODE) 
  s = re.sub(u'\w:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', r'\1\2', s, re.UNICODE) 
  s = re.sub(u'\w:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', r'\1\2', s, re.UNICODE) 
  s = re.sub(u'\w:#0#([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', r'\1', s, re.UNICODE) 
  s = re.sub(u'\w:#0#([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', r'\1', s, re.UNICODE) 
  s = re.sub(u'\w:#0#([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', r'\1', s, re.UNICODE) 
  s = re.sub(u'#0#:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', r'\1\2', s, re.UNICODE) 
  s = re.sub(u'#0#:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', r'\1\2', s, re.UNICODE) 
  s = re.sub(u'#0#:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', r'\1\2', s, re.UNICODE) 
  #s = re.sub(u'([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', r'+KAP+\1', s, re.UNICODE) 

  #print '06 A\t' + s.encode('utf-8')

  s = re.sub(u'[aeiouäöü]:([aeiouäöü])(\w*)<NN>:#0#(\w+)<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#', r'\1\2\3in+KAP+\t+nen\t', s, re.UNICODE) # Dränglerinnen as Drang+ler+in+nen
  # a:äng<NN>:#0#ler<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#

  # N>N derivations "Brauch-tum", "Arbeiterschaft". There should be none with umlaut, and diminutives are dealt w/ sep.
  s = re.sub(u'<NN>:#0#(\w+)#0#:(\w+)<NN>:#0#<SUFF>:#0#', r'\1+KAP+\t+\2\t', s, re.UNICODE) # Bauchtums... // Note: SMOR fails on "Brauchtümerpflege", "Arbeitschaftenvermittlung" etc.
  s = re.sub(u'[aeiouäöü]:([aeiouäöü])(\w*)<NN>:#0#(\w+)<NN>:#0#<SUFF>:#0#', r'\1\2\3+KAP+\t', s, re.UNICODE) # Drängler as Drang+ler
  
  #print '06 B\t' + s.encode('utf-8')

  # Undo other suffix analyses.

  # Firts, rescue the stupid "Rinnen" analyses.
  s = re.sub(u'[aeiouäöü]:([aeiouäöü])(\w*)#0#:e<NN>:#0#R:rinne<\+NN>$', r'\1\2erin+KAP+', s, re.UNICODE) # with umlaut, final
  s = re.sub(u'#0#:e<NN>:#0#R:rinne<\+NN>$', r'erin+KAP+', s, re.UNICODE) # without umlaut, final

  s = re.sub(u'[aeiouäöü]:([aeiouäöü])(\w*)#0#:e<NN>:#0#R:rinne#0#:n<NN>:#0#', r'\1\2erin+KAP+\t+nen\t', s, re.UNICODE) # with umlaut, non-final
  s = re.sub(u'#0#:e<NN>:#0#R:rinne#0#:n<NN>:#0#', r'erin+KAP+\t+nen\t', s, re.UNICODE) # without umlaut, non-final

  s = re.sub(u'<NN>:#0#(?:<SUFF>:#0#|)in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#', r'in+KAP+\t+nen<NN>:#0#', s, re.UNICODE) # "Betreuerinnen"

  # Diminutives.
  s = re.sub(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#:#0#(lein|chen)<NN>:#0#<SUFF>:#0#', r'\1\3\4\6+KAP+\t', s, re.UNICODE)
  s = re.sub(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#(lein|chen)<NN>:#0#<SUFF>:#0#', r'\1\3\4\6+KAP+\t', s, re.UNICODE)

  # ... final.
  s = re.sub(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#:#0#(lein|chen)<SUFF>:#0#<\+NN>', r'\1\3\4\6+KAP+\t', s, re.UNICODE)
  s = re.sub(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#(lein|chen)<SUFF>:#0#<\+NN>', r'\1\3\4\6+KAP+\t', s, re.UNICODE)

  #print '07\t' + s.encode('utf-8')

  s = re.sub(u'(?:e:#0#|)([^aeiouäöü]|)n:#0#<V>:#0#(\w+)<F>:#0#<NN>:#0#<SUFF>:#0#', r'\1\2+KAP+\t+0\t', s, re.UNICODE) # Versammlungverbot with missing LE.
  s = re.sub(u'<V>:#0#(\w+)#0#:(\w+)<NN>:#0#<SUFF>:#0#', r'\1+KAP+\t+\2\t', s, re.UNICODE) # Versammlungsverbot with correct LE. V-stem internal replacements done already (above).

  # Likely obsolete because general V-stem internal substitutions and two lines directly above do the same job better.
  #s = re.sub(u'(?:e:#0#|)(.|)n:#0#<V>:#0#(\w+)(#0#:\w+|)<NN>:#0#<SUFF>:#0#', r'\1\2+KAP+\t+\3\t', s, re.UNICODE)  # "Verlautbarungs" etc. LE gets moved PAST <NN>
  #s = re.sub(u'(?:e:#0#|)(.|)n:#0#<V>:#0#(\w+)<SUFF>:#0#(?:<NN>|<\+NN>)', r'\1\2+KAP+\t', s, re.UNICODE) # the same, without LE  

  #print '08\t' + s.encode('utf-8')

  # This one is critical: there might be more than 'erin'. But it breaks the V compound element detection when (\w+) is used instead of (erin).
  s = re.sub(u'(?:e:#0#|)n:#0#<V>:#0#(erin)', r'\1', s, re.UNICODE) # Leftover: b:Betreue:#0#n:#0#<V>:#0#erin

  #print '09\t' + s.encode('utf-8')

  s = re.sub(u'(<ADJ>:#0#)(\w+)(#0#:\w+|)<NN>:#0#<SUFF>:#0#', r'\2+KAP+\t+\3\t', s, re.UNICODE)  # "Lieblichkeits" etc. LE gets moved PAST <NN>
  s = re.sub(u'(\w*)([aou]):([äöü])([\w#0:]*)<NN>:#0#(?:<SUFF>:#0#|)(\w+)<SUFF>:#0#', r'\1\3\4\5<NN>:#0#', s, re.UNICODE)      # rescue umlauting suffixes
  s = re.sub(u'<NN>:#0#(?:<SUFF>:#0#|)(\w+)<SUFF>:#0#', r'\1<NN>:#0#', s, re.UNICODE)     # same again w/o umlaut
  s = re.sub(u'<NN>:#0#(\w+)<SUFF>:#0#(<\+NN>|<NN>:#0#)', r'\1\t', s, re.UNICODE)

  #print '10\t' + s.encode('utf-8')

  s = re.sub(u'(?:e:#0#|)n:#0#<V>:#0#<NN>:#0#<SUFF>:#0#', r'+KAP+\t', s, re.UNICODE) # Satzbau-
  s = re.sub(u'(?:e:#0#|)n:#0#<V>:#0#<SUFF>:#0#<\+NN>', r'+KAP+', s, re.UNICODE)  # The same, final.

  #print '11\t' + s.encode('utf-8')

  # Remove derivational information which we don't need.
  s = re.sub(u'<VPART>:#0#', u'', s, re.UNICODE)

  #print '12\t' + s.encode('utf-8')

  # Fix TRUNC.
  s = re.sub(r'{:#0#([^}]+)}:#0#-<TRUNC>:#0#', r'\1\t--\t', s)

  #print '13\t' + s.encode('utf-8')

  # Separate prefixes and ORD ("Dritt-mittel").
  s = re.sub(u'(\w):(\w)(\w*)(<ORD>|<PREF>):#0#', r'\1\3~\t', s, re.UNICODE)  # initial, make lower case
  s = re.sub(u'(?:<ORD>|<PREF>):#0#', r'~\t', s, re.UNICODE)  # not initial, just insert boundary

  #print '13 A\t' + s.encode('utf-8')

  # Some derivational affixes.
  s = re.sub(u'<NN>:#0#(\w+)<ADJ>:#0#<SUFF>:#0#', r'\1-KAP-\t', s, re.UNICODE)
  s = re.sub(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<NN>:#0#<SUFF>:#0#', r'\1\2\3+KAP+\t', s, re.UNICODE)
  s = re.sub(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<ADJ>:#0#<SUFF>:#0#', r'\1\2\3-KAP-\t', s, re.UNICODE)
  s = re.sub(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<V>:#0#<SUFF>:#0#', r'\1\2\3-KAP-\t', s, re.UNICODE)
  s = re.sub(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<NN>:#0#<SUFF>:#0#', r'\1\2+KAP+\t', s, re.UNICODE)
  s = re.sub(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<ADJ>:#0#<SUFF>:#0#', r'\1\2-KAP-\t', s, re.UNICODE)
  s = re.sub(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<V>:#0#<SUFF>:#0#', r'\1\2-KAP-\t', s, re.UNICODE)
  s = re.sub(u'<[A-Z]+>:#0#(\w+)<NN>:#0#<SUFF>:#0#', r'\1+KAP+\t', s, re.UNICODE)
  s = re.sub(u'<[A-Z]+>:#0#(\w+)<ADJ>:#0#<SUFF>:#0#', r'\1-KAP-\t', s, re.UNICODE)
  s = re.sub(u'<[A-Z]+>:#0#(\w+)<V>:#0#<SUFF>:#0#', r'\1-KAP-\t', s, re.UNICODE)

  #print '14\t' + s.encode('utf-8')

  # First split. We will join & split again later.
  nouns = re.split(r'<NN>:#0#|\t|<ADJ>:#0#', s)

  #print '15\t' + "\t".join(nouns).encode('utf-8')

  # Separate and mark remaning FEs.
  nouns = [fix_fes(x) for x in nouns]

  #print '16\t' + "\t".join(nouns).encode('utf-8')

  # Clean elements containing suffixes.
  nouns = ['+KAP+' + re.sub(u'(?:<[^>]+>|\w):#0#', r'', x, re.UNICODE) if '<SUFF>' in x else x for x in nouns]

  #print '17\t' + "\t".join(nouns).encode('utf-8')

  # Split ADJ and V compound elements.
  nouns = [re.sub(u'<ADJ>:#0#', r'-KAP-\t', x, re.UNICODE) for x in nouns]
  nouns = [re.sub(u'e:#0#n:#0#<V>:#0#', r'en-KAP-\t#en\t', x, re.UNICODE) for x in nouns]
  nouns = [re.sub(u'n:#0#<V>:#0#', r'n-KAP-\t#n\t', x, re.UNICODE) for x in nouns]

  #print '18\t' + "\t".join(nouns).encode('utf-8')

  # Second split.
  nouns = '\t'.join(nouns).split('\t')

  #print '19\t' + "\t".join(nouns).encode('utf-8')

  # Some cleanups.
  nouns = [x.replace('<+NN>', '').strip() if not x == '+' else '' for x in nouns]
  nouns = [re.sub(r'^:#0#', r'', n, re.UNICODE) for n in nouns]

  #print '20\t' + "\t".join(nouns).encode('utf-8')

  # Do NOT keep umlaut in head noun. Is plural!
  nouns = nouns[:-1] + [re.sub(u'([aou]):([äöü])', r'\1', nouns[-1], re.UNICODE)]

  #print '21\t' + "\t".join(nouns).encode('utf-8')

  # Move +KAP+ to end.
  nouns = [re.sub(r'\+KAP\+', r'', x) + '+KAP+' if '+KAP+' in x else x for x in nouns]
  nouns = [re.sub(r'-KAP-', r'', x) + '-KAP-' if '-KAP-' in x else x for x in nouns]

  #print '22\t' + "\t".join(nouns).encode('utf-8')

  # Make capitalization substitutions.
  nouns = [re.sub(u'^([a-zäöüA-ZÄÖÜß]):[a-zäöüA-ZÄÖÜß]', r'\1', x, re.UNICODE) for x in nouns]
  nouns = [fix_cap(x) for x in nouns]

  #print '23\t' + "\t".join(nouns).encode('utf-8')

  # Clean remaining to/from-NULL substitutions.
  nouns = [substitute_nulls(x) for x in nouns]

  #print '24\t' + "\t".join(nouns).encode('utf-8')

  # Compact.
  nouns = filter(None, nouns)

  #print '25\t' + "\t".join(nouns).encode('utf-8')

  return [nouns] + check_lex(nouns)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('infile', help='input from SMOR (gzip)')
  parser.add_argument('outfile', help='output file name (gzip)')
  parser.add_argument('nouns', help='noun dictionary file name (gzip)')
  parser.add_argument('names', help='name dictionary file name (gzip)')
  parser.add_argument('rest', help='verb, adjective, etc. dictionary file name (gzip)')
  parser.add_argument("--nounlim", type=int, help="only use the first <this number> of nouns from list")
  parser.add_argument("--namelim", type=int, default=10000, help="only use the first <this number> of names from list")
  parser.add_argument("--restlim", type=int, help="only use the first <this number> of non-noun lemmas from list")
  parser.add_argument("--lexperc", default=67, type=int, help="percentage of lexical items required to be known in lexicon")
  parser.add_argument("--erase", action='store_true', help="erase outout files if present")
  args = parser.parse_args()

  # Check input files.
  infiles = [args.infile, args.nouns, args.names, args.rest]
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
  global dict_n
  global dict_pn
  global dict_rest
  fh_dict = gzip.open(args.nouns)
  counter = 0
  for l in fh_dict:
    counter = counter + 1
    dict_n.add(l.decode('utf-8').strip())
    if args.nounlim and counter >= args.nounlim:
      break
  fh_dict.close()

  fh_dict = gzip.open(args.names)
  counter = 0
  for l in fh_dict:
    counter = counter + 1
    dict_pn.add(l.decode('utf-8').strip())
    if args.namelim and counter >= args.namelim:
      break
  fh_dict.close()

  fh_dict = gzip.open(args.rest)
  counter = 0
  for l in fh_dict:
    counter = counter + 1
    dict_rest.add(l.decode('utf-8').strip())
    if args.restlim and counter >= args.restlim:
      break
  fh_dict.close()

  ofh = gzip.open(args.outfile, 'wb')
  ifh = gzip.open(args.infile, 'r')

  c_analyses  = list()
  c_token     = ''

  while True:
    l = ifh.readline().decode('utf-8')

    # Start new word.
    if re.match(r'^> ', l) or l == '>' or not l:

      if len(c_analyses) > 0 and c_token:

          # Save full analyses for later.
          cdata = '<![CDATA[' + ' '.join(c_analyses) + ']]>'
    
          # Remove trailing inflection analysis and useless ORTH info.
          c_analyses = [re.sub(r'(<\+[^>]+>).*$', r'\1', x).replace('<NEWORTH>','').replace('<OLDORTH>','') for x in c_analyses] 

          # Only get analyses for this as noun.
          nounalyses = [nounalize(x) for x in c_analyses if '<+NN>' in x]

          # Eliminate analyses below required lexical sanity level.
          # Also: Only use analyses with the best possible lexical score.
          if len(nounalyses) > 1:
            lex_max = max([a[1] for a in nounalyses])
            nounalyses = [e for e in nounalyses if len(e) > 0 and e[1] >= args.lexperc and e[1] == lex_max]
    
          # One lexical item means "not compound". Get rid.
          nounalyses = [e for e in nounalyses if e[2] > 1]

          # Remove awful "Rinnen" analyses for "movierte" nouns.
          if len(nounalyses) > 0 and re.match(u'.+rinnen$', c_token, re.UNICODE):
            nounalyses = [e for e in nounalyses if len(e) > 0 and not e[0][-1] == 'Rinne' ]

          # Remove "Chen"-Analyses of diminutives. Should not occur anymore, but to be safe.
          if len(nounalyses) > 0:
            nounalyses = [e for e in nounalyses if len(e) > 0 and not 'Chen' in set([0]) ]

          # If there are still multiple analyses left, use the ones with the least no. of lexical items. 
          if len(nounalyses) > 1:
            lex_item_min = min([a[2] for a in nounalyses])
            nounalyses = [e for e in nounalyses if e[2] <= lex_item_min]
          
          # If there are still multiple analyses left, use the ones with the least no. of items. 
          if len(nounalyses) > 1:
            lex_item_min = min([a[3] for a in nounalyses])
            nounalyses = [e for e in nounalyses if e[3] <= lex_item_min]

          # Out of criteria. Just use the first f there is at least one analysis or empty annotation if non.
          # First case: Work around > token problem. Requires > tokens to be transformed to GÖTÖBLÄNKK before smor-infl run.
          if c_token == u'GÖTÖBLÄNKK':
            annotation = '\t'.join([u'>'] + NO_ANNO)
          elif len(nounalyses) > 0:
            lexies = [e for e in nounalyses[0][0] if re.match(u'^[a-zA-ZäöüÄÖÜß]+$', e, re.UNICODE)]
            fugies = [e[1:] for e in nounalyses[0][0] if re.match(u'^\+', e, re.UNICODE)]
            fugiestring = '|'+'|'.join(fugies)+'|' if len(fugies)>0 else '|'
            annotation = '\t'.join([c_token, '_'.join(nounalyses[0][0]), lexies[-1], '|'+'|'.join(lexies[:-1])+'|', fugiestring])
          elif not c_token == '>':
            annotation = '\t'.join([c_token] + NO_ANNO)
          else:
            annotation = ''

          ofh.write(annotation.encode('utf-8') + '\n')

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
