# -*- coding: utf-8 -*-

from corexreader import CORexReader as CX
from corexreader import outify
from corex_basic import per, add_per
import re
import logging


sein_part_re = re.compile('.*ge(gangen|fallen|laufen|flogen|wachsen|fahren|reist|schritten|geblieben|sprungen|kommen|blieben|drungen|wichen|stiegen|worden|stehen|taucht|storben|rutscht|rannt)')


sein_part_set = set([u'geboren', u'gelungen', u'verhungert', u'zusammengebrochen', u'verklungen', u'passiert', u'weggezogen', u'fehlgeschlagen', u'geschehen', u'verreist', u'geflohen', u'gestoßen', u'gestossen', u'gewandert', u'begegnet', u'verschmolzen', u'abgekühlt', u'versunken', u'eingeschlafen', u'gestrandet', u'abgebogen', u'misslungen', u'explodiert', u'gekrochen', u'ausgetrocknet', u'ausgetreten', u'worden', u'zerfallen', u'abgehauen', u'gestürzt', u'abgewandert', u'geplatzt', u'ertrunken', u'erschienen', u'erwachsen', u'verschwunden', u'widerfahren', u'zerbrochen', u'eingetreten', u'gestartet', u'verstrichen', u'entkommen', u'zugestoßen', u'zugestossen', u'verblieben', u'gelandet', u'gefolgt', u'abgestürzt', u'aufgesessen', u'geschlüpft', u'entwachsen', u'abgebrannt', u'geraten', u'umgezogen', u'eingeschlagen', u'bekommen', u'geklettert', u'gereift', u'dagewesen', u'gewesen', u'auferstanden', u'zurückgetreten', u'gekippt', u'vergangen', u'eingebrochen', u'geschwommen', u'gelangt', u'erschrocken', u'eingestürzt', u'geschmolzen', u'verflogen', u'hervorgetreten', u'mutiert', u'verheilt', u'unterlaufen', u'ergangen', u'beigetreten', u'ausgezogen', u'ausgewandert', u'erwacht', u'aufgestanden', u'eingewandert', u'erfolgt', u'gescheitert', u'aufgewacht', u'geflüchtet', u'entsprungen', u'überlaufen', u'zugezogen', u'angetreten', u'gestolpert', u'eingeflossen', u'entstanden', u'geglückt', u'gestanden', u'abgeklungen', u'angeschwollen', u'entgangen', u'geschrumpft', u'gesunken', u'zerrissen', u'verfallen', u'aufgetreten', u'ausgebrochen', u'verkommen', u'verstorben', u'abgezogen', u'erloschen', u'ausgeschieden', u'durchgebrannt', u'verunglückt', u'abgesunken'])


oberfeld_re = re.compile('VAFIN(?: V.INF)+')


ersatzinfinitives_set = set([u'sehen', u'hören', u'fühlen', u'lassen', u'wollen', u'müssen', u'dürfen', u'sollen', u'können', u'mögen', u'spüren'])


tty_green = ''
tty_red   = ''
tty_cyan  = ''
tty_yellow  = ''
tty_reset = ''


def perfect_enable_color():
  global tty_green
  global tty_red
  global tty_cyan
  global tty_yellow
  global tty_reset
  tty_green   = '\033[1;32m'
  tty_red     = '\033[1;31m'
  tty_cyan    = '\033[1;36m'
  tty_yellow  = '\033[1;33m'
  tty_reset   = '\033[1;m'


def words_to_string(parent):
  b = []
  for word in parent.findall('.//*word'):
    b.append(word.text)
  line = ' '.join(b) 
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


# Check for a non-verb-final structure (left bracket in verb-final clauses is 'c', not 'lk').
def get_dominating_lk(vc):
  current = vc
  lks = []
  while True:
    parent = get_dominating_X(current)

    if parent is not None:
      lks =  parent.findall('.//lk')
      tags = [i.tag for i in lks]
      logging.debug('\t\t\t\tLKS: ' + ' + '.join(tags))
      if len(lks) > 0:
        logging.debug('\t\t\t\tFound LK in clause: ' + words_to_string(parent))
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
  lemmastring = lemmastring.strip('|')
  lemmalist = lemmastring.split('|')
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


# Returns tokens tagged as 'V.PP'.
def participles2tokens(wwords, ttttpos, llemmas, mmpos):

  # TODO Mayba add VMPP?
  part_set = set([u'VVPP', u'VAPP']) 
  words_pos_lemmas_mmpos = zip(wwords, ttttpos, llemmas, mmpos)

  # Sometimes, Marmot gets the pos tag V.PP correct when TreeTagger thinks its V.FIN.
  participletokens = [word for (word, pos, lemma, mpos) in words_pos_lemmas_mmpos if (pos in part_set or mpos in part_set)]
  return(participletokens)



