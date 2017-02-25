# -*- coding: utf-8 -*-

from corex_basic import per, add_per
import logging



tty_green   = ''
tty_red     = ''
tty_cyan    = ''
tty_yellow  = ''
tty_reset   = ''


def passive_enable_color():
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


def get_dominating_simpx(element):
  while True:
    parent = element.getparent()
    if parent is not None:

      # TODO Maybe 'fkonj' also?
      if parent.tag in ['simpx', 'rsimpx']:
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
  logging.debug('\t\tClause: ' + words_to_string(vcparent))

  # Check for a non-verb-final structure (left bracket in verb-final clauses is 'c', not 'lk').
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
    logging.debug('\t\tIs a verb-final clause.')
    logging.debug('\t\t\t\t' + tty_red + '=> NO PASSIVE' + tty_reset)
  logging.debug('\tNumber of LK found: ' + str(len(lks)))

  return(lks)


# Selects the first lemma from a string denoting a set of lemmas.
def firstlemma(lemmastring):
  lemmastring = lemmastring.strip('|')
  lemmalist = lemmastring.split('|')
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
    logging.debug('')
    logging.debug(tty_cyan + words_to_string(s) + tty_reset)
    sent_passcounter = 0
    sent_perfcounter = 0

    # vc is not always a direct child of simpx (e.g. in coordination).
    for vc in s.findall('.//vc'):

      logging.debug('\tVC: ' + words_to_string(vc))
      (wwords,ppos,llemmas) = get_wpl(vc)
      logging.debug('\tWords: ' + ' + '.join(wwords))
      logging.debug('\tTags: ' + ' + '.join(ppos))
      logging.debug('\tLemmas: ' + ' + '.join(llemmas))

      # Most general case: verbal complex contains a participle (could be perfekt or passive).
      participles = [word for word in ppos if word == 'VVPP']
      logging.debug('\tParticiples: ' + ', '.join(participles))
      if len(participles) > 0:
        has_passive = False
        logging.debug('\t\tPast participle found.')

        for participle in participles:
          if u'werden' in llemmas:
            for i in range(0,len(llemmas)):

              # Experimental: 'sein' must not occur before werden
              # ('dass der Schaden auch bei rechtzeitiger Leistung eingetreten sein würde').
              if llemmas[i] == u'werden' and ppos[i].startswith('VA') and llemmas[i-1] != u'sein':
                has_passive = True
                sent_passcounter += 1
                logging.debug('\t\tPassive aux found in verbal complex.')
                logging.debug('\t\t\t' + tty_green + '=> PASSIVE' + tty_reset)
                break

        # Get the left bracket of the immediately dominating <simplex>-element.
        if has_passive == False:
           logging.debug('\t\tNo passive aux found in verbal complex.')
           for participle in participles:
             vcparent = get_dominating_simpx(vc)

             if vcparent is not None:
              lks = get_dominating_lk2(vcparent)
              if lks == []:
                logging.debug('\t\t\tNo left bracket filled with a verb in this clause.')
                logging.debug('\t\t\t' + tty_red + '=> NO PASSIVE' + tty_reset)

              else:
                for lk in lks:
                  (wwords,ppos,llemmas) = get_wpl(lk)
                  logging.debug('\t\t\tleft bracket: ' + ' '.join(wwords))

                  # Check for passive axuiliary.
                  if llemmas[0] == 'werden' and ppos[0].startswith('VA'):
                    logging.debug('\t\t\tFound finite form: ' + wwords[0])
                    logging.debug('\t\t\t\t' + tty_green + '=> PASSIVE' + tty_reset)
                    sent_passcounter += 1
                  else:
                    logging.debug('\t\t\tFound no finite form of \'werden\'.')
                    logging.debug('\t\t\t\t' + tty_red + '=> NO PASSIVE' + tty_reset)

      else:
        logging.debug('\t\tFound no past participle in verbal complex.')
        logging.debug('\t\t\t' + tty_red + '=> NO PASSIVE' + tty_reset)

    passcounter = passcounter + sent_passcounter
    logging.debug(tty_yellow + 'Total passive count: ' + str(sent_passcounter) + tty_reset)
    s.set('passives', str(passcounter))

  c_simpx = len(doc.findall('.//simpx'))
  c_psimpx = len(doc.findall('.//psimpx'))
  c_rsimpx = len(doc.findall('.//rsimpx'))

  add_per(doc, 'crx_pass', passcounter, c_simpx + c_psimpx + c_rsimpx, 1)


