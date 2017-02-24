#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os.path
import sys
from corexreader import CORexReader as CX
from corexreader import outify
from corex_basic import per, add_per
import codecs
import re
import logging

sein_part_re = re.compile('.*ge(gangen|fallen|laufen|flogen|wachsen|fahren|reist|schritten|geblieben|sprungen|kommen|blieben|drungen|wichen|stiegen|worden|stehen|taucht|storben|rutscht|rannt)')

sein_part_restdic = {u'geboren': '', u'gelungen': '', u'verhungert': '', u'zusammengebrochen': '', u'verklungen': '', u'passiert': '', u'weggezogen': '', u'fehlgeschlagen': '', u'geschehen': '', u'verreist': '', u'geflohen': '', u'gesto\xdfen': '', u'gewandert': '', u'begegnet': '', u'verschmolzen': '', u'abgek\xfchlt': '', u'versunken': '', u'eingeschlafen': '', u'gestrandet': '', u'abgebogen': '', u'misslungen': '', u'explodiert': '', u'gekrochen': '', u'ausgetrocknet': '', u'ausgetreten': '', u'worden': '', u'zerfallen': '', u'abgehauen': '', u'gest\xfcrzt': '', u'abgewandert': '', u'geplatzt': '', u'ertrunken': '', u'erschienen': '', u'erwachsen': '', u'verschwunden': '', u'widerfahren': '', u'zerbrochen': '', u'eingetreten': '', u'gestartet': '', u'verstrichen': '', u'entkommen': '', u'zugesto\xdfen': '', u'verblieben': '', u'gelandet': '', u'gefolgt': '', u'abgest\xfcrzt': '', u'aufgesessen': '', u'geschl\xfcpft': '', u'entwachsen': '', u'abgebrannt': '', u'geraten': '', u'umgezogen': '', u'eingeschlagen': '', u'bekommen': '', u'geklettert': '', u'gereift': '', u'dagewesen': '', u'gewesen': '', u'auferstanden': '', u'zur\xfcckgetreten': '', u'gekippt': '', u'vergangen': '', u'eingebrochen': '', u'geschwommen': '', u'gelangt': '', u'erschrocken': '', u'eingest\xfcrzt': '', u'geschmolzen': '', u'verflogen': '', u'hervorgetreten': '', u'mutiert': '', u'verheilt': '', u'unterlaufen': '', u'ergangen': '', u'beigetreten': '', u'ausgezogen': '', u'ausgewandert': '', u'erwacht': '', u'aufgestanden': '', u'eingewandert': '', u'erfolgt': '', u'gescheitert': '', u'aufgewacht': '', u'gefl\xfcchtet': '', u'entsprungen': '', u'\xfcberlaufen': '', u'zugezogen': '', u'angetreten': '', u'gestolpert': '', u'eingeflossen': '', u'entstanden': '', u'gegl\xfcckt': '', u'gestanden': '', u'abgeklungen': '', u'angeschwollen': '', u'entgangen': '', u'geschrumpft': '', u'gesunken': '', u'zerrissen': '', u'verfallen': '', u'aufgetreten': '', u'ausgebrochen': '', u'verkommen': '', u'verstorben': '', u'abgezogen': '', u'erloschen': '', u'ausgeschieden': '', u'durchgebrannt': '', u'verungl\xfcckt': '', u'abgesunken': ''}

oberfeld_re = re.compile('VAFIN(?: V.INF)+')

ersatzinfinitives_dict = {u'sehen': '', u'hören': '', u'fühlen': '', u'lassen': '', u'wollen': '', u'müssen': '', u'dürfen': '', u'sollen': '', u'können': '', u'mögen': '', u'spüren': ''} # more verbs here?


tty_green = ''
tty_red   = ''
tty_cyan  = ''
tty_reset = ''


def perfect_enable_color():
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


def get_dominating_X(element):
  while True:
    parent = element.getparent()
    if parent is not None:
      if parent.tag in ['simpx', 'rsimpx', 'fkonj', 'fkoord']:
        break
      elif parent.tag == '<s>':
        break
      else:
        element = parent
    else:
      parent = None
      break
  return(parent)