# Returns (a list of) tokens tagged as infinitive.
def infinitives2tokens(wwords, ttttpos):
  words_pos = zip(wwords, ttttpos)
  inf_set =  set([u'VVINF', u'VAINF', u'VMINF'])
  infinitivetokens = [word for (word, pos) in words_pos if pos in inf_set]
  return(infinitivetokens)


# Returns (a list of) tokens tagged as 'VVFIN' or 'VMINF' and that can form ersatzinfinitives.
def ersatzinfinitives_candidates(wwords, ttttpos, llemmas):
  words_pos_lemmas = zip(wwords, ttttpos, llemmas)
  ersatzposlist = [u'VVINF', u'VMINF']
  ersatzcandidatetokens = [word for (word, pos, lemma) in words_pos_lemmas if pos in ersatzposlist and lemma in ersatzinfinitives_set]
  return(ersatzcandidatetokens)


def perfect(doc):
  doc_perfcounter = 0
  doc_pluperfcounter = 0

  for s in doc.iter('s'):
    logging.debug('')
    logging.debug(tty_cyan + words_to_string(s) + tty_reset)
    sent_perfcounter = 0
    sent_pluperfcounter = 0

    # vc is not always a direct child of simpx (e.g. in coordination).
    for vc in s.findall('.//vc'):
      logging.debug('\tVC: ' + words_to_string(vc))
      (wwords,ttttpos,llemmas,mmpos,mmorph) = get_wplpm(vc)

      # Most general case: verbal complex contains a participle.
      participles = participles2tokens(wwords, ttttpos, llemmas, mmpos)
      infinitives = infinitives2tokens(wwords, ttttpos)
      ersatzcandidates = ersatzinfinitives_candidates(wwords, ttttpos, llemmas)
      participles_and_ersatzinfs = participles + ersatzcandidates

      logging.debug('\tAll tokens in this VC: ' + ' + '.join(wwords))
      logging.debug('\tAll tags in this VC: ' + ' + '.join(ttttpos))
      logging.debug('\tAll lemmas in this VC: ' + ' + '.join(llemmas))
      logging.debug('\tAll participles in this VC: ' + ' + '.join(participles))
      logging.debug('\tAll infinitives in this VC: ' + ' + '.join(infinitives))
      logging.debug('\tAll potential ersatzinfinitives: ' + ' + '.join(ersatzcandidates))

      if len(participles_and_ersatzinfs) > 0:
        logging.debug('\t\tpast participle(s) and infinitives found: ' + ' + '.join(participles_and_ersatzinfs))

        # Check if verbal complex ends with a perfect aux.
        logging.debug('\t\tParticiplelist before processing first participle: ' + ' + '.join(participles_and_ersatzinfs))
        donelist = []

        for participle in participles_and_ersatzinfs:
          logging.debug('\t\t\tNow processing participle: ' + participle + ' (analyzing verbal complex)')
          if ttttpos[-1] == 'VAFIN':
            candidate = wwords[-1]
            logging.debug('Last word in VC: ' + candidate)
            if llemmas[-1] == u'haben':

              # Check tense.
              # Don't rely on Marmot morph annotations:
              # there will be no annotation if Marmot thinks it is 'VAINF'.
              if haben_pres(candidate):
                sent_perfcounter += 1
                donelist.append(participle)
                logging.debug('\t\t[A] Finite perfect aux (pres) found in verbal complex: ' + candidate)
                logging.debug('\t\t\t' + tty_green + '=> PERFECT' + tty_reset)
              elif haben_past(candidate):
                sent_pluperfcounter += 1
                logging.debug('\t\t[B] Finite perfect aux (past) found in verbal complex: ' + candidate)
                logging.debug('\t\t\t' + tty_green + '=> PLUPERFECT' + tty_reset)

            elif llemmas[-1] == u'sein':

              # Check if participle is among those that take 'sein' as perfect tense auxiliary.
              if sein_part_re.match(participle) or participle in sein_part_set:
                if sein_pres(candidate):
                  sent_perfcounter += 1
                  logging.debug('\t\t[C] Finite perfect aux (pres) found in verbal complex: ' + candidate)
                  logging.debug('\t\t\t' + tty_green + '=> PERFECT' + tty_reset)
                elif sein_past(candidate):
                  sent_pluperfcounter += 1
                  logging.debug('\t\t[D] Finite perfect aux (past) found in verbal complex: ' + candidate)
                  logging.debug('\t\t\t' + tty_green + '=> PLUPERFECT' + tty_reset)

            logging.debug('\t\tParticiplelist after processing one participle (aux in vc): ' + ' + '.join(participles_and_ersatzinfs))

          # Get the left bracket of the immediately dominating fkonj, fkord or simplex-element.
          else:
            logging.debug('\t\t\t\tNo perfect aux found in verbal complex.')

        logging.debug('\t\tParticiplelist after processing all participles (looking for aux in vc): ' + ' + '.join(participles_and_ersatzinfs))

        # Make sure we do not process a participle twice.
        logging.debug('\t\tDonelist: ' + ' + '.join(donelist))
        participles_and_ersatzinfs = [participle for participle in participles_and_ersatzinfs if not participle in donelist]
        logging.debug('\t\tRemaining part_and_ersatzinfs: '  + ' + '.join(participles_and_ersatzinfs))

        for participle in participles_and_ersatzinfs:
          logging.debug('\t\t\tNow processing participle: ' + participle)
          logging.debug('\t\t\tLooking for a left bracket...')
          lks = get_dominating_lk(vc)

          if lks == []:
            pass

          else:
            for lk in lks:
              (wwords,ttttpos,llemmas,mmpos,mmorph) = get_wplpm(lk)
              logging.debug('\t\t\t\tLeft bracket: ' + ' '.join(wwords))

              # check for perfect auxiliary in left bracket:
              if  ttttpos[0] == u'VAFIN':
                candidate =  wwords[0]
                if llemmas[0] == u'haben':
                  if haben_pres(candidate):
                    logging.debug('\t\t\t\t[E] Finite perfect aux (pres) found in left bracket: ' + candidate)
                    logging.debug('\t\t\t\t' + tty_green + '=> PERFECT' + tty_reset)
                    sent_perfcounter += 1
                  elif haben_past(candidate):
                    logging.debug('\t\t\t\t[F] Finite perfect aux (past) found in left bracket: ' + candidate)
                    logging.debug('\t\t\t\t' + tty_green + '=> PLUPERFECT' + tty_reset)
                    sent_pluperfcounter += 1
                elif llemmas[0] == u'sein':
                  if sein_part_re.match(participle) or participle in sein_part_set:
                    if sein_pres(candidate):
                      sent_perfcounter += 1
                      logging.debug('\t\t\t\t[G] Finite perfect aux (pres) found in left bracket: ' + candidate)
                      logging.debug('\t\t\t\t' + tty_green + '=> PERFECT' + tty_reset)
                    elif sein_past(candidate):
                      sent_pluperfcounter += 1
                      logging.debug('\t\t\t\t[H] Finite perfect aux (past) found in left bracket: ' + candidate)
                      logging.debug('\t\t\t\t' + tty_green + '=> PLUPERFECT' + tty_reset)
                logging.debug('Found a suitable aux: ' + candidate + ' + stop searching for more LKs.')

                # Stop looking for aux in further lk when one suitable aux has been found.
                break

              # No perfect auxiliary in left bracket.
              else:
                logging.debug('\t\t\t\tNo finite perfect aux in left bracket.')

      else:
        logging.debug('\t\tNo past participle or infinitive found in verbal complex.')
        logging.debug('\t\t\t' + tty_red + '=> NO PERFECT' + tty_reset)

    # Check for Oberfeldumstellung with Ersatzinfinitiv
    # (no point in using topo-parse information here, it's almost always incorrect).
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
              if lastlemma in ersatzinfinitives_set:
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



    ttttpos_string = ' '.join(ttttpos)
    logging.debug('\tAll pos tags in this <simpx>: ' + ttttpos_string)
    ofu = oberfeld_re.findall(ttttpos_string)
    logging.debug('\tOberfeldumstellung + sequence: ' + ' + '.join(ofu))
    logging.debug(tty_yellow + 'Total perfect in this sentence:' + str(sent_perfcounter) + tty_reset)
    logging.debug(tty_yellow + 'Total pluperfect in this sentence:' + str(sent_pluperfcounter) + tty_reset)

    s.set('perfects', str(sent_perfcounter))
    s.set('pluperfects', str(sent_pluperfcounter))

    doc_perfcounter = doc_perfcounter + sent_perfcounter
    pluperfcounter = doc_pluperfcounter + sent_pluperfcounter

  # Unit of reference is 1 simpx (including subtypes of simpx).
  c_simpx = len(doc.findall('.//simpx'))
  c_psimpx = len(doc.findall('.//psimpx'))
  c_rsimpx = len(doc.findall('.//rsimpx'))
  add_per(doc, 'crx_perf', doc_perfcounter, c_simpx + c_psimpx + c_rsimpx, 1)
  add_per(doc, 'crx_plu', doc_pluperfcounter, c_simpx + c_psimpx + c_rsimpx, 1)


