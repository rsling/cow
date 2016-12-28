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

  # Pure umlaut, "Mütter", Öfen.
  s = rr(u'([aou]):([äöü])([^#0:]*\w$)').sub(r'\1\3\t+=', s)
  s = rr(u'^([AOUaou]):([ÄÖÜäöü])([^#0:]*\w$)').sub(r'\1\3\t+=', s)

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
     

def loan_fix(s):
  if u'+FEFIX+' in s and rr(u'(?:[a-z]|#0#):[a-z]').search(s):
    s = rr(u'([a-z]):([a-z])([a-z]):([a-z])').sub(r'\1\3\t-\1\3\t+\2\4', s)
    s = rr(u'((?:#0#:[a-z])+)').sub(r'\t+\1', s)
    s = rr(u'((?:[a-z]:#0#)+)').sub(r'\1\t-\1', s)
    if '+KAP+' in s:
      s = '+KAP+' + s.replace(u'+KAP+', u'')
  elif u'+PLFIX+' in s:
    s = rr(u'([a-z]):(?:[a-z])([a-z]):(?:[a-z])').sub(r'\1\3', s)
    s = rr(u'(#0#:[a-z])+').sub(r'', s)
    s = rr(u'([a-z]):#0#').sub(r'\1', s)
    if '+KAP+' in s:
      s = '+KAP+' + s.replace(u'+KAP+', u'')

  s = s.replace(u'+PLFIX+', u'')
  s = s.replace(u'+FEFIX+', u'')
  return s


ERRS = [
         {'from' : [u'Blech','Dosis'], 'to' : ['Blech', 'Dose']}
         ,{'from' : [u'Einkommen', u'+s', u'teuerer', u'Klärung'], 'to' : [u'Einkommen', u'Steuer', u'Erklärung']}
         ,{'from' : [u'Fischer', u'Ei'], 'to' : [u'Fischerei']}
         ,{'from' : [u'Hang', u'+=e'], 'to' : [u'hängen', u'#en']}
         ,{'from' : [u'Pferd', u'+es', u'Port'], 'to' : [u'Pferd', u'+e', u'Sport']}
         ,{'from' : [u'rege', u'-e', u'Lunge'], 'to' : [u'Regelung']}
         ,{'from' : [u'rege', u'Lunge'], 'to' : [u'Regelung']}
         ,{'from' : [u'regen', u'#en', u'Lunge'], 'to' : [u'Regelung']}
         ,{'from' : [u'Wart', u'+e'], 'to' : [u'warten', u'#n']}
         ,{'from' : [u'List', '+en'], 'to' : [u'Liste', u'+n']}
         ,{'from' : [u'best', u'Ehe'], 'to' : [u'bestehen', u'#n']}
         ,{'from' : [u'best', u'Elle'], 'to' : [u'bestellen', u'#n']}
         ,{'from' : [u'eins', u'Ehe'], 'to' : [u'einsehen', u'#n']}
         ,{'from' : [u'früher', u'Kennung'], 'to' : [u'früh', u'Erkennung']}
         ,{'from' : [u'herb', 'Ei'], 'to' : [u'herbei']}
         ,{'from' : [u'kohlen', u'+s', u'Aura'], 'to' : [u'Kohle', '+n', u'sauer']}
         ,{'from' : [u'tastend', u'Ruck'], 'to' : [u'Taste', u'+n', u'Druck']}
         ,{'from' : [u'unterdrucken', u'#en'], 'to' : [u'unter', u'Druck']}
         ,{'from' : [u'unterputzen', u'#en'], 'to' : [u'unter', u'Putz']}
         ,{'from' : [u'untertonen', u'#en'], 'to' : [u'unter', u'Ton']}
         ,{'from' : [u'unterwassern', u'#n'], 'to' : [u'unter', u'Wasser']}
         ,{'from' : [u'unterst', u'Elle'], 'to' : [u'unterstellen', u'#n']}
         ,{'from' : [u'unterstufen'], 'to' : [u'unter', u'Stufe', u'+n']}
         ,{'from' : [u'verschleißt', u'Eile'], 'to' : [u'verchleißen', u'#en', u'Teile']}
         ,{'from' : [u'vorschulen', u'#en'], 'to' : [u'vor', u'Schule', u'-e']}
         ,{'from' : [u'weit', u'ergeben'], 'to' : [u'weitergeben']}
         ,{'from' : [u'zubetten', u'#en'], 'to' : [u'zu', u'Bett']}
         ,{'from' : [u'überlanden', '#en'], 'to' : [u'über', 'Land']}
         ,{'from' : [u'Konzept', u'Ionierung'], 'to' : [u'Konzeptionierung']}
         ,{'from' : [u'Vers', u'Ionierung'], 'to' : [u'Versionierung']}
         ,{'from' : [u'Unglück', u'Lich', u'er', u'Weise'], 'to' : [u'unglücklicherweise']}
         ,{'from' : [u'Gott', u'+s', u'Ei', u'Dank'], 'to' : [u'Gottseidank']}
         ,{'from' : [u'best', u'reiten', u'#en', u'Bar'], 'to' : [u'unbestreitbar']}
         ,{'from' : [u'ermögen', u'#en', u'Licht'], 'to' : [u'ermöglicht']}
         ,{'from' : [u'gefahren'], 'to' : [u'Gefahr', '+en']}
         ,{'from' : [u'gegenfahren', '#en'], 'to' : [u'gegen', u'fahren', u'#en']}
         ,{'from' : [u'irren', u'Haus'], 'to' : [u'irr', u'+en', u'Haus']}
         ,{'from' : [u'irre', u'-e', u'+en', u'Haus'], 'to' : [u'irr', u'+en', u'Haus']}
         ,{'from' : [u'sitzen', u'Bleibe'], 'to' : [u'sitzen', u'bleiben']}
         ,{'from' : [u'Skriptum'], 'to' : [u'Skript']}
         ,{'from' : [u'Kolleg'], 'to' : [u'Kollege']}
         ,{'from' : [u'nierder', u'landen'], 'to' : [u'Niederlande']}
         ,{'from' : [u'Schi', u'Essen'], 'to' : [u'schießen']}
         ,{'from' : [u'Gel', u'Ernte'], 'to' : [u'gelernt']}
         ,{'from' : [u'irre', u'-re', u'Real'], 'to' : [u'irreal']}
         ,{'from' : [u'Türe'], 'to' : [u'Tür']}
         ,{'from' : [u'+s', u'Trasse'], 'to' : [u'Straße']}
         ,{'from' : [u'zuwidern', u'#n'], 'to' : [u'zuwider']}
         #,{'from' : [], 'to' : []}
       ]


