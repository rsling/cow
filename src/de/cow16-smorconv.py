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

rexe = dict()

def rr(regex):
  global rexe
  if not regex in rexe:
    rexe[regex] = re.compile(regex, re.UNICODE)
  return rexe[regex]


NO_ANNO=['_', '_', '|', '|']

DEBUG = 4

def debug(s, l = 1):
  if l >= DEBUG:
    print s.encode('utf-8')

def substitute_nulls(s):
  s = rr(u'(?:[a-zäöüßA-ZÄÖÜ]|<[^>]+>):#0#').sub(r'', s)
  s = rr(u'#0#:([a-zäöüßA-ZÄÖÜ])').sub(r'\1', s)

  # Some initial :#0# garbage.
  s = rr(u'^:#0#').sub(r'', s)
  return s


def fix_fes(s):
  # ...ismen as letters to 0 and 0 to letters in blocks.
  s = rr(u'([a-zäöüß]):#0#([a-zäöüß]):#0##0#:([a-zäöüß])#0#:([a-zäöüß])').sub(r'\1\2\t-\1\2\t+\3\4\t', s)

  # Mechanismus > en etc. as letter against letter replacement.
  s = rr(u'([a-zäöüß]):([a-zäöüß])([a-zäöüß]):([a-zäöüß])$').sub(r'\1\3\t-\1\3\t+\2\4\t', s)

  # Unfortunately represented in more complex way (vowel substitution + suffix): Marienbild.
  s = rr(u'([a-z]):([a-z])#0#:([a-z])').sub(r'\1\t-\1\t+\2\3', s)

  # Pure umlaut, "Mütter".
  s = rr(u'([aou]):([äöü])([^#0:]*\w$)').sub(r'\1\3\t+=', s)

  # Suffixation with umlaut.
  s = rr(u'([aou]):([äöü])(.*)#0#:([a-z])#0#:([a-z])#0#:([a-z])$').sub(r'\1\3\t+=\4\5\6', s)
  s = rr(u'([aou]):([äöü])(.*)#0#:([a-z])#0#:([a-z])$').sub(r'\1\3\t+=\4\5', s)
  s = rr(u'([aou]):([äöü])(.*)#0#:([a-z])$').sub(r'\1\3\t+=\4', s)

  # Suffixation without umlaut.
  s = rr(u'#0#:([a-z])#0#:([a-z])#0#:([a-z])$').sub(r'\t+\1\2\3', s)
  s = rr(u'#0#:([a-z])#0#:([a-z])$').sub(r'\t+\1\2', s)
  s = rr(u'#0#:([a-z])$').sub(r'\t+\1', s)

  # "Suppletions".
  s = rr(u'(\w):(\w)$').sub(r'\1\t-\1\t+\2', s)

  # Deletions.
  s = rr(u'([a-zäöü]):#0#([a-zäöü]):#0#([a-zäöü]):#0#(\t|$)').sub(r'\1\2\3\t-\1\2\3\4', s)
  s = rr(u'([a-zäöü]):#0#([a-zäöü]):#0#(\t|$)').sub(r'\1\2\t-\1\2\3', s)
  s = rr(u'([a-zäöü]):#0#(\t|$)').sub(r'\1\t-\1\2', s)
  return s


def fix_cap(s):
  
  # Some heuristics.
  s = rr(u'^([a-zäöüA-ZÄÖÜß]):[a-zäöüA-ZÄÖÜß]').sub(r'\1', s)
  s = rr(u'([a-zäöüßA-ZÄÖÜ])[A-ZÄÖÜ]:([a-zäöü])').sub(r'\1\2', s)

  # Fix the ablaut in strong verbs.
  if '+ABL+' in s:
    s = rr(u'[aeiouäöü]:').sub(r'', s)
    s = s.replace('+ABL+', '')

  # Now the KAP stuff.
  if '+KAP+' in s and '-KAP-' in s:
    s = rr(r'\+KAP\+|-KAP-').sub(r'', s).lower()
  elif '+KAP+' in s:
    s = rr(r'\+KAP\+').sub(r'', s).title()
  elif '-KAP-' in s:
    s = rr(r'-KAP-').sub(r'', s).lower()

  return s


def check_lex_single(s):
  global dict_n
  global dict_pn
  global dict_rest
  if rr(u'^[A-ZÄÖÜ][a-zäöüß]+$').match(s):
    return 1 if s in dict_n or s in dict_pn else 0
  elif rr(u'^[a-zäöüß]+$').match(s):
    return 1 if s in dict_rest else 0
  else:
    return 1

# Returns for a list of: [0] lex percentage, [1] lex count, [2] total count
def check_lex(l):
  lex = [e for e in l if rr(u'^[A-ZÄÖÜ][a-zäöüß]+$|^[a-zäöüß]+$').match(e)]
  chex = [check_lex_single(e) for e in lex]
  if len(chex) > 0:
    return [int(round(sum(chex)/float(len(chex))*100)), len(lex), len(l)]
  else:
    return [-1, 0, len(l)]


def is_lexically_sane(e):
  if e[2] < 3:
    return False if e[1] < 50 else True
  else:
    return False if e[1] < 67 else True
     


