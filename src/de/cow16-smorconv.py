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

rex_000 = re.compile(u'(?:[a-zäöüßA-ZÄÖÜ]|<[^>]+>):#0#', re.UNICODE)
rex_001 = re.compile(u'#0#:([a-zäöüßA-ZÄÖÜ])', re.UNICODE)
rex_002 = re.compile(u'([a-z]):([a-z])#0#:([a-z])', re.UNICODE)
rex_003 = re.compile(u'([aou]):([äöü])([^#0:]*\w$)', re.UNICODE)
rex_004 = re.compile(u'([aou]):([äöü])(.*)#0#:([a-z])#0#:([a-z])#0#:([a-z])$', re.UNICODE)
rex_005 = re.compile(u'([aou]):([äöü])(.*)#0#:([a-z])#0#:([a-z])$', re.UNICODE)
rex_006 = re.compile(u'([aou]):([äöü])(.*)#0#:([a-z])$', re.UNICODE)
rex_007 = re.compile(u'#0#:([a-z])#0#:([a-z])#0#:([a-z])$', re.UNICODE)
rex_008 = re.compile(u'#0#:([a-z])#0#:([a-z])$', re.UNICODE)
rex_009 = re.compile(u'#0#:([a-z])$', re.UNICODE)
rex_010 = re.compile(u'(\w):(\w)$', re.UNICODE)
rex_011 = re.compile(u'([a-zäöü]):#0#([a-zäöü]):#0#([a-zäöü]):#0#(\t|$)', re.UNICODE)
rex_012 = re.compile(u'([a-zäöü]):#0#([a-zäöü]):#0#(\t|$)', re.UNICODE)
rex_013 = re.compile(u'([a-zäöü]):#0#(\t|$)', re.UNICODE)
rex_020 = re.compile(u'([a-z]):([A-Z])([a-zäöüß]+)(?:<VPART>|<VPREF>):#0#', re.UNICODE)
rex_021 = re.compile(u'(?:<VPART>|<VPREF>):#0#', re.UNICODE)
rex_022 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+)<CARD>:#0#([a-zäöüß]+)<ADJ>:#0#<SUFF>:#0#', re.UNICODE) # "dreifach" and similar derivations
rex_023 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+)<CARD>:#0#', re.UNICODE)
rex_024 = re.compile(u'[aeiouäöü]:([aeiouäöü])(\w*)(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>', re.UNICODE)  # with umlaut
rex_025 = re.compile(u'(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>', re.UNICODE)  # w/o
rex_026 = re.compile(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>', re.UNICODE)
rex_027 = re.compile(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#in<SUFF>:#0##0#:n#0#:e#0#:n<\+NN>', re.UNICODE)
rex_028 = re.compile(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_029 = re.compile(u'<NN>:#0#([a-zäöü]+)<NN>:#0#<SUFF>:#0#in<SUFF>:#0#<\+NN>', re.UNICODE)  # w/o
rex_030 = re.compile(u'<NN>:#0#([a-zäöü]+)<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE)  # w/o
rex_031 = re.compile(u'[aeiouäöü]:([aeiouäöü])(\w*)(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE)  # w/o
rex_032 = re.compile(u'(?:e:#0#|)(\w|)n:#0#<V>:#0#er<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE)  # w/o
rex_033 = re.compile(u'#0#:sß:s', re.UNICODE)
rex_034 = re.compile(u's:#0#s:s', re.UNICODE)
rex_035 = re.compile(u's:#0#s:ß:#0#', re.UNICODE)
rex_036 = re.compile(u's:#0#s#0#:s', re.UNICODE)
rex_037 = re.compile(u's:#0#s:ß', re.UNICODE)
rex_038 = re.compile(u's:ßs:#0#', re.UNICODE)
rex_039 = re.compile(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w+)(e:#0#|)n:#0#<V>:#0##0#:n(<\+NN>|<NN>:#0#)<SUFF>:#0#', re.UNICODE) # With LE -n.
rex_040 = re.compile(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w+)(e:#0#|)n:#0#<V>:#0#(<\+NN>|<NN>:#0#)<SUFF>:#0#', re.UNICODE) # Without LE -n.
rex_041 = re.compile(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w+)(e:#0#|)n:#0#<V>:#0#(\w+)<SUFF>:#0#<\+NN>', re.UNICODE) # Word-final V>N derivations with umlaut
rex_042 = re.compile(u'([aeiouäöü]):([aeiouäöü])(\w+)n:#0#<V>:#0#<SUFF>:#0#<\+NN>', re.UNICODE)
rex_043 = re.compile(u'[aeiouäöü]:([aeiouäöü])(\w*)e:#0#(\w|)n:#0#<V>:#0#(\w+)<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_044 = re.compile(u'e:#0#(\w|)n:#0#<V>:#0#(\w+)<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_045 = re.compile(u'<ADJ>:#0#(\w+)<F>:#0#<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_046 = re.compile(u'([a-zäöüA-ZÄÖÜß:]+)<KSF>:#0#', re.UNICODE)
rex_047 = re.compile(u'#0#:g#0#:e([a-zäöü]+)#0#:iei:#0#([a-zäöü]+)e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>', re.UNICODE)
rex_048 = re.compile(u'#0#:g#0#:e([a-zäöü]+)#0#:iei:#0#([a-zäöü]+)e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_049 = re.compile(u'\w:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', re.UNICODE) 
rex_050 = re.compile(u'\w:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', re.UNICODE) 
rex_051 = re.compile(u'\w:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', re.UNICODE) 
rex_052 = re.compile(u'\w:#0#([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', re.UNICODE) 
rex_053 = re.compile(u'\w:#0#([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', re.UNICODE) 
rex_054 = re.compile(u'\w:#0#([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', re.UNICODE) 
rex_055 = re.compile(u'#0#:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', re.UNICODE) 
rex_056 = re.compile(u'#0#:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', re.UNICODE) 
rex_057 = re.compile(u'#0#:(\w)([^<>]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', re.UNICODE) 
rex_058 = re.compile(u'([^<>#]*<V>:#0#[^<>]*<NN>:#0#<SUFF>:#0#)', re.UNICODE) 

rex_059 = re.compile(u'\w:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', re.UNICODE) 
rex_060 = re.compile(u'\w:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', re.UNICODE) 
rex_061 = re.compile(u'\w:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', re.UNICODE) 
rex_062 = re.compile(u'\w:#0#([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', re.UNICODE) 
rex_063 = re.compile(u'\w:#0#([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', re.UNICODE) 
rex_064 = re.compile(u'\w:#0#([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', re.UNICODE) 
rex_065 = re.compile(u'#0#:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', re.UNICODE) 
rex_066 = re.compile(u'#0#:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', re.UNICODE) 
rex_067 = re.compile(u'#0#:(\w)([^<>]*<V>:#0#<SUFF>:#0#<\+NN>)', re.UNICODE) 

rex_068 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>', re.UNICODE)
rex_069 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)e:#0#n:#0#<V>:#0##0#:e#0#:n<PPast>:#0#<ADJ>:#0#<SUFF>:#0#', re.UNICODE)
rex_070 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)e:#0#n:#0#<V>:#0##0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_071 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)e:#0#n:#0#<V>:#0##0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>', re.UNICODE)
rex_072 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)n:#0#<V>:#0##0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>', re.UNICODE)
rex_073 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)n:#0#<V>:#0##0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_074 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)e:#0#n:#0#<V>:#0##0#:e#0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>', re.UNICODE)
rex_075 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+|)(#0#:[Gg]#0#:e|)([a-zäöüßA-ZÄÖÜ:]+)e:#0#n:#0#<V>:#0##0#:e#0#:t<PPast>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_076 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+)<ADJ>:#0#<SUFF>:#0#<\+NN>', re.UNICODE)

rex_077 = re.compile(u'e:#0#n:#0#<V>:#0##0#:e#0#:n#0#:d<PPres>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>', re.UNICODE) 
rex_078 = re.compile(u'n:#0#<V>:#0##0#:n#0#:d<PPres>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>', re.UNICODE) 
rex_079 = re.compile(u'([a-zäöüA-ZÄÖÜß:]+)e:#0#n:#0#<V>:#0##0#:e#0#:n#0#:d<PPres>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_080 = re.compile(u'([a-zäöüA-ZÄÖÜß:]+)n:#0#<V>:#0##0#:n#0#:d<PPres>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_081 = re.compile(u'[aeiouäöü]:([aeiouäöü])(\w*)<NN>:#0#(\w+)<NN>:#0#<SUFF>:#0#in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE) # Dränglerinnen as Drang+ler+in+nen
rex_082 = re.compile(u'<NN>:#0#(\w+)#0#:(\w+)<NN>:#0#<SUFF>:#0#', re.UNICODE) # Bauchtums... // Note: SMOR fails on "Brauchtümerpflege", "Arbeitschaftenvermittlung" etc.
rex_083 = re.compile(u'[aeiouäöü]:([aeiouäöü])(\w*)<NN>:#0#(\w+)<NN>:#0#<SUFF>:#0#', re.UNICODE) # Drängler as Drang+ler
rex_084 = re.compile(u'[aeiouäöü]:([aeiouäöü])(\w*)#0#:e<NN>:#0#R:rinne<\+NN>$', re.UNICODE) # with umlaut, final
rex_085 = re.compile(u'#0#:e<NN>:#0#R:rinne<\+NN>$', re.UNICODE) # without umlaut, final
rex_086 = re.compile(u'[aeiouäöü]:([aeiouäöü])(\w*)#0#:e<NN>:#0#R:rinne#0#:n<NN>:#0#', re.UNICODE) # with umlaut, non-final
rex_087 = re.compile(u'#0#:e<NN>:#0#R:rinne#0#:n<NN>:#0#', re.UNICODE) # without umlaut, non-final
rex_088 = re.compile(u'<NN>:#0#(?:<SUFF>:#0#|)in#0#:n#0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE) # "Betreuerinnen"
rex_089 = re.compile(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#:#0#(lein|chen)<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_090 = re.compile(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#(lein|chen)<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_091 = re.compile(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#:#0#(lein|chen)<SUFF>:#0#<\+NN>', re.UNICODE)
rex_093 = re.compile(u'(\w*)([aeiouäöü]):([aeiouäöü])(\w*)(\w:#0#|)<NN>:#0#(lein|chen)<SUFF>:#0#<\+NN>', re.UNICODE)
rex_094 = re.compile(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<SUFF>:#0#<\+NN>', re.UNICODE) # "Ökologe" as triple! suffixation.
rex_095 = re.compile(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<SUFF>:#0#<\+NN>', re.UNICODE) # "Motoriker" as double suffixation.
rex_096 = re.compile(u'<NN>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#([a-z]+)<NN>:#0#<SUFF>:#0#e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE) # "Ökologen(verband)"
rex_097 = re.compile(u'(?:e:#0#|)([^aeiouäöü]|)n:#0#<V>:#0#(\w+)<F>:#0#<NN>:#0#<SUFF>:#0#', re.UNICODE) # Versammlungverbot with missing LE.
rex_098 = re.compile(u'<V>:#0#(\w+)#0#:(\w+)<NN>:#0#<SUFF>:#0#', re.UNICODE) # Versammlungsverbot with correct LE. V-stem internal replacements done already (above).
rex_099 = re.compile(u'(?:e:#0#|)n:#0#<V>:#0#(erin)', re.UNICODE) # Leftover: b:Betreue:#0#n:#0#<V>:#0#erin

rex_100 = re.compile(u'(<ADJ>:#0#)(\w+)(#0#:\w+|)<NN>:#0#<SUFF>:#0#', re.UNICODE)  # "Lieblichkeits" etc. LE gets moved PAST <NN>
rex_100a =re.compile(u'<ADJ>:#0#([a-zäöüß]+)<SUFF>:#0#<\+NN>', re.UNICODE) # For h/keit final.

rex_101 = re.compile(u'(\w*)([aou]):([äöü])([\w#0:]*)<NN>:#0#(?:<SUFF>:#0#|)(\w+)<SUFF>:#0#', re.UNICODE)      # rescue umlauting suffixes
rex_102 = re.compile(u'<NN>:#0#(?:<SUFF>:#0#|)(\w+)<SUFF>:#0#', re.UNICODE)     # same again w/o umlaut
rex_103 = re.compile(u'<NN>:#0#(\w+)<SUFF>:#0#(<\+NN>|<NN>:#0#)', re.UNICODE)

rex_104 = re.compile(u'(?:e:#0#|)n:#0#<V>:#0#<NN>:#0#<SUFF>:#0#', re.UNICODE) # Satzbau-
rex_105 = re.compile(u'(?:e:#0#|)n:#0#<V>:#0#<SUFF>:#0#<\+NN>', re.UNICODE)  # The same, final.
rex_106 = re.compile(r'{:#0#([^}]+)}:#0#-<TRUNC>:#0#')
rex_107 = re.compile(u'(\w):(\w)(\w*)(<ORD>|<PREF>):#0#', re.UNICODE)  # initial, make lower case
rex_108 = re.compile(u'(?:<ORD>|<PREF>):#0#', re.UNICODE)  # not initial, just insert boundary
rex_109 = re.compile(u'<NN>:#0#(\w+)<ADJ>:#0#<SUFF>:#0#', re.UNICODE)
rex_110 = re.compile(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_111 = re.compile(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<ADJ>:#0#<SUFF>:#0#', re.UNICODE)
rex_112 = re.compile(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<V>:#0#<SUFF>:#0#', re.UNICODE)
rex_113 = re.compile(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_114 = re.compile(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<ADJ>:#0#<SUFF>:#0#', re.UNICODE)
rex_115 = re.compile(u'<[A-Z]+>:#0#(\w+)<[A-Z]+>:#0#<SUFF>:#0#(\w+)<V>:#0#<SUFF>:#0#', re.UNICODE)
rex_116 = re.compile(u'<[A-Z]+>:#0#(\w+)<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_117 = re.compile(u'<[A-Z]+>:#0#(\w+)<ADJ>:#0#<SUFF>:#0#', re.UNICODE)
rex_118 = re.compile(u'<[A-Z]+>:#0#(\w+)<V>:#0#<SUFF>:#0#', re.UNICODE)
rex_119 = re.compile(u'<NN>:#0##0#:n#0#:e#0#:n<\+NN>', re.UNICODE) 
rex_120 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>', re.UNICODE) # Comp w/umlaut final. 
rex_121 = re.compile(u'<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>', re.UNICODE) # w/o umlaut final. 
rex_122 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE) # w/umlaut final.
rex_123 = re.compile(u'<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE)
rex_124 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0#', re.UNICODE) # Comp in "Stärkerstellung".
rex_125 = re.compile(u'<ADJ>:#0##0#:e#0#:r<Comp>:#0#<ADJ>:#0#<SUFF>:#0#', re.UNICODE) # w/o umlaut.
rex_126 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>', re.UNICODE) # Lichtstärksten
rex_127 = re.compile(u'<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#<SUFF>:#0#<\+NN>', re.UNICODE)
rex_128 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#', re.UNICODE) # Stärkststellung.
rex_129 = re.compile(u'<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0#', re.UNICODE) # w/o umlaut
rex_130 = re.compile(u'([A-ZÄÖÜa-zäöüß:]+)[aou]:([äöü])([a-zäöüß]+)<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE) # Superl w/umlaut.
rex_131 = re.compile(u'<ADJ>:#0##0#:s#0#:t<Sup>:#0#<ADJ>:#0#<SUFF>:#0##0#:e#0#:n<NN>:#0#<SUFF>:#0#', re.UNICODE) # Superl w/o umlaut.

rex_200 = re.compile(u'e:#0#n:#0#<V>:#0##0#:e#0#:n<SUFF>:#0#<\+NN>', re.UNICODE) # "gießen" in "Spritzgießen" as spritzen-en+en<SUFF>
rex_201 = re.compile(u'n:#0#<V>:#0##0#:e#0#:n<SUFF>:#0#<\+NN>', re.UNICODE) # "gießen" in "Spritzgießen" as spritzen-en+en<SUFF>

rex_220 = re.compile(u'<CARD>:#0#er<SUFF>:#0#<\+NN>', re.UNICODE)
rex_221 = re.compile(u'<CARD>:#0#er<NN>:#0#<SUFF>:#0#', re.UNICODE)

rex_230 = re.compile(u'<NN>:#0#([a-zäöüß]+)<ADJ>:#0#<SUFF>:#0#([a-zäöüß]+)<SUFF>:#0#<\+NN>', re.UNICODE) # Gesetzmäßigkeit
rex_231 = re.compile(u'<NN>:#0#([a-zäöüß]+)<ADJ>:#0#<SUFF>:#0#([a-zäöüß]+)#0#:([a-z]+)<NN>:#0#<SUFF>:#0#', re.UNICODE) # Gesetzmäßigkeits-
rex_232 = re.compile(u'<NN>:#0#([a-zäöüß]+)<ADJ>:#0#<SUFF>:#0#([a-zäöüß]+)<F>:#0#<NN>:#0#<SUFF>:#0#', re.UNICODE) # Gesetzmäßigkeitversteck with +0

rex_250 = re.compile(u'([a-zäöüß]):([a-zäöüß])([a-zäöüß]):([a-zäöüß])$', re.UNICODE) # Mechanismus/en in fix_fes()

rex_260 = re.compile(u'([a-zäöüß]):#0##0#:e#0#:n<\+NN>', re.UNICODE)
rex_261 = re.compile(u'([a-zäöüß]):e([a-zäöüß]):n<\+NN>', re.UNICODE)

rex_270 = re.compile(u'e:#0#n:#0#<V>:#0#<SUFF>:#0#<\+NN>', re.UNICODE)
rex_271 = re.compile(u'n:#0#<V>:#0#<SUFF>:#0#<\+NN>', re.UNICODE)

rex_290 = re.compile(u'[aeiouäöü]:', re.UNICODE)

rex_300 = re.compile(u'([a-zäöüß]):#0#([a-zäöüß]):#0##0#:([a-zäöüß])#0#:([a-zäöüß])', re.UNICODE)
rex_301 = re.compile(u'<NN>:#0#([a-zäöüß:#0]+)<SUFF>:#0#', re.UNICODE)

rex_900 = re.compile(u'^:#0#', re.UNICODE)

rex_1001 = re.compile(u'(?:<[^>]+>|\w):#0#', re.UNICODE) 

rex_1002 = re.compile(r'\+KAP\+|-KAP-', re.UNICODE)
rex_1003 = re.compile(r'\+KAP\+', re.UNICODE)
rex_1004 = re.compile(r'-KAP-', re.UNICODE)

rex_1010 = re.compile(u'<Simp>:#0#|<UC>:#0#|<SS>:#0#', re.UNICODE)

rex_1020 = re.compile(u'<ADJ>:#0#', re.UNICODE)
rex_1021 = re.compile(u'e:#0#n:#0#<V>:#0#', re.UNICODE)
rex_1022 = re.compile(u'n:#0#<V>:#0#', re.UNICODE)

rex_1040 = re.compile(r'^:#0#', re.UNICODE)
rex_1041 = re.compile(u'([aou]):([äöü])', re.UNICODE)
rex_1042 = re.compile(r'\+KAP\+', re.UNICODE)
rex_1043 = re.compile(r'-KAP-', re.UNICODE)
rex_1044 = re.compile(u'^([a-zäöüA-ZÄÖÜß]):[a-zäöüA-ZÄÖÜß]',re.UNICODE)

rex_1060 = re.compile(r'(<\+[^>]+>).*$', re.UNICODE)
rex_1061 = re.compile(r'^> ', re.UNICODE)

rex_2000 = re.compile(u'^[A-ZÄÖÜ][a-zäöüß]+$', re.UNICODE)
rex_2001 = re.compile(u'^[a-zäöüß]+$', re.UNICODE)
rex_2002 = re.compile(u'^[A-ZÄÖÜ][a-zäöüß]+$|^[a-zäöüß]+$', re.UNICODE)
rex_2003 = re.compile(u'[:#<>]', re.UNICODE)
rex_2004 = re.compile(r'^> ', re.UNICODE)
rex_2005 = re.compile(u'.+rinnen$', re.UNICODE)
rex_2006 = re.compile(u'^[a-zA-ZäöüÄÖÜß]+$', re.UNICODE)
rex_2007 = re.compile(u'^\+', re.UNICODE)

NO_ANNO=['_', '_', '|', '|']

DEBUG = 5

def debug(s, l = 1):
  if l >= DEBUG:
    print s.encode('utf-8')

def substitute_nulls(s):
  s = rex_000.sub(r'', s)
  s = rex_001.sub(r'\1', s)

  # Some initial :#0# garbage.
  s = rex_900.sub(r'', s)
  return s


def fix_fes(s):
  # ...ismen as letters to 0 and 0 to letters in blocks.
  s = rex_300.sub(r'\1\2\t-\1\2\t+\3\4\t', s)

  # Mechanismus > en etc. as letter against letter replacement.
  s = rex_250.sub(r'\1\3\t-\1\3\t+\2\4\t', s)

  # Unfortunately represented in more complex way (vowel substitution + suffix): Marienbild.
  s = rex_002.sub(r'\1\t-\1\t+\2\3', s)

  # Pure umlaut, "Mütter".
  s = rex_003.sub(r'\1\3\t+=', s)

  # Suffixation with umlaut.
  s = rex_004.sub(r'\1\3\t+=\4\5\6', s)
  s = rex_005.sub(r'\1\3\t+=\4\5', s)
  s = rex_006.sub(r'\1\3\t+=\4', s)

  # Suffixation without umlaut.
  s = rex_007.sub(r'\t+\1\2\3', s)
  s = rex_008.sub(r'\t+\1\2', s)
  s = rex_009.sub(r'\t+\1', s)

  # "Suppletions".
  s = rex_010.sub(r'\1\t-\1\t+\2', s)

  # Deletions.
  s = rex_011.sub(r'\1\2\3\t-\1\2\3\4', s)
  s = rex_012.sub(r'\1\2\t-\1\2\3', s)
  s = rex_013.sub(r'\1\t-\1\2', s)
  return s


def fix_cap(s):

  # Fix the ablaut in strong verbs fixed by last rule (rex_068, rex_069).
  if '+ABL+' in s:
    s = rex_290.sub(r'', s)
    s = s.replace('+ABL+', '')

  # Now the KAP stuff.
  if '+KAP+' in s and '-KAP-' in s:
    s = rex_1002.sub(r'', s).lower()
  elif '+KAP+' in s:
    s = rex_1003.sub(r'', s).title()
  elif '-KAP-' in s:
    s = rex_1004.sub(r'', s).lower()

  return s


def check_lex_single(s):
  global dict_n
  global dict_pn
  global dict_rest
  if rex_2000.match(s):
    return 1 if s in dict_n or s in dict_pn else 0
  elif rex_2001.match(s):
    return 1 if s in dict_rest else 0
  else:
    return 1

# Returns for a list of: [0] lex percentage, [1] lex count, [2] total count
def check_lex(l):
  lex = [e for e in l if rex_2002.match(e)]
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

  # Very specific lexical defect of SMOR: does not know plural of "Ausfall".
  s = s.replace(u'aus<VPART>:#0#fa:älle:#0#n:#0#<V>:#0#<SUFF>:#0#<+NN>', u'\tAusfall')
  s = s.replace(u'aus<VPART>:#0#fälle:#0#n:#0#<V>:#0##0#:e#0#:n<SUFF>:#0#<+NN>', u'\tAusfall')

  debug('01 B\t' + s, 2)

  # Remove "Schreibweise" tags.
  s = rex_1010.sub(r'', s)

  # Get rid of verb prefix information as early as possible
  s = rex_020.sub(r'\1\3', s)
  s = rex_021.sub(r'', s, re.UNICODE)

  # Cardinals can also be fixed at beginning.
  # ... with extra rules first to fix misanalyses of "Neunziger" etc.
  s = rex_220.sub(r'er+KAP+', s)
  s = rex_221.sub(r'er+KAP+\t', s)
  
  s = rex_022.sub(r'\t\1\2-KAP-\t', s)
  s = rex_023.sub(r'\t\1-KAP-\t', s)

  debug('01 C\t' + s, 2)

  # Final "Betreuerin". Needs to be protected before other suffix rules apply.
  s = rex_024.sub(r'\1\2\3erin+KAP+<+NN>', s)
  s = rex_025.sub(r'\1erin+KAP+<+NN>', s)

  # Grobmotorikerin (triple NN suffixation).
  s = rex_026.sub(r'\1\2in+KAP+<+NN>', s)
  s = rex_027.sub(r'\1\2in+KAP+<+NN>', s)
  s = rex_028.sub(r'\1\2in+KAP+\t+nen\t', s)

  # Journalistin, Frauenrechtlerin etc. (double NN suffixation)
  s = rex_029.sub(r'\1in+KAP+<+NN>', s)
  s = rex_030.sub(r'\1in+KAP+\t+nen\t', s)
 
  # For some reason, yet another analysis of the same thing.
  s = rex_031.sub(r'\1\2erin+KAP+\t+nen\t', s)
  s = rex_032.sub(r'\1erin+KAP+\t+nen\t', s)

  debug('02\t' + s)

  # Very specific orthographic ss/ß conversions.
  s = rex_033.sub(u'ß', s)
  s = rex_034.sub(u'ss', s)
  s = rex_035.sub(u'ss', s)
  s = rex_036.sub(u'ss', s)
  s = rex_037.sub(u'ss', s)
  s = rex_038.sub(u'ss', s)

  debug('03\t' + s)

  # No distinction between NN and NE.
  s = s.replace(r'<NPROP>', r'<NN>')

  debug('04\t' + s)

  # Rescue original ablaut vowel in V>N derivations. "Annahme(verweigerung)"
  s = rex_039.sub(r'\1\3\4+KAP+\6\t+n\t', s)
  s = rex_040.sub(r'\1\3\4+KAP+\6\t', s)

  # ... final.
  s = rex_041.sub(r'\1\3\4\6+KAP+', s)

  # ... and deal with loan word plurals in final elements.
  s = rex_260.sub(r'\1', s)
  s = rex_261.sub(r'\1\2', s)

  # "Mitnahme" final.
  s = rex_042.sub(r'\2\3+KAP+', s)

  # "Anfänger" (middle).
  s = rex_043.sub(r'\1\2\3\4+KAP+\t', s)
  s = rex_044.sub(r'\1\2+KAP+\t', s)

  debug('05\t' + s)

  # Presevere "missing LE" notification.
  s = rex_045.sub(r'+KAP+\1\t+0\t', s)
 
  # Save KSF elements... Whatever.
  s = rex_046.sub(r'\t\1\t', s)

  debug('05 A\t' + s)

  # ...gebliebenen.
  s = rex_047.sub(r'\tge\1ie\2en-KAP-', s)
  s = rex_048.sub(r'\tge\1ie\2en-KAP-\t+en\t', s)

  debug('06\t' + s, 2)

  # "Umzug" from "ziehen". Wow!
  s = rex_049.sub(r'\1\2', s)
  s = rex_050.sub(r'\1\2', s)
  s = rex_051.sub(r'\1\2', s)
  s = rex_052.sub(r'\1', s)
  s = rex_053.sub(r'\1', s)
  s = rex_054.sub(r'\1', s)
  s = rex_055.sub(r'\1\2', s)
  s = rex_056.sub(r'\1\2', s)
  s = rex_057.sub(r'\1\2', s)
  s = rex_058.sub(r'+KAP+\1', s)

  debug('06 a\t' + s, 2)

  # "Stoß" as 0-derivation, final.
  s = rex_270.sub(r'+KAP+', s)
  s = rex_271.sub(r'+KAP+', s)

  debug('06 A\t' + s, 2)

  # The same, final.
  # e:ii:ege:<>n:<><V>:<><SUFF>:<><+NN>
  s = rex_059.sub(r'\1\2', s)
  s = rex_060.sub(r'\1\2', s)
  s = rex_061.sub(r'\1\2', s)
  s = rex_062.sub(r'\1', s)
  s = rex_063.sub(r'\1', s)
  s = rex_064.sub(r'\1', s)
  s = rex_065.sub(r'\1\2', s)
  s = rex_066.sub(r'\1\2', s)
  s = rex_067.sub(r'\1\2', s)

  debug('06 B\t' + s, 2)

  # Very specific V > PP > Adj > NN word formation. Final and non-final "Anspruchsberechtigte" etc. (also strong verbs).
  s = rex_068.sub(r'\t\1\2\3en-KAP-+ABL+\t', s)
  s = rex_069.sub(r'\t\1\2\3en-KAP-+ABL+\t', s)

  s = rex_070.sub(r'\t\1\2\3t-KAP-\t+en\t', s)
  s = rex_071.sub(r'\t\1\2\3t-KAP-\t', s)

  s = rex_072.sub(r'\t\1\2\3t-KAP-\t', s)
  s = rex_073.sub(r'\t\1\2\3t-KAP-\t+en\t', s)

  s = rex_074.sub(r'\t\1\2\3et-KAP-\t', s)
  s = rex_075.sub(r'\t\1\2\3et-KAP-\t+en\t', s)

  # No idea why this goes wrong otherwise: "Bodybuildingbegeistert".
  s = rex_076.sub(r'\t\1-KAP-', s)

  debug('06 C\t' + s, 2)

  s = rex_077.sub(r'end-KAP-', s)
  s = rex_078.sub(r'nd-KAP-', s)
  s = rex_079.sub(r'\1end-KAP-\t+en\t', s)
  s = rex_080.sub(r'\1nd-KAP-\t+en\t', s)

  debug('06 D\t' + s, 2)

  s = rex_081.sub(r'\1\2\3in+KAP+\t+nen\t', s)

  # N>N derivations "Brauch-tum", "Arbeiterschaft". There should be none with umlaut, and diminutives are dealt w/ sep.
  s = rex_082.sub(r'\1+KAP+\t+\2\t', s)
  s = rex_083.sub(r'\1\2\3+KAP+\t', s)
  
  debug('06 E\t' + s)

  # Undo other suffix analyses.

  # Remove the stupid "Rinnen" analyses.
  s = rex_084.sub(r'\1\2erin+KAP+', s)
  s = rex_085.sub(r'erin+KAP+', s)

  s = rex_086.sub(r'\1\2erin+KAP+\t+nen\t', s)
  s = rex_087.sub(r'erin+KAP+\t+nen\t', s)

  s = rex_088.sub(r'in+KAP+\t+nen<NN>:#0#', s)
  
  debug('06 F\t' + s)

  # Diminutives.
  s = rex_089.sub(r'\1\3\4\6+KAP+\t', s)
  s = rex_090.sub(r'\1\3\4\6+KAP+\t', s)

  # ... final.
  s = rex_091.sub(r'\1\3\4\6+KAP+\t', s)
  s = rex_093.sub(r'\1\3\4\6+KAP+\t', s)
  
  debug('06 G\t' + s)

  # Some NN suffixations.
  s = rex_094.sub(r'\1\2\3+KAP+', s)
  s = rex_095.sub(r'\1\2+KAP+', s)
  
  s = rex_096.sub(r'\1\2+KAP+\t+en\t', s)

  debug('07\t' + s)

  s = rex_097.sub(r'\1\2+KAP+\t+0\t', s)
  s = rex_098.sub(r'\1+KAP+\t+\2\t', s)

  debug('08\t' + s)

  # This one is critical: there might be more than 'erin'. But it breaks the V compound element detection when (\w+) is used instead of (erin).
  s = rex_099.sub(r'\1', s)

  debug('09\t' + s)

  s = rex_100.sub(r'\2+KAP+\t+\3\t', s)
  s = rex_100a.sub(r'\1+KAP+', s)
  s = rex_101.sub(r'\1\3\4\5<NN>:#0#', s)
  s = rex_102.sub(r'\1<NN>:#0#', s)
  s = rex_103.sub(r'\1\t', s)

  debug('10\t' + s)

  s = rex_104.sub(r'+KAP+\t', s)
  s = rex_105.sub(r'+KAP+', s)

  debug('11\t' + s)

  # Fix TRUNC.
  s = rex_106.sub(r'\1\t--\t', s)

  debug('13\t' + s)

  # Separate prefixes and ORD ("Dritt-mittel").
  s = rex_107.sub(r'\1\3~\t', s)
  s = rex_108.sub(r'~\t', s)

  debug('13 A\t' + s)

  # Some derivational affixes.
  s = rex_230.sub(r'\1\2+KAP+\t', s) # NN-ADJ-NN
  s = rex_231.sub(r'\1\2+KAP+\t+\3\t', s) # NN-ADJ-NN
  s = rex_232.sub(r'\1\2+KAP+\t+0\t', s) # NN-ADJ-NN
  
  s = rex_109.sub(r'\1-KAP-\t', s) # NN-ADJ

  s = rex_110.sub(r'\1\2\3+KAP+\t', s)
  s = rex_111.sub(r'\1\2\3-KAP-\t', s)
  s = rex_112.sub(r'\1\2\3-KAP-\t', s)
  s = rex_113.sub(r'\1\2+KAP+\t', s)
  s = rex_114.sub(r'\1\2-KAP-\t', s)
  s = rex_115.sub(r'\1\2-KAP-\t', s)
  s = rex_116.sub(r'\1+KAP+\t', s)
  s = rex_117.sub(r'\1-KAP-\t', s)
  s = rex_118.sub(r'\1-KAP-\t', s)

  # Fix "in nen".
  s = rex_119.sub(r'<+NN>', s)

  debug('13 B\t' + s, 2)

  # Comparatives and superlatives.

  s = rex_120.sub(r'\t\1\2\3er-KAP-', s)
  s = rex_121.sub(r'er-KAP-', s)
  s = rex_122.sub(r'\t\1\2\3er-KAP-\t+en\t', s)
  s = rex_123.sub(r'er-KAP-\t+en\t', s)

   
  s = rex_124.sub(r'\t\1\2\3er-KAP-\t', s)
  s = rex_125.sub(r'er-KAP-\t', s)
  
  s = rex_126.sub(r'\t\1\2\3st-KAP-', s)
  s = rex_127.sub(r'st-KAP-', s)

  s = rex_128.sub(r'\t\1\2\3st-KAP-\t', s)
  s = rex_129.sub(r'st-KAP-\t', s)
 
  s = rex_130.sub(r'\t\1\2\3st-KAP-\t+en\t', s)
  s = rex_131.sub(r'st-KAP-\t+en\t', s)

  debug('13 C\t' + s, 2)

  s = rex_200.sub(r'en-KAP-', s)
  s = rex_201.sub(r'en-KAP-', s)

  # rescue strange -ismus/en analyses.
  s = rex_301.sub(r'\1', s)

  debug('14\t' + s, 2)

  # First split. We will join & split again later.
  nouns = re.split(r'<NN>:#0#|\t|<ADJ>:#0#', s)

  debug('15\t' + "\t".join(nouns))

  # Separate and mark remaning FEs.
  nouns = [fix_fes(x) for x in nouns]

  debug('16\t' + "\t".join(nouns))

  # Clean elements containing suffixes.
  nouns = ['+KAP+' + rex_1001.sub(r'', x) if '<SUFF>' in x else x for x in nouns]

  debug('17\t' + "\t".join(nouns))

  # Split ADJ and V compound elements.
  nouns = [rex_1020.sub(r'-KAP-\t', x) for x in nouns]
  nouns = [rex_1021.sub(r'en-KAP-\t#en\t', x) for x in nouns]
  nouns = [rex_1022.sub(r'n-KAP-\t#n\t', x) for x in nouns]

  debug('18\t' + "\t".join(nouns))

  # Second split.
  nouns = '\t'.join(nouns).split('\t')

  debug('19\t' + "\t".join(nouns))

  # Some cleanups.
  nouns = [x.replace('<+NN>', '').strip() if not x == '+' else '' for x in nouns]
  nouns = [rex_1040.sub(r'', n) for n in nouns]

  debug('20\t' + "\t".join(nouns))

  # Do NOT keep umlaut in head noun. Is plural!
  nouns = nouns[:-1] + [rex_1041.sub(r'\1', nouns[-1])]

  debug('21\t' + "\t".join(nouns))

  # Move +KAP+ to end.
  nouns = [rex_1042.sub(r'', x) + '+KAP+' if '+KAP+' in x else x for x in nouns]
  nouns = [rex_1043.sub(r'', x) + '-KAP-' if '-KAP-' in x else x for x in nouns]

  debug('22\t' + "\t".join(nouns))

  # Make capitalization substitutions.
  nouns = [rex_1044.sub(r'\1', x) for x in nouns]
  nouns = [fix_cap(x) for x in nouns]

  debug('23\t' + "\t".join(nouns))

  # Clean remaining to/from-NULL substitutions.
  nouns = [substitute_nulls(x) for x in nouns]

  debug('24\t' + "\t".join(nouns))

  # Compact.
  nouns = filter(None, nouns)

  debug('25\t' + "\t".join(nouns), 3)

  return [nouns] + check_lex(nouns)


# Checks whether analysis contains : # or <.
def is_trash(a):
  ana = '_'.join(a[0])
  if rex_2003.match(ana):
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
    if rex_2004.match(l) or l == '>' or not l:

      if len(c_analyses) > 0 and c_token:

          # Remove trailing inflection analysis and useless ORTH info.
          c_analyses = [rex_1060.sub(r'\1', x).replace('<NEWORTH>','').replace('<OLDORTH>','') for x in c_analyses] 

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
          if len(nounalyses) > 0 and rex_2005.match(c_token):
            nounalyses = [e for e in nounalyses if len(e) > 0 and not e[0][-1] == 'Rinne' ]

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
            lexies = [e for e in nounalyses[0][0] if rex_2006.match(e)]
            fugies = [e[1:] for e in nounalyses[0][0] if rex_2007.match(e)]
            fugiestring = '|'+'|'.join(fugies)+'|' if len(fugies)>0 else '|'
            annotation = '\t'.join([c_token, '_'.join(nounalyses[0][0]), lexies[-1], '|'+'|'.join(lexies[:-1])+'|', fugiestring])
          elif not c_token == '>':
            annotation = '\t'.join([c_token] + NO_ANNO)
          else:
            annotation = ''

          ofh.write(annotation.encode('utf-8') + '\n')

      # Fresh start.
      c_analyses = list()
      c_token    = rex_1061.sub(r'', l.strip())

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