# check if we have a non-verb-final structure (left bracket in verb-final clauses is "c", not "lk")
def get_dominating_lk(vc):
  current = vc
  lks = []
  while True:
    parent = get_dominating_X(current)

    if parent is not None:
      logging.debug('\t\t\t\tLooking for LK in clause: ' + "'" + words_to_string(parent) + "'" + " (" + parent.tag + ")")
      lks =  parent.findall('.//lk')
      tags = [i.tag for i in lks]
      logging.debug("\t\t\t\tLKS: " + " + ".join(tags))
      if len(lks) > 0:
        logging.debug('\t\t\t\tFound LK in clause: ' + "'" + words_to_string(parent) + "'")
        break
      else:
        if parent.tag.endswith('simpx'):
          break
        else:
          current = parent
    else:
      break
  return(lks)


def firstlemma(lemmastring):
  lemmastring = lemmastring.strip("|")
  lemmalist = lemmastring.split("|")
  return(lemmalist[0])


def get_wplpm(enclosing_element):
  words = enclosing_element.findall('.//*word')
  ttpos =  enclosing_element.findall('.//*ttpos')
  lemmas =  enclosing_element.findall('.//*lemma')
  mpos =  enclosing_element.findall('.//*mpos')
  morph =  enclosing_element.findall('.//*morph')

  wwords = [w.text for w in words]
  ttttpos = [p.text for p in ttpos]
  lemmasetstrings =  [l.text for l in lemmas]
  llemmas = [firstlemma(l) for l in lemmasetstrings]
  mmpos = [p.text for p in mpos]
  mmorph =  [m.text for m in morph]

  return(wwords,ttttpos,llemmas,mmpos,mmorph)


def verbose(verbosearg,sentencelist):
  if verbosearg == True:
    for s in sentencelist:
      sys.stderr.write(s.encode('utf-8'))


def haben_pres(candidate):
  if candidate.lower() in [u'habe', u'hab', u'hast', u'habest', u'hat', u'haben', u'habt', u'habet']:
    return(True)
  else:
    return(False)

def haben_past(candidate):
  if candidate.lower() in  [u'hatte', u'hätte', u'hattest', u'hättest', u'hatten', u'hätten', u'hattet', u'hättet']:
    return(True)
  else:
    return(False)


def sein_pres(candidate):
  if candidate.lower() in [u'bin', u'bist', u'ist', u'sind', u'seid', u'sind', u'sei', u'seist', u'seiest', u'seien', u'seiet']:
    return(True)
  else:
    return(False)

def sein_past(candidate):
  if candidate.lower() in  [u'war', u'warst', u'waren', u'wart', u'wäre', u'wärst', u'wär', u'wären', u'wärt', u'wäret']:
    return(True)
  else:
    return(False)


# returns tokens tagged as 'V.PP'
def participles2tokens(wwords, ttttpos, llemmas, mmpos):
  part_dict = {u'VVPP': '', u'VAPP':''} # plus VMPP?
  words_pos_lemmas_mmpos = zip(wwords, ttttpos, llemmas, mmpos)

  # sometimes, Marmot gets the pos tag V.PP correct when TreeTagger thinks its V.FIN:
  participletokens = [word for (word, pos, lemma, mpos) in words_pos_lemmas_mmpos if (pos in part_dict or mpos in part_dict)]
  return(participletokens)



# Returns (a list of) tokens tagged as infinitive.
def infinitives2tokens(wwords, ttttpos):
  words_pos = zip(wwords, ttttpos)
  infdict =  {u'VVINF': '', u'VAINF': '', u'VMINF': ''}
  infinitivetokens = [word for (word, pos) in words_pos if pos in infdict]
  return(infinitivetokens)


# Returns (a list of) tokens tagged as 'VVFIN' or 'VMINF' and that can form ersatzinfinitives.
def ersatzinfinitives_candidates(wwords, ttttpos, llemmas):
  words_pos_lemmas = zip(wwords, ttttpos, llemmas)
  ersatzposlist = [u'VVINF', u'VMINF']
  ersatzcandidatetokens = [word for (word, pos, lemma) in words_pos_lemmas if pos in ersatzposlist and lemma in ersatzinfinitives_dict]
  return(ersatzcandidatetokens)