def nounalize(s):
  s = s.strip()

  debug('=========================================', 2)

  debug('00\t' + s, 2)

  # Make zero elements distinguishable from categories.
  s = s.replace(r'<>', r'#0#')

  debug('01\t' + s, 2)

  # (ver)dreifach(en)
  s = s.replace(u'<CARD>:#0#fach<ADJ>:#0#<SUFF>:#0#', u'fach')

  # zehntel with <ORD>
  s = s.replace(u'<ORD>:#0#el<ADJ>:#0#<SUFF>:#0#', u'el-KAP-\t')

  # (lieb)ens(wert)
  s = s.replace(u'e:#0#n:#0#<V>:#0#<SUFF>:#0##0#:e#0#:n#0#:s<NN>:#0#<SUFF>:#0#', u'en-KAP-\t+s\t')
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:e#0#:n#0#:s<NN>:#0#<SUFF>:#0#', u'en-KAP-\t+s\t')

  # At least 'Alltagsbewusstsein' is effed up somehow by SMOR.
  s = s.replace(u'sein:#0#<+NN>', u'sein<+NN>')

  # Same with "missbrauch"
  s = s.replace(u'auch:#0#<+NN>', u'auch<+NN>')

  # Very specific lexical defect of SMOR: does not know plural of "Ausfall".
  s = s.replace(u'aus<VPART>:#0#fa:älle:#0#n:#0#<V>:#0#<SUFF>:#0#<+NN>', u'\tAusfall')
  s = s.replace(u'aus<VPART>:#0#fälle:#0#n:#0#<V>:#0##0#:e#0#:n<SUFF>:#0#<+NN>', u'\tAusfall')

  debug('01 B\t' + s, 2)

  # Remove "Schreibweise" tags.
  s = rr(u'<Simp>:#0#|<UC>:#0#|<SS>:#0#').sub(r'', s)

  # Get rid of verb prefix information as early as possible
  s = rr(u'([a-z]):([A-Z])([a-zäöüß]+)(?:<VPART>|<VPREF>):#0#').sub(r'\1\3', s)
  s = rr(u'(?:<VPART>|<VPREF>):#0#').sub(r'', s, re.UNICODE)

  # Cardinals can also be fixed at beginning.
  # ... with extra rules first to fix misanalyses of "Neunziger" etc.
  s = rr(u'<CARD>:#0#er<SUFF>:#0#<\+NN>').sub(r'er+KAP+', s)
  s = rr(u'<CARD>:#0#er<NN>:#0#<SUFF>:#0#').sub(r'er+KAP+\t', s)
  
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)<CARD>:#0#([a-zäöüß]+)<ADJ>:#0#<SUFF>:#0#').sub(r'\t\1\2-KAP-\t', s) # "dreifach" and similar derivations
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)<CARD>:#0#').sub(r'\t\1-KAP-\t', s)

  # Röntgen misanalyses.
  s = s.replace(u'r:Röntge:#0#n:#0#<V>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', u'Röntgen+KAP+\t')
  s = s.replace(u'röntge:#0#n:#0#<V>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', u'Röntgen+KAP+\t')

  debug('01 C\t' + s, 2)

  # Final "Betreuerin". Needs to be protected before other suffix rules apply.
  s = rr(u'[aeiouäöü]:([aeiouäöü])(\w*)(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>').sub(r'\1\2\3erin+KAP+<+NN>', s) # with umlaut
  s = rr(u'(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>').sub(r'\1erin+KAP+<+NN>', s) # w/o

  # Klässlerinnen, Klässlerin, Klässler (non-last)
  s = rr(u'[aou]:([äöü])([a-zäöüß:#0]+)<NN>:#0#([a-zäöüß]+)<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1\2\3in+KAP+\t+en\t', s)
  s = rr(u'[aou]:([äöü])([a-zäöüß:#0]+)<NN>:#0#:#0#([a-zäöüß]+)<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>').sub(r'\1\2\3in+KAP+', s)
  s = rr(u'[aou]:([äöü])([a-zäöüß:#0]+)<NN>:#0#([a-zäöüß]+)<NN>:#0#<SUFF>:#0#').sub(r'\1\2\3+KAP+\t', s)

  # Grobmotorikerin (triple NN suffixation).
  s = rr(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>').sub(r'\1\2in+KAP+<+NN>', s)
  s = rr(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#in<SUFF>:#0##0#:n#0#:e#0#:n<\+NN>').sub(r'\1\2in+KAP+<+NN>', s)
  s = rr(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1\2in+KAP+\t+en\t', s)

  # Journalistin, Frauenrechtlerin etc. (double NN suffixation)
  s = rr(u'<NN>:#0#([a-zäöü]+)<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>').sub(r'\1in+KAP+<+NN>', s)
  s = rr(u'<NN>:#0#([a-zäöü]+)<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1in+KAP+\t+en\t', s)
 
  # For some reason, yet another analysis of the same thing.
  s = rr(u'[aeiouäöü]:([aeiouäöü])(\w*)(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1\2erin+KAP+\t+en\t', s)
  s = rr(u'(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1erin+KAP+\t+en\t', s)

  # ... and for some reason, Touristinnen still fails.
  s = s.replace(u'<NN>:#0#ist<NN>:#0#<SUFF>:#0#in<SUFF>:#0##0#:n#0#:e#0#:n<+NN>', u'istin+KAP+')

  debug('02\t' + s)

  # Very specific orthographic ss/ß conversions.
  s = s.replace(u'#0#:sß:s', u'ß')
  s = s.replace(u's:#0#s:s', u'ss')
  s = s.replace(u's:#0#s:ß:#0#', u'ss')
  s = s.replace(u's:#0#s#0#:s', u'ss')
  s = s.replace(u's:#0#s:ß', u'ss')
  s = s.replace(u's:ßs:#0#', u'ss')
  s = s.replace(u's:#0#s#0#:s', 'ss')

  # sometimes <ADJ>:#0#:#0#
  s = s.replace(u'>:#0#:#0#', '>:#0#')
 
  debug('03\t' + s)

  # No distinction between NN and NE.
  s = s.replace(r'<NPROP>', r'<NN>')

  debug('04\t' + s)

  # Rescue original ablaut vowel in V>N derivations. "Annahme(verweigerung)"
  s = rr(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w+)(e:#0#|)n:#0#<V>:#0##0#:n(<\+NN>|<NN>:#0#)<SUFF>:#0#').sub(r'\1\3\4+KAP+\6\t+n\t', s)
  s = rr(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w+)(e:#0#|)n:#0#<V>:#0#(<\+NN>|<NN>:#0#)<SUFF>:#0#').sub(r'\1\3\4+KAP+\6\t', s)
  debug('04 A\t' + s)

  # ... final.
  s = rr(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w+)(e:#0#|)n:#0#<V>:#0#(\w+)<SUFF>:#0#<\+NN>').sub(r'\1\3\4\6+KAP+', s)
  debug('04 B\t' + s)

  # ... and deal with loan word plurals in final elements.
  s = rr(u'([a-zäöüß]):#0#([a-zäöüß]):#0##0#:e#0#:n<\+NN>').sub(r'\1\2+KAP+', s)

  s = rr(u'([a-zäöüß]):#0##0#:e#0#:n<\+NN>').sub(r'\1', s)
  s = rr(u'([a-zäöüß]):e([a-zäöüß]):n<\+NN>').sub(r'\1\2', s)
  debug('04 C\t' + s)

  # "Mitnahme" final.
  s = rr(u'([aeiouäöü]):([aeiouäöü])(\w+)n:#0#<V>:#0#<SUFF>:#0#<\+NN>').sub(r'\2\3+KAP+', s)

  # "Anfänger" (middle).
  s = rr(u'[aeiouäöü]:([aeiouäöü])(\w*)e:#0#(\w|)n:#0#<V>:#0#(\w+)<NN>:#0#<SUFF>:#0#').sub(r'\1\2\3\4+KAP+\t', s)
  s = rr(u'e:#0#(\w|)n:#0#<V>:#0#(\w+)<NN>:#0#<SUFF>:#0#').sub(r'\1\2+KAP+\t', s)

  debug('05\t' + s)

  # Presevere "missing LE" notification.
  s = rr(u'<ADJ>:#0#(\w+)<F>:#0#<NN>:#0#<SUFF>:#0#').sub(r'+KAP+\1\t+0\t', s)
 
  # Save KSF elements... Whatever.
  s = rr(u'([a-zäöüA-ZÄÖÜß:]+)<KSF>:#0#').sub(r'\t\1\t', s)

  debug('05 A\t' + s)

  # Lebendigkeit/s
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:e#0#:n#0#:d<PPres>:#0#<ADJ>:#0#<SUFF>:#0#igkeit<SUFF>:#0#<+NN>', u'endigkeit+KAP+')
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:e#0#:n#0#:d<PPres>:#0#<ADJ>:#0#<SUFF>:#0#igkeit#0#:s<NN>:#0#<SUFF>:#0#', u'endigkeit+KAP+\t+s\t')

  # Abgegklärtheit/s
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0#heit<SUFF>:#0#<+NN>', u'theit+KAP+')
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0#heit#0#:s<NN>:#0#<SUFF>:#0#', u'theit+KAP+\t+s\t')

  # ...gebliebenen.
  s = rr(u'#0#:g#0#:e([a-zäöü]+)#0#:iei:#0#([a-zäöü]+)e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'\tge\1ie\2en-KAP-', s)
  s = rr(u'#0#:g#0#:e([a-zäöü]+)#0#:iei:#0#([a-zäöü]+)e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\tge\1ie\2en-KAP-\t+en\t', s)

  # ausgeglichen
  s = rr(u'e:#0#i([a-zäöüß]+)e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0#([a-zäöüß]+)<SUFF>:#0#').sub(r'i\1en\2+KAP+', s)
  s = rr(u'e:#0#i([a-zäöüß]+)e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0#').sub(r'i\1en', s)

  # Bezogenheit
  s = s.replace(u'i:oe:gh:#0#e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0#heit<SUFF>:#0#<+NN>', u'ogenheit+KAP+')
  s = s.replace(u'i:oe:gh:#0#e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0#heit#0#:s<NN>:#0#<SUFF>:#0#', u'ogenheit+KAP+\t+s\t')

  # ausgewogen
  s = s.replace(u'i:oe:#0#', u'o')

  # verzerrt
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0#', u't-KAP-\t')

  # auszubildend
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:e#0#:n#0#:d<PPres>:#0#<zu>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', u'end\t+en\t')
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:e#0#:n#0#:d<PPres>:#0#<zu>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#', u'end')
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:e#0#:n#0#:d<PPres>:#0#<ADJ>:#0#<SUFF>:#0#', u'end-KAP-\t')

  debug('06\t' + s, 2)

  # Abschrift 
  s = s.replace(u'e:#0#ib:f#0#:te:#0#n:#0#<V>:#0#<SUFF>:#0#', u'ift+KAP+')
  s = s.replace(u'e:#0#ib:f#0#:te:#0#n:#0#<V>:#0#', u'ift+KAP+')

  # Riss
  s = s.replace(u'e:#0#iß:se:#0#n:#0#<V>:#0##0#:s<NN>:#0#', u'iss+KAP+\t')

  # Mitschnitt
  s = s.replace(u'e:#0#id:t#0#:te:#0#n:#0#<V>:#0#<SUFF>:#0#', u'itt+KAP+')
  s = s.replace(u'e:#0#id:t#0#:te:#0#n:#0#<V>:#0#', u'itt+KAP+')
 
  # Abriss etc. derived from verb. Ugh.
  s = s.replace(u'e:#0#iß:se:#0#n:#0#<V>:#0##0#:s<NN>:#0#<SUFF>:#0#:#0#', u'iss+KAP+\t')
  s = s.replace(u'e:#0#iß:se:#0#n:#0#<V>:#0#<SUFF>:#0#:s<+NN>', u'iss+KAP+')
  s = s.replace(u'e:#0#iße:#0#n:#0#<V>:#0#<SUFF>:#0#:#0#<+NN>', u'iss+KAP+')

  # Stieg
  s = s.replace(u'e:ii:e', u'ie')

  # "Umzug" from "ziehen". Wow!
  s = rr(u'\w:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)').sub(r'\1\2', s)
  s = rr(u'\w:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)').sub(r'\1\2', s)
  s = rr(u'\w:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)').sub(r'\1\2', s)
  s = rr(u'\w:#0#([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)').sub(r'\1', s)
  s = rr(u'\w:#0#([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)').sub(r'\1', s)
  s = rr(u'\w:#0#([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)').sub(r'\1', s)
  s = rr(u'#0#:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)').sub(r'\1\2', s)
  s = rr(u'#0#:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)').sub(r'\1\2', s)
  s = rr(u'#0#:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)').sub(r'\1\2', s)
  s = rr(u'([^<>#]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)').sub(r'+KAP+\1', s)

  s = s.replace(u'i:ue:#0#h:g', u'ug+KAP+\t') # Einzug from ziehen.

  # "Amerikanisierung"
  s = rr(u'#0#:([a-zäöüß])<NN>:#0#is<V>:#0#<SUFF>:#0#ier<V>:#0#<SUFF>:#0#ung<SUFF>:#0#<\+NN>').sub(r'\1isierung+KAP+', s)
  s = rr(u'#0#:([a-zäöüß])<NN>:#0#is<V>:#0#<SUFF>:#0#ier<V>:#0#<SUFF>:#0#ung').sub(r'\1isierung', s)
  debug('06 a\t' + s, 2)

  # "Stoß" as 0-derivation, final.
  s = rr(u'e:#0#n:#0#<V>:#0#<SUFF>:#0#<\+NN>').sub(r'+KAP+', s)
  s = rr(u'n:#0#<V>:#0#<SUFF>:#0#<\+NN>').sub(r'+KAP+', s)

  debug('06 A\t' + s, 2)

  # The same, final.
  s = rr(u'\w:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)').sub(r'\1\2', s)
  s = rr(u'\w:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)').sub(r'\1\2', s)
  s = rr(u'\w:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)').sub(r'\1\2', s)
  s = rr(u'\w:#0#([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)').sub(r'\1', s)
  s = rr(u'\w:#0#([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)').sub(r'\1', s)
  s = rr(u'\w:#0#([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)').sub(r'\1', s)
  s = rr(u'#0#:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)').sub(r'\1\2', s)
  s = rr(u'#0#:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)').sub(r'\1\2', s)
  s = rr(u'#0#:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)').sub(r'\1\2', s)

  # verdrossen
  s = s.replace(u'i:oe:sß:s', u'oss')

  # beschrieben
  s = s.replace(u'#0#:iei:#0#', u'ie')

  debug('06 B\t' + s, 2)

  # Verdrossenheits...
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0#heit#0#:s<NN>:#0#<SUFF>:#0#', u'enheit+KAP+\t+s\t')

  # Very specific V > PP > Adj > NN word formation. Final and non-final "Anspruchsberechtigte" etc. (also strong verbs).
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'\t\1\2\3en-KAP-+ABL+\t', s)
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0#([a-zäöüß]+)<SUFF>:#0#<\+NN>').sub(r'\t\1\2\3en\4+KAP++ABL+\t', s)
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0#').sub(r'\t\1\2\3en-KAP-+ABL+\t', s)
  debug('06 Ba\t' + s)

  s = rr(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)e:#0#n:#0#<V>:#0##0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\t\1\2\3t-KAP-\t+en\t', s)
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)e:#0#n:#0#<V>:#0##0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'\t\1\2\3t-KAP-\t', s)
  debug('06 Bb\t' + s)

  s = rr(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)n:#0#<V>:#0##0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'\t\1\2\3t-KAP-\t', s)
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)n:#0#<V>:#0##0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\t\1\2\3t-KAP-\t+en\t', s)
  debug('06 Bc\t' + s)

  s = rr(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)e:#0#n:#0#<V>:#0##0#:e#0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'\t\1\2\3et-KAP-\t', s)
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)e:#0#n:#0#<V>:#0##0#:e#0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\t\1\2\3et-KAP-\t+en\t', s)
  debug('06 Bd\t' + s)

  # ADJ > NN with l stems "Dunkles".
  s = rr(u'e:#0#l<ADJ>:#0#<SUFF>:#0#<\+NN>').sub(r'el-KAP-', s)
  s = rr(u'e:#0#l<ADJ>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'el-KAP-\t+en\t', s)

  # No idea why this goes wrong otherwise: "Bodybuildingbegeistert".
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)<ADJ>:#0#<SUFF>:#0#<\+NN>').sub(r'\t\1-KAP-', s)

  debug('06 C\t' + s, 2)

  s = rr(u'e:#0#n:#0#<V>:#0##0#:e#0#:n#0#:d<PPres>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'end-KAP-', s)
  s = rr(u'n:#0#<V>:#0##0#:n#0#:d<PPres>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'nd-KAP-', s)
  s = rr(u'([a-zäöüA-ZÄÖÜß:]+)e:#0#n:#0#<V>:#0##0#:e#0#:n#0#:d<PPres>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1end-KAP-\t+en\t', s)
  s = rr(u'([a-zäöüA-ZÄÖÜß:]+)n:#0#<V>:#0##0#:n#0#:d<PPres>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1nd-KAP-\t+en\t', s)

  debug('06 D\t' + s, 2)

  s = rr(u'[aeiouäöü]:([aeiouäöü])(\w*)<NN>:#0#(\w+)<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1\2\3in+KAP+\t+en\t', s) # Dränglerinnen as Drang+ler+in+en

  # N>N derivations "Brauch-tum", "Arbeiterschaft". There should be none with umlaut, and diminutives are dealt w/ sep.
  s = rr(u'<NN>:#0#(\w+)#0#:(\w+)<NN>:#0#<SUFF>:#0#').sub(r'\1+KAP+\t+\2\t', s) # Bauchtums... // Note: SMOR fails on "Brauchtümerpflege", "Arbeitschaftenvermittlung" etc.
  s = rr(u'[aeiouäöü]:([aeiouäöü])(\w*)<NN>:#0#(\w+)<NN>:#0#<SUFF>:#0#').sub(r'\1\2\3+KAP+\t', s) # Drängler as Drang+ler
  
  debug('06 E\t' + s)

  # Undo other suffix analyses.

  # Remove the stupid "Rinnen" analyses.
  s = rr(u'[aeiouäöü]:([aeiouäöü])(\w*)#0#:e<NN>:#0#R:rinne<\+NN>$').sub(r'\1\2erin+KAP+', s)
  s = rr(u'#0#:e<NN>:#0#R:rinne<\+NN>$').sub(r'erin+KAP+', s) # without umlaut, final

  s = rr(u'[aeiouäöü]:([aeiouäöü])(\w*)#0#:e<NN>:#0#R:rinne#0#:n<NN>:#0#').sub(r'\1\2erin+KAP+\t+en\t', s) # with umlaut, non-final
  s = rr(u'#0#:e<NN>:#0#R:rinne#0#:n<NN>:#0#').sub(r'erin+KAP+\t+en\t', s) # without umlaut, non-final

  s = rr(u'<NN>:#0#(?:<SUFF>:#0#|)in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'in+KAP+\t+en<NN>:#0#', s) # "Betreuerinnen"
 
  # SMOR and some weird stuff on "Berlinerin"
  s = s.replace(u'<NN>:#0#er<NN>:#0#<SUFF>:#0#in<SUFF>:#0##0#:n#0#:e#0#:n<+NN>', u'erin+KAP+')
 
  debug('06 F\t' + s)

  # Diminutives.
  s = rr(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#:#0#(lein|chen)<NN>:#0#<SUFF>:#0#').sub(r'\1\3\4\6+KAP+\t', s)
  s = rr(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#(lein|chen)<NN>:#0#<SUFF>:#0#').sub(r'\1\3\4\6+KAP+\t', s)

  # ... final.
  s = rr(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#:#0#(lein|chen)<SUFF>:#0#<\+NN>').sub(r'\1\3\4\6+KAP+\t', s)
  s = rr(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#(lein|chen)<SUFF>:#0#<\+NN>').sub(r'\1\3\4\6+KAP+\t', s)
  
  debug('06 G\t' + s)

  # Some NN suffixations.
  s = rr(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<SUFF>:#0#<\+NN>').sub(r'\1\2\3+KAP+', s) # "Ökologe" as triple! suffixation.
  s = rr(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<SUFF>:#0#<\+NN>').sub(r'\1\2+KAP+', s) # "Motoriker" as double suffixation.
  
  s = rr(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1\2+KAP+\t+en\t', s)# "Ökologen(verband)"

  s = s.replace(u'<NN>:#0#ist#0#:e#0#:n<NN>:#0#<SUFF>:#0#', u'ist+KAP+\t+en\t') # Faschisten- as "Fasch-ist+en" ???

  debug('07\t' + s)

  s = rr(u'(?:e:#0#|)([^aeiouäöü]|)n:#0#<V>:#0#(\w+)<F>:#0#<NN>:#0#<SUFF>:#0#').sub(r'\1\2+KAP+\t+0\t', s) # Versammlungverbot with missing LE.
  s = rr(u'<V>:#0#(\w+)#0#:(\w+)<NN>:#0#<SUFF>:#0#').sub(r'\1+KAP+\t+\2\t', s)# Versammlungsverbot with correct LE. V-stem internal replacements done already (above).

  debug('08\t' + s)

  # There might be more than 'erin'. But it breaks the V compound element detection when (\w+) is used instead of (erin).
  s = rr(u'(?:e:#0#|)n:#0#<V>:#0#(erin)').sub(r'\1', s) # Leftover: b:Betreue:#0#n:#0#<V>:#0#erin

  debug('09\t' + s)

  s = rr(u'(<ADJ>:#0#)(\w+)(#0#:\w+|)<NN>:#0#<SUFF>:#0#').sub(r'\2+KAP+\t+\3\t', s) # "Lieblichkeits" etc. LE gets moved PAST <NN>
  s = rr(u'<ADJ>:#0#([a-zäöüß]+)<SUFF>:#0#<\+NN>').sub(r'\1+KAP+', s) # For h/keit final.
  s = rr(u'(\w*)([aou]):([äöü])([\w#0:]*)<NN>:#0#(?:<SUFF>:#0#|)(\w+)<SUFF>:#0#').sub(r'\1\3\4\5<NN>:#0#', s) # rescue umlauting suffixes
  s = rr(u'<NN>:#0#(?:<SUFF>:#0#|)(\w+)<SUFF>:#0#').sub(r'\1<NN>:#0#', s) # same again w/o umlaut
  s = rr(u'<NN>:#0#(\w+)<SUFF>:#0#(<\+NN>|<NN>:#0#)').sub(r'\1\t', s)

  debug('10\t' + s)

  s = rr(u'(?:e:#0#|)n:#0#<V>:#0#<NN>:#0#<SUFF>:#0#').sub(r'+KAP+\t', s) # Satzbau-
  s = rr(u'(?:e:#0#|)n:#0#<V>:#0#<SUFF>:#0#<\+NN>').sub(r'+KAP+', s) # The same, final.

  debug('11\t' + s)

  # Fix TRUNC.
  s = rr(u'{:#0#([^}]+)}:#0#-<TRUNC>:#0#').sub(r'\1\t--\t', s)

  debug('13\t' + s)

  # Separate prefixes and ORD ("Dritt-mittel").
  s = rr(u'(\w):(\w)(\w*)(<ORD>|<PREF>):#0#').sub(r'\1\3~\t', s) # initial, make lower case
  s = rr(u'(?:<ORD>|<PREF>):#0#').sub(r'~\t', s)# not initial, just insert boundary

  debug('13 A\t' + s)

  # Some derivational affixes.
  s = rr(u'<NN>:#0#([a-zäöüß]+)<ADJ>:#0#<SUFF>:#0#([a-zäöüß]+)<SUFF>:#0#<\+NN>').sub(r'\1\2+KAP+\t', s) # NN-ADJ-NN: Gesetzmäßigkeit
  s = rr(u'<NN>:#0#([a-zäöüß]+)<ADJ>:#0#<SUFF>:#0#([a-zäöüß]+)#0#:([a-z]+)<NN>:#0#<SUFF>:#0#').sub(r'\1\2+KAP+\t+\3\t', s) # NN-ADJ-NN: Gesetzmäßigkeits-
  s = rr(u'<NN>:#0#([a-zäöüß]+)<ADJ>:#0#<SUFF>:#0#([a-zäöüß]+)<F>:#0#<NN>:#0#<SUFF>:#0#').sub(r'\1\2+KAP+\t+0\t', s) # NN-ADJ-NN:  Gesetzmäßigkeitversteck with +0
  debug('13 Aa\t' + s)

  # Qudruple suffixation as in "Professionalisierung" 
  s = rr(u'<[A-Z]+>:#0#([a-zäöüß]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß]+)<SUFF>:#0#<\+NN>').sub(r'\1\2\3\4+KAP+', s)
  s = rr(u'<[A-Z]+>:#0#([a-zäöüß]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß]+)#0#:([a-zäöüß]+)<NN>:#0#<SUFF>:#0#').sub(r'\1\2\3\4+KAP+\t+\5\t', s)
 
  s = rr(u'<NN>:#0#(\w+)<ADJ>:#0#<SUFF>:#0#').sub(r'\1-KAP-\t', s) # NN-ADJ
  debug('13 Ab\t' + s)

  s = rr(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<NN>:#0#<SUFF>:#0#').sub(r'\1\2\3+KAP+\t', s)
  s = rr(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<SUFF>:#0#<\+NN>').sub(r'\1\2\3+KAP+\t', s)
  s = rr(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<ADJ>:#0#<SUFF>:#0#').sub(r'\1\2\3-KAP-\t', s)
  s = rr(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<V>:#0#<SUFF>:#0#').sub(r'\1\2\3-KAP-\t', s)
  debug('13 Ac\t' + s)

  s = rr(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<NN>:#0#<SUFF>:#0#').sub(r'\1\2+KAP+\t', s)
  s = rr(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<SUFF>:#0#<\+NN>').sub(r'\1\2+KAP+', s)
  debug('13 Ac.1\t' + s)
  s = rr(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)([#0:a-zäöü]+)<NN>:#0#<SUFF>:#0#').sub(r'\1\2+KAP+\t\3\t', s)
  debug('13 Ac.2\t' + s)
  s = rr(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<ADJ>:#0#<SUFF>:#0#').sub(r'\1\2-KAP-\t', s)
  s = rr(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<V>:#0#<SUFF>:#0#').sub(r'\1\2-KAP-\t', s)
  debug('13 Ad\t' + s)

  # These mess up "Kraftwerksneubauten" and similar compounds. What were they good for originally?
  #s = rr(u'<[A-Z]+>:#0#(\w+)<NN>:#0#<SUFF>:#0#').sub(r'\1+KAP+\t', s)
  #s = rr(u'<[A-Z]+>:#0#(\w+)<ADJ>:#0#<SUFF>:#0#').sub(r'\1-KAP-\t', s)
  #s = rr(u'<[A-Z]+>:#0#(\w+)<V>:#0#<SUFF>:#0#').sub(r'\1-KAP-\t', s)
  
  s = rr(u'<V>:#0##0#:t<PPast>:#0#<[A-Z]+>:#0#<SUFF>:#0#(\w+)<SUFF>:#0#<\+NN>').sub(r't\1+KAP+', s)
  s = rr(u'<V>:#0##0#:t<PPast>:#0#<[A-Z]+>:#0#<SUFF>:#0#(\w+)([#0:a-z]+)<NN>:#0#<SUFF>:#0#').sub(r't\1+KAP+\t\2\t', s)

  debug('13 B\t' + s, 2)

  # Fix "in nen".
  s = rr(u'<NN>:#0##0#:n#0#:e#0#:n<\+NN>').sub(r'<+NN>', s)

  debug('13 Ba\t' + s, 2)

  # Comparatives and superlatives.

  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'\t\1\2\3er-KAP-', s) # Comp w/umlaut final.
  s = rr(u'<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'er-KAP-', s) # w/o umlaut final.
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\t\1\2\3er-KAP-\t+en\t', s) # w/umlaut final.
  s = rr(u'<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'er-KAP-\t+en\t', s)
   
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0#').sub(r'\t\1\2\3er-KAP-\t', s) # Comp in "Stärkerstellung".
  s = rr(u'<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0#').sub(r'er-KAP-\t', s) # w/o umlaut.
  
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'\t\1\2\3st-KAP-', s) # Lichtstärksten
  s = rr(u'<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'st-KAP-', s) 

  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#').sub(r'\t\1\2\3st-KAP-\t', s) # Stärkststellung.
  s = rr(u'<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#').sub(r'st-KAP-\t', s)
 
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\t\1\2\3st-KAP-\t+en\t', s) # Superl w/umlaut.
  s = rr(u'<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'st-KAP-\t+en\t', s) # Superl w/o umlaut.

  # still some superlatives left
  s = s.replace('<ADJ>:#0##0#:e#0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#', u'est')
  s = rr(u'[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'\1\2t-KAP-', s) # größter final
  s = rr(u'<ADJ>:#0##0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(u't-KAP-', s) # no uml
  s = rr(u'[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1\2t-KAP-\t+en\t', s) # größten-
  s = rr(u'<ADJ>:#0##0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(u't-KAP-\t+en\t', s) # no uml

  debug('13 C\t' + s, 2)

  s = rr(u'e:#0#n:#0#<V>:#0##0#:e#0#:n<SUFF>:#0#<\+NN>').sub(r'en-KAP-', s) # "gießen" in "Spritzgießen" as spritzen-en+en<SUFF>
  s = rr(u'n:#0#<V>:#0##0#:e#0#:n<SUFF>:#0#<\+NN>').sub(r'en-KAP-', s) # "gießen" in "Spritzgießen" as spritzen-en+en<SUFF>

  # rescue strange -ismus/en analyses.
  s = rr(u'<NN>:#0#([a-zäöüß:#0]+)<SUFF>:#0#').sub(r'\1', s)

  debug('14\t' + s, 2)

  # Try to rescue Ärztekammer (A:ä).
  s = rr(u'([AOU]):[äöü]([a-zäöüß]+)#0#:e<NN>:#0#').sub(r'\1\2\t+=e\t', s)

  # First split. We will join & split again later.
  nouns = re.split(r'<NN>:#0#|\t|<ADJ>:#0#', s)

  debug('15\t' + "\t".join(nouns))

  # Rescue "Bedürfnisse" (avoid +se linking element).
  nouns = [rr(u'nis#0#:s#0#:e$').sub(r'nis\t+e\t', x) for x in nouns]
  nouns = [rr(u'nis#0#:s<\+NN>').sub(r'nis', x) for x in nouns]

  # Separate and mark remaning FEs.
  nouns = [fix_fes(x) for x in nouns]

  debug('16\t' + "\t".join(nouns))

  # Clean elements containing suffixes.
  nouns = ['+KAP+' + rr(u'(?:<[^>]+>|\w):#0#').sub(r'', x) if '<SUFF>' in x else x for x in nouns]

  debug('17\t' + "\t".join(nouns))

  # Split ADJ and V compound elements.
  nouns = [rr(u'<ADJ>:#0#').sub(r'-KAP-\t', x) for x in nouns]
  nouns = [rr(u'e:#0#n:#0#<V>:#0#').sub(r'en-KAP-\t#en\t', x) for x in nouns]
  nouns = [rr(u'n:#0#<V>:#0#').sub(r'n-KAP-\t#n\t', x) for x in nouns]

  debug('18\t' + "\t".join(nouns))

  # Second split.
  nouns = '\t'.join(nouns).split('\t')

  debug('19\t' + "\t".join(nouns))

  # Some cleanups.
  nouns = [x.replace('<+NN>', '').strip() if not x == '+' else '' for x in nouns]
  nouns = [rr(u'^:#0#').sub(r'', n) for n in nouns]

  debug('20\t' + "\t".join(nouns))

  # Do NOT keep umlaut in head noun. Is plural!
  nouns = nouns[:-1] + [rr(u'([aou]):([äöü])').sub(r'\1', nouns[-1])]

  debug('21\t' + "\t".join(nouns))

  # Move +KAP+ to end.
  nouns = [rr(u'\+KAP\+').sub(r'', x) + '+KAP+' if '+KAP+' in x else x for x in nouns]
  nouns = [rr(u'-KAP-').sub(r'', x) + '-KAP-' if '-KAP-' in x else x for x in nouns]

  debug('22\t' + "\t".join(nouns))

  # Clean remaining to/from-NULL substitutions.
  nouns = [substitute_nulls(x) for x in nouns]

  debug('23\t' + "\t".join(nouns))

  # Try to catch remaining ablauts.
  nouns = [rr(u'[aeiouäöü]:([aeiouäöü])').sub(r'\1', x) for x in nouns]
  
  # Some uncaught umlauts, such as A:ärztin
  nouns = [rr(u'^[AOU]:([äöü])').sub(r'+KAP+\1', x) for x in nouns]

  # Make capitalization substitutions.
  nouns = [fix_cap(x) for x in nouns]

  debug('24\t' + "\t".join(nouns))

  # Compact.
  nouns = filter(None, nouns)

  debug('25\t' + "\t".join(nouns), 3)

  return [nouns] + check_lex(nouns)


# Checks whether analysis contains : # or <.
def is_trash(a):
  ana = '_'.join(a[0])
  if rr(u'[:#<>]').match(ana):
    debug(ana, 4)
    return False
  else:
    return True

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
  parser.add_argument("--nosanitycheck", action='store_true', help="disable check for lexical sanity")
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
    if rr(u'^> ').match(l) or l == '>' or not l:

      if len(c_analyses) > 0 and c_token:

          # Remove trailing inflection analysis and useless ORTH info.
          c_analyses = [rr(u'(<\+[^>]+>).*$').sub(r'\1', x).replace('<NEWORTH>','').replace('<OLDORTH>','') for x in c_analyses] 

          # Massive speedup: Remove identical analyses after inflection analyses have been stripped.
          c_analyses = list(set(c_analyses))

          # Only get analyses for this as noun.
          nounalyses = [nounalize(x) for x in c_analyses if '<+NN>' in x]
    
          # One lexical item means "not compound". Get rid.
          nounalyses = [e for e in nounalyses if e[2] > 1]

          # Eliminate analyses with : and # and <> in them and report them in debug mode.
          nounalyses = filter(is_trash, nounalyses)

          # Only use analyses with the best possible lexical score.
          # Also: Eliminate analyses below required lexical sanity level.
          if len(nounalyses) > 1:
            lex_max = max([a[1] for a in nounalyses])
            nounalyses = [e for e in nounalyses if len(e) > 0 and e[1] == lex_max and (args.nosanitycheck or is_lexically_sane(e))]

          # Remove "Rinnen" analyses for "movierte" nouns.
          if len(nounalyses) > 0 and rr(u'.+rinnen$').match(c_token):
            nounalyses = [e for e in nounalyses if len(e) > 0 and not e[0][-1] == 'Rinne' ]

          # Remove "Nachstel-Lungen" etc.
          if len(nounalyses) > 0 and rr(u'.+llungen$').match(c_token):
            nounalyses = [e for e in nounalyses if len(e) > 0 and not e[0][-1] == 'Lunge' ]

          # Fix "Kassa".
          if len(nounalyses) > 0 and rr(u'.*[Kk]assen.*').match(c_token):
            nounalyses = [[[f if not f == u'Kassa' else u'Kasse' for f in e[0]], e[1], e[2], e[3]] for e in nounalyses if len(e) > 0 ]

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
            lexies = [e for e in nounalyses[0][0] if rr(u'^[a-zA-ZäöüÄÖÜß]+$').match(e)]
            fugies = [e[1:] for e in nounalyses[0][0] if rr(u'^\+').match(e)]
            fugiestring = '|'+'|'.join(fugies)+'|' if len(fugies)>0 else '|'
            annotation = '\t'.join([c_token, '_'.join(nounalyses[0][0]), lexies[-1], '|'+'|'.join(lexies[:-1])+'|', fugiestring])
          elif not c_token == '>':
            annotation = '\t'.join([c_token] + NO_ANNO)
          else:
            annotation = ''

          ofh.write(annotation.encode('utf-8') + '\n')

      # Fresh start.
      c_analyses = list()
      c_token    = rr(u'^> ').sub(r'', l.strip())

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