def sublist(sub_list,this_list):
    if sub_list[0] in this_list:
        for i,item in enumerate(sub_list[1:]):
            if item not in this_list[this_list.index(sub_list[i]):]:
                return False
        return(this_list.index(sub_list[0]),len(sub_list))


def err_check(ns):
  global ERRS
  for e in ERRS:
    if len(e['from']) <= len(ns):
      sl = sublist(e['from'], ns)
      if sl:
        ns = ns[0:sl[0]] + e['to'] + ns[sl[1]:]
  return ns

def nounalize(s):
  s = s.strip()

  debug('=========================================', 4)

  debug('00\t' + s, 2)

  # Make zero elements distinguishable from categories.
  s = s.replace(r'<>', r'#0#')

  debug('01\t' + s, 2)

  # Fix Aenderungs-, Oeffnungs-, Ueber- orthography
  s = s.replace(u'<ASCII>:#0#ä:A#0#:e', u'ä')
  s = s.replace(u'<ASCII>:#0#ö:O#0#:e', u'ö')
  s = s.replace(u'<ASCII>:#0#ü:U#0#:e', u'ü')

  s = s.replace(u'<ASCII>:#0#Ä:A#0#:e', u'Ä')
  s = s.replace(u'<ASCII>:#0#Ö:O#0#:e', u'Ö')
  s = s.replace(u'<ASCII>:#0#Ü:U#0#:e', u'Ü')

  s = s.replace(u'<ASCII>:#0#A#0#:e', u'Ä') # Öfen etc. Some 
  s = s.replace(u'<ASCII>:#0#O#0#:e', u'Ö')
  s = s.replace(u'<ASCII>:#0#U#0#:e', u'Ü')

  s = s.replace(u'ä:a#0#:e', u'ä')
  s = s.replace(u'ö:a#0#:e', u'ü')
  s = s.replace(u'u:a#0#:e', u'ö')

  # Binnen-I
  s = rr(u'<NN>:#0#<SUFF>:#0#In<SUFF>:#0#<\+NN>|<NN>:#0#<SUFF>:#0#In<SUFF>:#0##0#:n#0#:e#0#:n<\+NN>').sub(r'<NN>:#0#<SUFF>:#0#\t:In+KAP+', s) 
  s = rr(u'<NN>:#0#In<SUFF>:#0#<\+NN>|<NN>:#0#In<SUFF>:#0##0#:n#0#:e#0#:n<\+NN>').sub(r'<NN>:#0#\t:In+KAP+', s)
  s = rr(u'<NN>:#0#<SUFF>:#0#In#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'<NN>:#0#<SUFF>:#0#\t:In\t+en\t', s)
  s = rr(u'<NN>:#0#In#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'<NN>:#0#\t:In\t+en\t', s)

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

  # Pl of Index > Indices
  s = s.replace(u'e:ix:z#0#:e#0#:s', u'ex+KAP+')

  # Party plural.
  s = s.replace(u'y:i#0#:e#0#:s<+NN>', u'y<+NN>')

  # Akzeptabilität
  s = rr(u'e:il<ADJ>:#0#<SUFF>:#0#ität(!:<SUFF>:#0#|)').sub(u'ilität', s)

  debug('01 B\t' + s, 2)

  # Remove "Schreibweise" tags.
  s = rr(u'<Simp>:#0#|<UC>:#0#|<SS>:#0#').sub(r'', s)

  # Get rid of verb prefix information as early as possible
  s = rr(u'<(VPART|VPREF)>:#0##0#:g#0#:e').sub(r'ge', s)
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

  # "Somatisch" fail
  s = s.replace(u'S:soma<NN>:#0#T:tisch<+NN>', u'\tsomatisch-KAP-')

  # "Krise" fail
  s = rr('(K:krisi:#0#s:#0##0#:e#0#:n|K:kris)<\+NN>').sub(r'\tKrise', s)

  # New attempt at -ologie etc. loans (which are fully decomposed by SMOR)
  s = rr(u'<NN>:#0#o<NN>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß:#0]+)(?:<[A-Z]+>:#0#|)<SUFF>:#0#([a-z:#0]+|)<\+NN>').sub(r'o\1\2\3\4\5+PLFIX++KAP+', s)
  debug('01 Ca\t' + s, 2)
  s = rr(u'<NN>:#0#o<NN>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß:#0]+)(?:<[A-Z]+>:#0#|)<SUFF>:#0#([a-z:#0]+|)<\+NN>').sub(r'o\1\2\3\4+PLFIX++KAP+', s)
  debug('01 Cb\t' + s, 2)
  s = rr(u'<NN>:#0#o<NN>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß:#0]+)(?:<[A-Z]+>:#0#|)<SUFF>:#0#([a-z:#0]+|)<\+NN>').sub(r'o\1\2\3+PLFIX++KAP+', s)
  debug('01 Cc\t' + s, 2)
  s = rr(u'<NN>:#0#o<NN>:#0#<SUFF>:#0#([a-zäöüß:#0]+)(?:<[A-Z]+>:#0#|)<SUFF>:#0#([a-z:#0]+|)<\+NN>').sub(r'o\1\2+PLFIX++KAP+', s)
  debug('01 Cd\t' + s, 2)

  s = rr(u'<NN>:#0#o<NN>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<NN>:#0#<SUFF>:#0#').sub(r'o\1\2\3\4+FEFIX++KAP+\t', s)
  s = rr(u'<NN>:#0#o<NN>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<NN>:#0#<SUFF>:#0#').sub(r'o\1\2\3+FEFIX++KAP+\t', s)
  s = rr(u'<NN>:#0#o<NN>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<[A-Z]+>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<NN>:#0#<SUFF>:#0#').sub(r'o\1\2+FEFIX++KAP+\t', s)
  s = rr(u'<NN>:#0#o<NN>:#0#<SUFF>:#0#([a-zäöüß:#0]+)<NN>:#0#<SUFF>:#0#').sub(r'o\1+FEFIX++KAP+\t', s)

  # Anarchist etc.
  s = s.replace(u'<NN>:#0#ist<NN>:#0#<SUFF>:#0#', u'ist')

  debug('01 C\t' + s, 2)

  # gliedrig
  s = s.replace(u'#0#:r<NN>:#0#<SUFF>:#0#ig<ADJ>:#0#<SUFF>:#0#keit<SUFF>:#0#<+NN>', u'rigkeit+KAP+')
  s = s.replace(u'#0#:r<NN>:#0#<SUFF>:#0#ig<ADJ>:#0#<SUFF>:#0#keit#0#:s<NN>:#0#<SUFF>:#0#', u'rigkeit+KAP+\t+s\t')
  s = s.replace(u'#0#:r<NN>:#0#<SUFF>:#0#ig<ADJ>:#0#<SUFF>:#0#', u'rig-KAP-\t')

  # "Waller" as "Wall_-l_ler"
  s = s.replace(u'll:#0#<NN>:#0#:#0#ler<NN>:#0#<SUFF>:#0#', u'ller\t')
  s = rr(u'([^l])l<NN>:#0#ler<NN>:#0#<SUFF>:#0#').sub(r'\1ller\t', s)

  # Final "Betreuerin". Needs to be protected before other suffix rules apply.
  s = rr(u'[aeiouäöü]:([aeiouäöü])(\w*)(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>').sub(r'\1\2\3erin+KAP+<+NN>', s) # with umlaut
  s = rr(u'(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>').sub(r'\1erin+KAP+<+NN>', s) # w/o

  # Klässlerinnen, Klässlerin, Klässler (non-last)
  s = rr(u'[aou]:([äöü])([a-zäöüß:#0]+)<NN>:#0#([a-zäöüß]+)<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1\2\3in+KAP+\t(n)\t+en\t', s)
  s = rr(u'[aou]:([äöü])([a-zäöüß:#0]+)<NN>:#0#:#0#([a-zäöüß]+)<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>').sub(r'\1\2\3in+KAP+', s)
  s = rr(u'[aou]:([äöü])([a-zäöüß:#0]+)<NN>:#0#([a-zäöüß]+)<NN>:#0#<SUFF>:#0#').sub(r'\1\2\3+KAP+\t', s)

  # Grobmotorikerin (triple NN suffixation).
  s = rr(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>').sub(r'\1\2in+KAP+<+NN>', s)
  s = rr(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#in<SUFF>:#0##0#:n#0#:e#0#:n<\+NN>').sub(r'\1\2in+KAP+<+NN>', s)
  s = rr(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1\2in+KAP+\t(n)\t+en\t', s)

  # Journalistin, Frauenrechtlerin etc. (double NN suffixation)
  s = rr(u'<NN>:#0#([a-zäöü]+)<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>').sub(r'\1in+KAP+<+NN>', s)
  s = rr(u'<NN>:#0#([a-zäöü]+)<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1in+KAP+\t(n)\t+en\t', s)
 
  # For some reason, yet another analysis of the same thing.
  s = rr(u'[aeiouäöü]:([aeiouäöü])(\w*)(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1\2erin+KAP+\t(n)\t+en\t', s)
  s = rr(u'(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1erin+KAP+\t(n)\t+en\t', s)

  # "Bauten"
  s = s.replace('au#0#:ten<V>:#0#<SUFF>:#0#<+NN>', u'au+KAP+')
  s = s.replace('au#0#:ten<V>:#0#<NN>:#0#<SUFF>:#0#', u'au+KAP+\t(t)\t+en\t')
  
  # "ophilie" in "Bibliophilie"
  #s = s.replace(u'<NN>:#0#o<NN>:#0#<SUFF>:#0#phil<ADJ>:#0#<SUFF>:#0#ie<SUFF>:#0#<+NN>', u'ophilie+KAP+')
  #s = s.replace(u'<NN>:#0#o<NN>:#0#<SUFF>:#0#phil<ADJ>:#0#<SUFF>:#0#ie<NN>:#0#<SUFF>:#0#', u'ophilie+KAP+\t')
  #s = s.replace(u'<NN>:#0#o<NN>:#0#<SUFF>:#0#log<NN>:#0#<SUFF>:#0#ikum<SUFF>:#0#<+NN>', u'ologikum+KAP+')

  # Angio
  s = s.replace(u'<NN>:#0#o<NN>:#0#<SUFF>:#0#', u'o+KAP+\t')

  # Thermie
  s = s.replace(u'<NN>:#0#ie<NN>:#0#<SUFF>:#0#', u'ie+KAP+\t')

  # ... and for some reason, Touristinnen still fails.
  s = s.replace(u'<NN>:#0#ist<NN>:#0#<SUFF>:#0#in<SUFF>:#0##0#:n#0#:e#0#:n<+NN>', u'istin+KAP+')

  # Examina
  s = s.replace(u'e:in#0#:a<+NN>', u'en+KAP+')
  s = s.replace(u'e:in#0#:a<NN>:#0#', u'en+KAP+\t-en/in\t+a\t')

  # "Stoffwechsel" fail
  s = s.replace(u'S:stoff<NN>:#0#wechseln:#0#<V>:#0#', u'\tStoffwechsel+KAP+\t')
  s = s.replace(u'Stoff<NN>:#0#wechseln:#0#<V>:#0#', u'\tStoffwechsel+KAP+\t')

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

  # Complete "selber" fail
  s = s.replace(u'Selb<NN>:#0#er<NN>:#0#<SUFF>:#0#', u'selber-KAP-\t')
  s = s.replace(u'S:selb<NN>:#0#er<NN>:#0#<SUFF>:#0#', u'\tselber-KAP-\t')

  # Aue-e+er
  s = s.replace(u'e:#0#<NN>:#0#er<NN>:#0#', u'er+KAP+\t')

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

  # Begleiterinnen final
  s = s.replace(u'e:#0#n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in<SUFF>:#0##0#:n#0#:e#0#:n<+NN>', u'erin+KAP+')

  # Harfenist/en/in/innen
  s = s.replace(u'<NN>:#0#niste:#0#n:#0#<V>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', u'nist+KAP+\t(n)\t+en\t')
  s = s.replace(u'<NN>:#0#niste:#0#n:#0#<V>:#0##0#:e#0#:n<SUFF>:#0#<+NN>', u'nist+KAP+')
  s = s.replace(u'<NN>:#0#niste:#0#n:#0#<V>:#0#innen<ADJ>:#0#', u'nistin+KAP+\t(n)\t+en\t')

  # "Anfänger" (middle).
  s = rr(u'[aeiouäöü]:([aeiouäöü])(\w*)e:#0#(\w|)n:#0#<V>:#0#(\w+)<NN>:#0#<SUFF>:#0#').sub(r'\1\2\3\4+KAP+\t', s)
  s = rr(u'e:#0#(\w|)n:#0#<V>:#0#(\w+)<NN>:#0#<SUFF>:#0#').sub(r'\1\2+KAP+\t', s)

  # "Buss" ???
  s = s.replace(u'B:bus#0#:s<+NN>', u'Bus+KAP+')
  s = s.replace(u'B:bus#0#:s#0#:e<NN>:#0#', u'\tBus\t+e\t')

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

  # bezogen
  s = s.replace(u'zi:oe:gh:#0#', u'zog')

  # ausgewogen
  s = s.replace(u'i:oe:#0#', u'o')

  # verzerrt
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0#', u't-KAP-\t')

  # auszubildend
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:e#0#:n#0#:d<PPres>:#0#<zu>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', u'end\t+en\t')
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:e#0#:n#0#:d<PPres>:#0#<zu>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#', u'end')
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:e#0#:n#0#:d<PPres>:#0#<ADJ>:#0#<SUFF>:#0#', u'end-KAP-\t')

  # das Aufeinanderprallen(lassen)
  s = s.replace(u'e:#0#n:#0#<V>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', u'en-KAP-\t')

  debug('06\t' + s, 2)

  # Bewunderns(wert)
  s = s.replace(u'ern:#0#<V>:#0##0#:n#0#:s<NN>:#0#<SUFF>:#0#', u'ern-KAP-\t+s\t')

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

  # Zusammenschlüsse/schluss
  s = s.replace(u'schli:üe:#0#ß:se:#0#n:#0#<V>:#0#<SUFF>:#0##0#:s<+NN>', u'schluss+KAP+')
  s = s.replace(u'schli:ue:#0#ß:se:#0#n:#0#<V>:#0#<SUFF>:#0#:s<+NN>', u'schluss+KAP+')

  # Stieg
  s = s.replace(u'e:ii:e', u'ie')

  # Unterlegenheit
  s = s.replace(u'i:#0#e', u'e')

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

  # 0 derivations, final.
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

  s = rr(u'[aeiouäöü]:([aeiouäöü])(\w*)#0#:e<NN>:#0#R:rinne#0#:n<NN>:#0#').sub(r'\1\2erin+KAP+\t(n)\t+en\t', s) # with umlaut, non-final
  s = rr(u'#0#:e<NN>:#0#R:rinne#0#:n<NN>:#0#').sub(r'erin+KAP+\t(n)\t+en\t', s) # without umlaut, non-final

  s = rr(u'<NN>:#0#(?:<SUFF>:#0#|)in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'in+KAP+\t(n)\t+en<NN>:#0#', s) # "Betreuerinnen"
 
  # SMOR and some weird stuff on "Berlinerin"
  s = s.replace(u'<NN>:#0#er<NN>:#0#<SUFF>:#0#in<SUFF>:#0##0#:n#0#:e#0#:n<+NN>', u'erin+KAP+')
 
  debug('06 F\t' + s)

  # Diminutives.
  s = rr(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#:#0#(lein|chen)<NN>:#0#<SUFF>:#0#').sub(r'\1\3\4\6+KAP+\t', s)
  s = rr(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#(lein|chen)<NN>:#0#<SUFF>:#0#').sub(r'\1\3\4\6+KAP+\t', s)

  # ... final.
  s = rr(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#:#0#(lein|chen)<SUFF>:#0#<\+NN>').sub(r'\1\3\4\6+KAP+\t', s)
  s = rr(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#(lein|chen)<SUFF>:#0#<\+NN>').sub(r'\1\3\4\6+KAP+\t', s)

  # Äderchen, for some reason 
  s = s.replace(u'<NN>:#0#chen<NN>:#0#<SUFF>:#0#', u'chen+KAP+\t')
 
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
  s = rr(u'<ORD>:#0#el<SUFF>:#0#<\+NN>').sub(r'el+KAP+', s)
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

  s = rr(u'[gG]:[bB]u:et:s#0#:s<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0#').sub(r'besser', s)# besser

  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'\t\1\2\3er-KAP-', s) # Comp w/umlaut final.
  s = rr(u'<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'er-KAP-', s) # w/o umlaut final.
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\t\1\2\3er-KAP-\t+en\t', s) # w/umlaut final.
  s = rr(u'<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'er-KAP-\t+en\t', s)
  debug('13 Ba1\t' + s, 2)
   
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0#').sub(r'\t\1\2\3er-KAP-\t', s) # Comp in "Stärkerstellung".
  s = rr(u'<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0#').sub(r'er-KAP-\t', s) # w/o umlaut.
  debug('13 Ba2\t' + s, 2)
  
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'\t\1\2\3st-KAP-', s) # Lichtstärksten
  s = rr(u'<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'st-KAP-', s) 
  debug('13 Ba3\t' + s, 2)

  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#').sub(r'\t\1\2\3st-KAP-\t', s) # Stärkststellung.
  s = rr(u'<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#').sub(r'st-KAP-\t', s)
  debug('13 Ba4\t' + s, 2)
 
  s = rr(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\t\1\2\3st-KAP-\t+en\t', s) # Superl w/umlaut.
  s = rr(u'<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'st-KAP-\t+en\t', s) # Superl w/o umlaut.
  debug('13 Ba5\t' + s, 2)

  # still some superlatives left
  s = s.replace('<ADJ>:#0##0#:e#0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#', u'est')
  s = rr(u'[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(r'\1\2t-KAP-', s) # größter final
  s = rr(u'<ADJ>:#0##0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>').sub(u't-KAP-', s) # no uml
  s = rr(u'[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(r'\1\2t-KAP-\t+en\t', s) # größten-
  s = rr(u'<ADJ>:#0##0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#').sub(u't-KAP-\t+en\t', s) # no uml

  # Complete "Inner" desaster
  s = s.replace(u'Inn<NN>:#0#er<NN>:#0#<SUFF>:#0#', u'inner-KAP-\t')
  s = s.replace(u'I:inn<NN>:#0#er<NN>:#0#<SUFF>:#0#', u'\tinner-KAP-\t')

  debug('13 C\t' + s, 2)

  s = rr(u'e:#0#n:#0#<V>:#0##0#:e#0#:n<SUFF>:#0#<\+NN>').sub(r'en-KAP-', s) # "gießen" in "Spritzgießen" as spritzen-en+en<SUFF>
  s = rr(u'n:#0#<V>:#0##0#:e#0#:n<SUFF>:#0#<\+NN>').sub(r'en-KAP-', s) # "gießen" in "Spritzgießen" as spritzen-en+en<SUFF>

  # rescue strange -ismus/en analyses.
  s = rr(u'<NN>:#0#([a-zäöüß:#0]+)<SUFF>:#0#').sub(r'\1', s)

  # "Tourismus" fail
  s = s.replace(u'<NN>:#0#ismus<NN>:#0#<SUFF>:#0#', u'ismus+KAP+\t')

  # "Türe" analyses instead of "Tür"
  s = s.replace(u'T:türe:#0#<NN>:#0#', u'\tTür\t')
  s = s.replace(u'Türe:#0#<NN>:#0#', u'\tTür\t')
  s = s.replace(u'T:türe:#0#<+NN>', u'\tTür')

  debug('14\t' + s, 2)

  # Rescue Konto/Konten
  s = s.replace(u'o:e#0#:n<+NN>', u'o')

  # Try to rescue Ärztekammer (A:ä).
  s = rr(u'([AOU]):[äöü]([a-zäöüß]+)#0#:e<NN>:#0#').sub(r'\1\2\t+=e\t', s)

  # And final 'Ärzt'
  s = rr(u'([AOU]):[äöü]([a-zäöüß]+)<\+NN>').sub(r'\1\2', s)

  # Abschus-s
  s = s.replace(u's<V>:#0##0#:s', u'ss')

  # First split. We will join & split again later.
  nouns = re.split(r'<NN>:#0#|\t|<ADJ>:#0#', s)
  
  debug('15\t' + "\t".join(nouns))

  # Rescue "Bedürfnisse" (avoid +se linking element).
  nouns = [rr(u'nis#0#:s#0#:e$').sub(r'nis\t+e\t', x) for x in nouns]
  nouns = [rr(u'nis#0#:s<\+NN>').sub(r'nis', x) for x in nouns]

  debug('15 A\t' + "\t".join(nouns))

  # Separate and mark remaning FEs.
  if rr(u'^\s*<\+NN>\s*$').match(nouns[-1]):
    nouns = nouns[:-1]
  nouns = [fix_fes(x) for x in nouns[:-1]] + [nouns[-1]]

  debug('16\t' + "\t".join(nouns))

  # Clean elements containing suffixes.
  nouns = ['+KAP+' + rr(u'(?:<[^>]+>|\w):#0#').sub(r'', x) if '<SUFF>' in x else x for x in nouns]

  debug('17\t' + "\t".join(nouns))

  # Split ADJ and V compound elements.
  nouns = [rr(u'<ADJ>:#0#').sub(r'-KAP-\t', x) for x in nouns]
  nouns = [rr(u'e:#0#n:#0#<V>:#0#').sub(r'en-KAP-\t#en\t', x) for x in nouns]
  nouns = [rr(u'n:#0#<V>:#0#').sub(r'n-KAP-\t#n\t', x) for x in nouns]

  debug('18\t' + "\t".join(nouns))

  # Join before second split.
  nouns = '\t'.join(nouns)
  
  debug('18 a\t' + nouns)

  # Rescue remaining +nen cases.
  nouns = rr(u'\t\+nen').sub(r'\t(n)\t+en', nouns)
  nouns = rr(u'\t\+es').sub(r'\t(e)\t+s', nouns)
  nouns = rr(u'\t\+ien').sub(r'\t(i)\t+en', nouns)
  
  debug('18 b\t' + nouns)

  # Remove studieren-en+Ende
  nouns = rr(u'en\t#en\tEnde($|\t)').sub(r'end-KAP-\1', nouns)
  
  debug('18 c\t' + nouns)

  # Second split.
  nouns = nouns.split('\t')
  
  debug('18 d\t' + "\t".join(nouns))

  # Fix g:best
  nouns = [rr('^[Gg]:[Bb]').sub(r'b', n) for n in nouns]
  
  debug('18 A\t' + "\t".join(nouns))

  # Resolve +FEFIX+ and +PLFIX+
  nouns = [loan_fix(x) for x in nouns]
  
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
  nouns = [x.replace(u're:üch', u'ruch') for x in nouns] # Bre:üch
  nouns = [rr(u'[aeiouäöü]:([aeiouäöü])').sub(r'\1', x) for x in nouns]
  
  # Some uncaught umlauts, such as A:ärztin
  nouns = [rr(u'^[AOU]:([äöü])').sub(r'+KAP+\1', x) for x in nouns]

  # Make capitalization substitutions.
  nouns = [fix_cap(x) for x in nouns]

  debug('24\t' + "\t".join(nouns))

  # Compact.
  nouns = filter(None, nouns)

  # Specifir error check.
  nouns = err_check(nouns)

  debug('25\t' + "\t".join(nouns), 3)

  return [nouns] + check_lex(nouns)


# Checks whether analysis contains : # or <.
def is_trash(a):
  ana = '_'.join(a[0])
  if rr(u'[<>]|[^_]:[^I]|[^_]#').search(ana):
    debug(ana, 5)
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
  parser.add_argument("--debug", default=3, type=int, help="set debuglevel (default = 4 = debug messages off)")
  args = parser.parse_args()

  global DEBUG
  DEBUG = args.debug

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

          # Eliminate analyses with : and # and <> in them and report them in debug mode.
          nounalyses = filter(is_trash, nounalyses)

          debug("S01\t" + "|".join(["_".join(na[0]) for na in nounalyses]), 3)

          # Remove "Rinnen" analyses for "movierte" nouns.
          if len(nounalyses) > 0 and rr(u'.+rinnen$').match(c_token):
            nounalyses = [e for e in nounalyses if len(e) > 0 and not e[0][-1] == 'Rinne' ]

          debug("S03\t" + "|".join(["_".join(na[0]) for na in nounalyses]), 3)

          # Remove "Nachstel-Lungen" etc.
          if len(nounalyses) > 0 and rr(u'.+llungen$').match(c_token):
            nounalyses = [e for e in nounalyses if len(e) > 0 and not e[0][-1] == 'Lunge' ]

          debug("S04\t" + "|".join(["_".join(na[0]) for na in nounalyses]), 3)

          # Prefer ...reise oder ...reis. Clumsy.
          if set([u'Halle', u'Album', u'Reise']) & set([e[0][-1] for e in nounalyses]):
            nounalyses = [e for e in nounalyses if not e[0][-1] in set([u'Hall', u'Alb', u'Reis'])]

          debug("S05\t" + "|".join(["_".join(na[0]) for na in nounalyses]), 3)
          
          # Remove diverse misanalyses recognizable from last element.
          if len(nounalyses) > 0:
            nounalyses = [e for e in nounalyses if not e[0][-1] in [u'bar', u'Linger', u'Elen', u'El']]

          debug("S06\t" + "|".join(["_".join(na[0]) for na in nounalyses]), 3)

          # Remove misana recognizable from any element.
          if len(nounalyses) > 0:
            nounalyses = [e for e in nounalyses if not set(e[0]) & set([u'Lich', u'Medik:zis'])]

          debug("S07\t" + "|".join(["_".join(na[0]) for na in nounalyses]), 3)

          # Fix "Kassa".
          if len(nounalyses) > 0 and rr(u'.*[Kk]assen.*').match(c_token):
            nounalyses = [[[f if not f == u'Kassa' else u'Kasse' for f in e[0]], e[1], e[2], e[3]] for e in nounalyses if len(e) > 0 ]

          debug("S08\t" + "|".join(["_".join(na[0]) for na in nounalyses]), 3)

          # Prefern non-"Ende" analyses ("Studierende" as "Studier Ende")
          if len(nounalyses) > 1 and ( set([e[0][-1] for e in nounalyses]) - set(u'Ende') ):
            nounalyses = [e for e in nounalyses if not e[0][-1] == u'Ende' ]

          debug("S09\t" + "|".join(["_".join(na[0]) for na in nounalyses]), 3)
    
          # One lexical item means "not compound". Get rid.
          if len(nounalyses) > 0:
            nounalyses = [e for e in nounalyses if e[2] > 1]

          debug("S10\t" + "|".join(["_".join(na[0]) for na in nounalyses]), 3)

          # Only use analyses with the best possible lexical score.
          # Also: Eliminate analyses below required lexical sanity level.
          if len(nounalyses) > 1:
            lex_max = max([a[1] for a in nounalyses])
            nounalyses = [e for e in nounalyses if len(e) > 0 and e[1] == lex_max and (args.nosanitycheck or is_lexically_sane(e))]

          debug("S11\t" + "|".join(["_".join(na[0]) for na in nounalyses]), 3)

          # If there are still multiple analyses left, use the ones with the least no. of lexical items. 
          if len(nounalyses) > 1:
            lex_item_min = min([a[2] for a in nounalyses])
            nounalyses = [e for e in nounalyses if e[2] <= lex_item_min]

          debug("S12\t" + "|".join(["_".join(na[0]) for na in nounalyses]), 3)

          # If there are still multiple analyses left, use the ones with the least no. of items. 
          if len(nounalyses) > 1:
            lex_item_min = min([a[3] for a in nounalyses])
            nounalyses = [e for e in nounalyses if e[3] <= lex_item_min]

          debug("S13\t" + "|".join(["_".join(na[0]) for na in nounalyses]), 3)

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