def perfect(doc):
  perfcounter = 0
  pluperfcounter = 0

  for s in doc.iter('s'):
    logging.debug("")
    logging.debug(tty_cyan + words_to_string(s) + tty_reset)
    sent_perfcounter = 0
    sent_pluperfcounter = 0

    # vc is not always a direct child of simpx (e.g. in coordination).
    for vc in s.findall('.//vc'):
      logging.debug("\tVC: " + "'" + words_to_string(vc) + "'")
      (wwords,ttttpos,llemmas,mmpos,mmorph) = get_wplpm(vc)

      # Most general case: verbal complex contains a participle.
      participles = participles2tokens(wwords, ttttpos, llemmas, mmpos)
      infinitives = infinitives2tokens(wwords, ttttpos)
      ersatzcandidates = ersatzinfinitives_candidates(wwords, ttttpos, llemmas)
      participles_and_ersatzinfs = participles + ersatzcandidates

      logging.debug("\tAll tokens in this VC: " + " + ".join(wwords))
      logging.debug("\tAll tags in this VC: " + " + ".join(ttttpos))
      logging.debug("\tAll lemmas in this VC: " + " + ".join(llemmas))
      logging.debug("\tAll participles in this VC: " + " + ".join(participles))
      logging.debug("\tAll infinitives in this VC: " + " + ".join(infinitives))
      logging.debug("\tAll potential ersatzinfinitives: " + " + ".join(ersatzcandidates))

      if len(participles_and_ersatzinfs) > 0:
        logging.debug('\t\tpast participle(s) and infinitives found: ' + ' + '.join(participles_and_ersatzinfs))

        # Check if verbal complex ends with a perfect aux.
        logging.debug("\t\tParticiplelist before processing first participle: " + " + ".join(participles_and_ersatzinfs))
        donelist = []

        for participle in participles_and_ersatzinfs:
          logging.debug("\t\t\tNow processing participle: " + participle + ' (analyzing verbal complex)')
          if ttttpos[-1] == 'VAFIN':
            candidate = wwords[-1]
            logging.debug("Last word in VC: " + candidate)
            if llemmas[-1] == "haben":

              # Check tense.
              # Don't rely on Marmot morph annotations:
              # there will be no annotation if Marmot thinks it is 'VAINF'.
              if haben_pres(candidate):
                sent_perfcounter += 1
                donelist.append(participle)
                logging.debug('\t\tA finite perfect aux (pres) found in verbal complex: ' + candidate)
                logging.debug('\t\t\t' + tty_green + '=> PERFECT' + tty_reset)
              elif haben_past(candidate):
                sent_pluperfcounter += 1
                logging.debug('\t\tB finite perfect aux (past) found in verbal complex: ' + candidate)
                logging.debug('\t\t\t' + tty_green + '=> PLUPERFECT' + tty_reset)

            elif llemmas[-1] == "sein":

              # Check if participle is among those that take 'sein' as perfect tense auxiliary.
              if sein_part_re.match(participle) or participle in sein_part_restdic:
                if sein_pres(candidate):
                  sent_perfcounter += 1
                  logging.debug('\t\tC finite perfect aux (pres) found in verbal complex: ' + candidate)
                  logging.debug('\t\t\t' + tty_green + '=> PERFECT' + tty_reset)
                elif sein_past(candidate):
                  sent_pluperfcounter += 1
                  logging.debug('\t\tD finite perfect aux (past) found in verbal complex: ' + candidate)
                  logging.debug('\t\t\t' + tty_green + '=> PLUPERFECT' + tty_reset)

            logging.debug("\t\tParticiplelist after processing one participle (aux in vc): " + " + ".join(participles_and_ersatzinfs))

          # Get the left bracket of the immediately dominating fkonj, fkord or simplex-element.
          else:
            logging.debug('\t\t\t\tno perfect aux found in verbal complex')

        logging.debug("\t\tParticiplelist after processing all participles (looking for aux in vc): " + " + ".join(participles_and_ersatzinfs))

        # Make sure we do not process a participle twice.
        logging.debug("\t\tDonelist: " + " + ".join(donelist))
        participles_and_ersatzinfs = [participle for participle in participles_and_ersatzinfs if not participle in donelist]
        logging.debug("\t\tRemaining part_and_ersatzinfs: "  + " + ".join(participles_and_ersatzinfs))

        for participle in participles_and_ersatzinfs:
          logging.debug("\t\t\tNow processing participle: " + participle)
          logging.debug("\t\t\tLooking for a left bracket")
          lks = get_dominating_lk(vc)
          if lks == []:
            pass
          else:
            for lk in lks:
              (wwords,ttttpos,llemmas,mmpos,mmorph) = get_wplpm(lk)
              logging.debug('\t\t\t\tleft bracket: ' + "'"  + " ".join(wwords)  + "'")

              # check for perfect auxiliary in left bracket:
              if  ttttpos[0] == ('VAFIN'):
                candidate =  wwords[0]
                if llemmas[0] == 'haben':
                  if haben_pres(candidate):
                    logging.debug('\t\t\t\tE finite perfect aux (pres) found in left bracket: ' + candidate)
                    logging.debug('\t\t\t\t' + tty_green + '=> PERFECT' + tty_reset)
                    sent_perfcounter += 1
                  elif haben_past(candidate):
                    logging.debug('\t\t\t\tF finite perfect aux (past) found in left bracket: ' + candidate)
                    logging.debug('\t\t\t\t' + tty_green + '=> PLUPERFECT' + tty_reset)
                    sent_pluperfcounter += 1
                elif llemmas[0] == 'sein':
                  if sein_part_re.match(participle) or participle in sein_part_restdic:
                    if sein_pres(candidate):
                      sent_perfcounter += 1
                      logging.debug('\t\t\t\tG finite perfect aux (pres) found in left bracket: ' + candidate)
                      logging.debug('\t\t\t\t' + tty_green + '=> PERFECT' + tty_reset)
                    elif sein_past(candidate):
                      sent_pluperfcounter += 1
                      logging.debug('\t\t\t\tH finite perfect aux (past) found in left bracket: ' + candidate)
                      logging.debug('\t\t\t\t' + tty_green + '=> PLUPERFECT' + tty_reset)
                logging.debug('Found a suitable aux: ' + candidate + ' + stop searching for more LKs')
                break # stop looking for aux in further lk when one suitable aux has been found
              # no perfect auxiliary in left bracket:
              else:
                logging.debug("\t\t\t\tno finite perfect aux in left bracket")

      else:
        logging.debug("\t\tNo past participle or infinitive found in verbal complex")
        logging.debug("\t\t\t" + tty_red + "=> NO PERFECT" + tty_reset)

    # check for Oberfeldumstellung with Ersatzinfinitiv
    # (no point in using topo-parse information here, it's almost always incorrect)
    (wwords,ttttpos,llemmas,mmpos,mmorph) = get_wplpm(s)
    words_and_tags_and_lemmas = zip(wwords,ttttpos,llemmas)
    for i in range(0, len(words_and_tags_and_lemmas)):
      if words_and_tags_and_lemmas[i][1] == 'VAFIN':
        lastlemma = words_and_tags_and_lemmas[i][2]
        infcounter = 1
        while True:
          try:
            (nextword, nextpos, nextlemma) = words_and_tags_and_lemmas[i+infcounter]
            if nextpos in ['VVINF', 'VAINF', 'VMINF']:
              lastlemma = nextlemma
              infcounter += 1
            else:
              if lastlemma in ersatzinfinitives_dict:
                candidate = wwords[i]
                if haben_pres(candidate):
                  logging.debug('\t\t\t\tI Oberfeldumstellung + finite perfect aux (pres) found in verbal complex: ' + candidate)
                  logging.debug('\t\t\t\t' + tty_green + '=> PERFECT' + tty_reset)
                  sent_perfcounter += 1
                elif haben_past(candidate):
                  logging.debug('\t\t\t\tJ Oberfeldumstellung + finite perfect aux (past) found in verbal complex: ' + candidate)
                  logging.debug('\t\t\t\t' + tty_green + '=> PLUPERFECT' + tty_reset)
                  sent_pluperfcounter += 1
              break
          except IndexError:
            break



    ttttpos_string = " ".join(ttttpos)
    logging.debug("\tAll pos tags in this <simpx>: " + ttttpos_string)
    ofu = oberfeld_re.findall(ttttpos_string)
    logging.debug("\tOberfeldumstellung + sequence: " + " + ".join(ofu))
    logging.debug(" " + 'Total perfect in this sentence:' + str(sent_perfcounter))
    logging.debug(" " + 'Total plu-perfect in this sentence:' + str(sent_pluperfcounter) + '')

    if sent_perfcounter > 0:
      s.set('crx_perf', '1')
    else:
      s.set('crx_perf', '0')

    if sent_pluperfcounter > 0:
      s.set('crx_plu', '1')
    else:
      s.set('crx_plu', '0')

    perfcounter = perfcounter + sent_perfcounter
    pluperfcounter = pluperfcounter + sent_pluperfcounter

  c_simpx = len(doc.findall('.//simpx'))
  c_psimpx = len(doc.findall('.//psimpx'))
  c_rsimpx = len(doc.findall('.//rsimpx'))

  add_per(doc, 'crx_perf', perfcounter, c_simpx + c_psimpx + c_rsimpx, 1)
  add_per(doc, 'crx_plu', pluperfcounter, c_simpx + c_psimpx + c_rsimpx, 1)


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
