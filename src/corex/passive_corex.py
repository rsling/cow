#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os.path
import sys
from corexreader import CORexReader as CX
from corex_basic import per, add_per
import codecs
import logging



tty_green = ''
tty_red   = ''
tty_cyan  = ''
tty_reset = ''


def passive_enable_color():
  global tty_green
  global tty_red
  global tty_cyan
  global tty_reset
  tty_green = '\033[1;32m'
  tty_red   = '\033[1;31m'
  tty_cyan  = '\033[1;36m'
  tty_reset = '\033[1;m'


def words_to_string(parent):
  b = []
  for word in parent.findall('.//*word'):
    b.append(word.text)
  line = " ".join(b) #+ "\n"
  return(line)


def get_dominating_simpx(element):
  while True:
    parent = element.getparent()
    if parent is not None:
      if parent.tag in ['simpx', 'rsimpx']: # 'fkonj' is experimental
        break
      elif parent.tag == '<s>':
        break
      else:
        element = parent
    else:
      parent = None
      break
  return(parent)


def get_dominating_lk2(vcparent):
  logging.debug('\t\tclause: ' + "'" + words_to_string(vcparent) + "'")

  # check if we have a non-verb-final structure (left bracket in verb-final clauses is "c", not "lk"):
  lks = vcparent.findall('lk')
  if lks == []:
    fkoords =  vcparent.findall('fkoord')
    if len(fkoords) > 0:
      fkonjs = []
      for fkoord in fkoords:
        fkonjs = fkonjs + fkoord.findall('fkonj')
        if len(fkonjs) > 0:
          for fkonj in fkonjs:
            lks = lks + fkonj.findall('lk')
  if lks == []:
    logging.debug('\t\tverb-final clause')
    logging.debug('\t\t\t\t' + tty_red + '=> NO PASSIVE' + tty_reset)
  logging.debug("\tNumber of LK found: " + str(len(lks)))

  return(lks)


# Selects the first lemma from a string denoting a "set" of lemmas.
def firstlemma(lemmastring):
  lemmastring = lemmastring.strip("|")
  lemmalist = lemmastring.split("|")
  return(lemmalist[0])


def get_wpl(enclosing_element):
  words = enclosing_element.findall('.//*word')
  pos =  enclosing_element.findall('.//*ttpos')
  lemmas =  enclosing_element.findall('.//*lemma')
  wwords = [w.text for w in words]
  ppos = [p.text for p in pos]
  lemmasetstrings =  [l.text for l in lemmas]
  llemmas = [firstlemma(l) for l in lemmasetstrings]
  return(wwords,ppos,llemmas)


def passive(doc):
  passcounter = 0

  for s in doc.iter('s'):
    logging.debug("")
    logging.debug(tty_cyan + words_to_string(s) + tty_reset)
    sent_passcounter = 0
    sent_perfcounter = 0

    # vc is not always a direct child of simpx (e.g. in coordination).
    for vc in s.findall('.//vc'):

      logging.debug("\tVC: " + "'" + words_to_string(vc) + "'")
      (wwords,ppos,llemmas) = get_wpl(vc)
      logging.debug("\tWords: " + " + ".join(wwords))
      logging.debug("\tTags: " + " + ".join(ppos))
      logging.debug("\tLemmas: " + " + ".join(llemmas))

      # most general case: verbal complex contains a participle (could be perfekt or passive)
      participles = [word for word in ppos if word == 'VVPP']
      logging.debug("\tParticiples: " + ", ".join(participles))
      if len(participles) > 0:
        has_passive = False
        logging.debug('\t\tpast participle found')

        for participle in participles:
          if "werden" in llemmas:
            for i in range(0,len(llemmas)):
              # experimental: "sein" must not occur before werden ("dass der Schaden auch bei rechtzeitiger Leistung eingetreten sein würde")
              if llemmas[i] == "werden" and ppos[i].startswith('VA') and llemmas[i-1] != 'sein':
                has_passive = True
                sent_passcounter += 1
                logging.debug('\t\tpassive aux found in verbal complex')
                logging.debug('\t\t\t' + tty_green + '=> PASSIVE' + tty_reset)
                break

        # get the left bracket of the immediately dominating <simplex>-element:
        if has_passive == False:
           logging.debug('\t\tno passive aux found in verbal complex')
           for participle in participles:
             vcparent = get_dominating_simpx(vc)

             if vcparent is not None:
              lks = get_dominating_lk2(vcparent)
              if lks == []:
                logging.debug('\t\t\tno left bracket filled with a verb in this clause')
                logging.debug('\t\t\t' + tty_red + '=> NO PASSIVE' + tty_reset)

             else:
               for lk in lks:
                 (wwords,ppos,llemmas) = get_wpl(lk)
                 logging.debug('\t\t\tleft bracket: ' + "'"  + " ".join(wwords)  + "'")

                 # check for passive axuiliary:
                 if llemmas[0] == 'werden' and ppos[0].startswith('VA'):
                   logging.debug("\t\t\tfound finite form: '" + wwords[0]  + "'")
                   logging.debug("\t\t\t\t" + tty_green + "=> PASSIVE" + tty_reset)
                   sent_passcounter += 1
                 else:
                   logging.debug("\t\t\tfound no finite form of 'werden'")
                   logging.debug("\t\t\t\t" + tty_red + "=> NO PASSIVE" + tty_reset)

      else:
        logging.debug("\t\tfound no past participle in verbal complex")
        logging.debug("\t\t\t" + tty_red + "=> NO PASSIVE" + tty_reset)

    passcounter = passcounter + sent_passcounter
    logging.debug("Total passive count: " + str(sent_passcounter))
    if sent_passcounter > 0:
      s.set('crx_pass', '1')
    else:
      s.set('crx_pass', '0')

  c_simpx = len(doc.findall('.//simpx'))
  c_psimpx = len(doc.findall('.//psimpx'))
  c_rsimpx = len(doc.findall('.//rsimpx'))

  add_per(doc, 'crx_pass', passcounter, c_simpx + c_psimpx + c_rsimpx, 1)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('infile', help='COW-XML input file')
  parser.add_argument('outfile', help='output file name')
  parser.add_argument('--annotations', type=str, help='comma-separated names for token annotations')
  parser.add_argument('--erase', action='store_true', help='erase existing output files')
  parser.add_argument('--verbose', action='store_true', help='print debugging output')

  args = parser.parse_args()

  if args.verbose:
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

  fn_out = args.outfile
  fn_in = args.infile

  # Check input files.
  infiles = [fn_in]
  for fn in infiles:
    if not os.path.exists(fn):
      sys.exit("Input file does not exist: " + fn)

  # Check (potentially erase) output files.
  outfiles = [fn_out]
  for fn in outfiles:
    if fn is not None and os.path.exists(fn):
      if args.erase:
        try:
          os.remove(fn)
        except:
          sys.exit("Cannot delete pre-existing output file: " + fn)
      else:
        sys.exit("Output file already exists: " + fn)

  # Split annos
  annos = list()
  if args.annotations:
    annos = args.annotations.split(',')

  # Create corpus iterator. 
  corpus_in = CX(fn_in, annos=annos)

  # open output file:
  outfile = open(fn_out, 'w')

  for doc in corpus_in:
    perfect(doc)
    outfile.write(outify(doc) + "\n")

if __name__ == "__main__":
  main()
