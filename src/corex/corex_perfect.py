# -*- coding: utf-8 -*-

from corex_reader import CORexReader as CX, outify
from corex_basic import per, add_per, FloatHandler
import re
import logging
import lxml.etree


sein_part_re = re.compile('.*ge(gangen|fallen|laufen|flogen|wachsen|fahren|reist|schritten|geblieben|sprungen|kommen|blieben|drungen|wichen|stiegen|worden|stehen|taucht|storben|rutscht|rannt)')

sein_part_set = set([u'geboren', u'gelungen', u'verhungert', u'zusammengebrochen', u'verklungen', u'passiert', u'weggezogen', u'fehlgeschlagen', u'geschehen', u'verreist', u'geflohen', u'gestoßen', u'gestossen', u'gewandert', u'begegnet', u'verschmolzen', u'abgekühlt', u'versunken', u'eingeschlafen', u'gestrandet', u'abgebogen', u'misslungen', u'explodiert', u'gekrochen', u'ausgetrocknet', u'ausgetreten', u'worden', u'zerfallen', u'abgehauen', u'gestürzt', u'abgewandert', u'geplatzt', u'ertrunken', u'erschienen', u'erwachsen', u'verschwunden', u'widerfahren', u'zerbrochen', u'eingetreten', u'gestartet', u'verstrichen', u'entkommen', u'zugestoßen', u'zugestossen', u'verblieben', u'gelandet', u'gefolgt', u'abgestürzt', u'aufgesessen', u'geschlüpft', u'entwachsen', u'abgebrannt', u'geraten', u'umgezogen', u'eingeschlagen', u'bekommen', u'geklettert', u'gereift', u'dagewesen', u'gewesen', u'auferstanden', u'zurückgetreten', u'gekippt', u'vergangen', u'eingebrochen', u'geschwommen', u'gelangt', u'erschrocken', u'eingestürzt', u'geschmolzen', u'verflogen', u'hervorgetreten', u'mutiert', u'verheilt', u'unterlaufen', u'ergangen', u'beigetreten', u'ausgezogen', u'ausgewandert', u'erwacht', u'aufgestanden', u'eingewandert', u'erfolgt', u'gescheitert', u'aufgewacht', u'geflüchtet', u'entsprungen', u'überlaufen', u'zugezogen', u'angetreten', u'gestolpert', u'eingeflossen', u'entstanden', u'geglückt', u'gestanden', u'abgeklungen', u'angeschwollen', u'entgangen', u'geschrumpft', u'gesunken', u'zerrissen', u'verfallen', u'aufgetreten', u'ausgebrochen', u'verkommen', u'verstorben', u'abgezogen', u'erloschen', u'ausgeschieden', u'durchgebrannt', u'verunglückt', u'abgesunken'])


oberfeld_re = re.compile('VAFIN(?: V.INF)+')


ersatzinfinitives_set = set([u'sehen', u'hören', u'fühlen', u'lassen', u'wollen', u'müssen', u'dürfen', u'sollen', u'können', u'mögen', u'spüren'])


tty_green = ''
tty_red   = ''
tty_cyan  = ''
tty_yellow  = ''
tty_blue    = ''
tty_magenta = ''
tty_reset = ''


def perfect_enable_color():
    global tty_green
    global tty_red
    global tty_cyan
    global tty_yellow
    global tty_magenta
    global tty_reset
    global tty_blue
    tty_green   = '\033[1;32m'
    tty_red     = '\033[1;31m'
    tty_cyan    = '\033[1;36m'
    tty_yellow  = '\033[1;33m'
    tty_magenta = '\033[1;35m'
    tty_blue    = '\033[1;34m'
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
            elif parent.tag == 's':
                break
            else:
                element = parent
        else:
            parent = None
            break
    return(parent)


def get_dominating_Y(element, dominating_cat):
    # return dominating element of category <dominating_cat>;
    # return None if there is no such element within s.
    while True:
        parent = element.getparent()
        if parent is not None:
            if parent.tag == dominating_cat:
                break
            elif parent.tag == 's':
                parent = None
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
            lks = parent.findall('./lk')

            tags = [i.tag for i in lks]

            # Stop searching after the first LK has been found:
            if len(lks) > 0:
                logging.debug("\t\tFound left bracket (lk) in this clause: '" + words_to_string(parent) + "'")
                break
            else:
            # stop searching at the clause boundary:
                if parent.tag.endswith('simpx'):
                    break
                else:
                    current = parent
        else:
            break
    return(lks)


# Check for a non-verb-final structure (left bracket in verb-final clauses is 'c', not 'lk').
def get_neighbouring_vce(vc):
    current = vc
    vces = []

    parent = get_dominating_X(current)

    if parent is not None:
        vces = parent.findall('./vce')
    return(vces)



def firstlemma(lemmastring):
    lemmastring = lemmastring.strip('|')
    lemmalist = lemmastring.split('|')
    return(lemmalist[0])


def get_wplpm(enclosing_element):
    words = enclosing_element.findall('.//*word')
    ttpos = enclosing_element.findall('.//*ttpos')
    lemmas = enclosing_element.findall('.//*lemma')
    mpos = enclosing_element.findall('.//*mpos')
    morph = enclosing_element.findall('.//*morph')

    wwords = [w.text for w in words]
    ttttpos = [p.text for p in ttpos]
    lemmasetstrings = [l.text for l in lemmas]
    llemmas = [firstlemma(l) for l in lemmasetstrings]
    mmpos = [p.text for p in mpos]
    mmorph = [m.text for m in morph]

    return(wwords,ttttpos,llemmas,mmpos,mmorph)


def oberfeld(s):
    # Check for Oberfeldumstellung with Ersatzinfinitiv
    # (no point in using topo-parse information here,
    # it's almost always incorrect).

    # Overload input type:

    if type(s) == lxml.etree._Element:
        (wwords,ttttpos,llemmas,mmpos,mmorph) = get_wplpm(s)
    elif type(s) == tuple:
        if len(s) == 5:
            (wwords,ttttpos,llemmas,mmpos,mmorph) = s
        else:
            sys.exit('oberfeld(): incorrect length of input tuple: ' + str(len(s)) + ' (required: 5)\n')
    else:
        sys.exit('oberfeld(): incompatible input type: ' + str(type(s))+ '\n')

    items = []
    posse = " ".join(ttttpos)
    m = re.search('V[AMV](?:INF|FIN)(?: V[AMV](?:INF|FIN)){2,}', posse)

    if m:
        words_and_tags_and_lemmas = zip(wwords,ttttpos,llemmas)

        seq = m.group(0).split(" ")
        for p in range(len(ttttpos) - len(seq) + 1):
            if ttttpos[p:p+len(seq)] == seq: 
                items = words_and_tags_and_lemmas[p:p+len(seq)]
    return(items)



def has_oberfeldumstellung(s):
    # Check for Oberfeldumstellung with Ersatzinfinitiv
    # (no point in using topo-parse information here, it's almost always incorrect).

    # Overload input type:

    if type(s) == lxml.etree._Element:
        (wwords,ttttpos,llemmas,mmpos,mmorph) = get_wplpm(s)
    elif type(s) == tuple:
        if len(s) == 5:
            (wwords,ttttpos,llemmas,mmpos,mmorph) = s
        else:
            sys.exit('oberfeld(): incorrect length of input tuple: ' + str(len(s)) + ' (required: 5)\n')
    else:
        sys.exit('oberfeld(): incompatible input type: ' + str(type(s))+ '\n')

    posse = " ".join(ttttpos)
    m = re.search('V[AMV](?:INF|FIN)(?: V[AMV](?:INF|FIN)){2,}', posse)

    if m:
        return True
    else:
        return False


def oberfeld2(s, successfully_processed, sent_perfcounter, sent_pluperfcounter):
    # Check for Oberfeldumstellung with Ersatzinfinitiv
    # (no point in using topo-parse information here, it's almost always incorrect).

    # Overload input type:

    if type(s) == lxml.etree._Element:
        (wwords,ttttpos,llemmas,mmpos,mmorph) = get_wplpm(s)
    elif type(s) == tuple:
        if len(s) == 5:
            (wwords,ttttpos,llemmas,mmpos,mmorph) = s
        else:
            sys.exit('oberfeld(): incorrect length of input tuple: ' + str(len(s)) + ' (required: 5)\n')
    else:
        sys.exit('oberfeld(): incompatible input type: ' + str(type(s))+ '\n')

    items = []
    posse = " ".join(ttttpos)
    logging.debug("\tPOS-Sequence: " + posse)

    # Also allow for a "VVPP" in the sequence ("hätten umgestellt werden müssen"):
    m = re.search('V[AMV](?:INF|FIN)(?: VVPP)?(?: V[AMV](?:INF|FIN)){2,}', posse)
    

    if m:
        logging.debug("\t\t" + posse[0:m.start()] + tty_magenta + posse[m.start():m.end()] + tty_reset + posse[m.end():])
        words_and_tags_and_lemmas = zip(wwords,ttttpos,llemmas)

        # Find sequence of (word, pos, lemma) triples that correspond 
        # to the matched part of posse:
        seq = m.group(0).split(" ")
        for p in range(len(ttttpos) - len(seq) + 1):
            if ttttpos[p:p+len(seq)] == seq: 
                items = words_and_tags_and_lemmas[p:p+len(seq)]

    if len(items) > 0:

        oberfeld_words = " ".join([e[0] for e in items])
        logging.debug("\t\tVC candidate: '" + oberfeld_words.encode('utf-8') + "'")
        logging.debug("\t\tSuccessfully processed before: " + jjoin(successfully_processed, ", ", "NONE").encode('utf-8'))

        if oberfeld_words in set(successfully_processed):
            logging.debug("""\t\tIgnoring sequence '""" +  oberfeld_words.encode('utf-8') + """': was successfully processed before.""")
        else:
            if items[-1][2] in ersatzinfinitives_set:
              finiteverb = [i for i in items if (i[1].endswith('FIN') and i[2] in ['haben', 'sein'])]
              if len(finiteverb) > 0:
                  if haben_pres(finiteverb[0][0]):
                      logging.debug("\t\t[I] Oberfeldumstellung + finite perfect aux (pres) found in verbal complex: '" + finiteverb[0][0] + "'")
                      logging.debug('\t\t\t' + tty_green + '=> PERFECT' + tty_reset)
                      sent_perfcounter += 1
                      successfully_processed.append(oberfeld_words)
                  elif haben_past(finiteverb[0][0]):
                      logging.debug("\t\t[J] Oberfeldumstellung + finite perfect aux (past) found in verbal complex: '" + finiteverb[0][0] +"'")
                      logging.debug('\t\t\t' + tty_green + '=> PLUPERFECT' + tty_reset)
                      sent_pluperfcounter += 1
                      successfully_processed.append(oberfeld_words)
                  
    else:
        logging.debug('\t\tNo suitable sequence of POS tags found.')

    return (sent_perfcounter, sent_pluperfcounter, successfully_processed)


# Try to find bare participles in the vorfeld ("Angemalt wurde es nicht.").
# These are typically not annotated as <vc> ...</vc> and we will thus miss them
# if we only look for participles with <vc> ... </vc>:

def vvpp_in_vf(s, sent_perfcounter, sent_pluperfcounter):
    vvpp_vf_perfect_counter = sent_perfcounter
    vvpp_vf_pluperfect_counter =  sent_pluperfcounter
    donelist = []

    # Retrieve all vf elements.

    vfs = s.findall('.//vf')
    logging.debug('\tNumber of vf in this s: ' + str(len(vfs)))

    for num, vf in enumerate(vfs):
      vxinf_list = []
      logging.debug('\tvf #' + str(num+1) + ': ' + words_to_string(vf))

      # Check if vf contains a finite verb.
      vxfin = vf.findall('.//vxfin')
      if len(vxfin) > 0:
          logging.debug('\t\tIgnoring this vf (contains finite verb: ' + words_to_string(vxfin[0]) + ')')
      else:
          vxinf_list = vxinf_list + vf.findall('./vxinf')
          simpx_list = vf.findall('./simpx')
          for simpx in simpx_list:
              vc_list =  simpx.findall('./vc')
              for vc in vc_list:
                  vxinf_list = vxinf_list + vc.findall('./vxinf')

      if len(vxinf_list) == 0:
         logging.debug('\t\t\tNo suitable participle found in this vf.')

      for vxinf in vxinf_list:

        # Check if vf contains a bare participle , for each vf.
        (wwords,ppos,llemmas,mmpos,mmorph) = get_wplpm(vxinf)
        participletags = ["VVPP", "VMPP", "VAPP"]
        V_PP_list = [wwords[i] for i, pos in enumerate(ppos) if (ppos[i] in participletags or mmpos[i] in participletags)]

        for participle in V_PP_list:
          logging.debug('\t\tFound suitable participle(s) in this vf: ' + participle)

          # If so, retrieve the simpx that dominates vf.
          parent =  get_dominating_X(vf)
          if parent is not None:

                # Retrieve all lk within the dominating simpx. 
                lks = parent.findall('.//lk')
                logging.debug('\t\tFound ' + str(len(lks)) + ' lk element(s).')
                for n, lk in enumerate(lks):
                    logging.debug('\t\tlk #' + str(n+1) + ': ' + words_to_string(lk))
                for lk in lks:

                    # Check if lk contains a perfect aux: increase perfect counters, stop looking at remaining lk.
                    (lkwwords,lkppos,lkllemmas,lkmmpos,lkmmorph) = get_wplpm(lk)
                    if len(lkllemmas) > 0:
                        candidate = lkwwords[0]
                        logging.debug('\t\tFound perfect aux in left bracket: ' + candidate + tty_reset)
                        (add_to_perfcounter, add_to_pluperfcounter, add_to_donelist)  = get_tense(lkwwords[0], lkllemmas[0], participle)
                        vvpp_vf_perfect_counter += add_to_perfcounter
                        vvpp_vf_pluperfect_counter += add_to_pluperfcounter
                        donelist = donelist + add_to_donelist

                        # Stop looking at remaining lks if we have found a perefect aux.
                        if add_to_perfcounter + add_to_pluperfcounter > 0:
                            break

                        # If there is no perfect aux in lk, check for modal verb(s).
                        else:
                            VM_list = [lkwwords[i] for i, pos in enumerate(lkppos) if (lkppos[i].startswith("VM") or lkmmpos[i].startswith("VM"))]
                            if len(VM_list) > 0:
                                logging.debug('\t\tFound a modal verb in the left bracket: ' + jjoin(wwords, " ", "NONE"))
                                logging.debug('\t\tLooking for a perfect aux in a verbal complex.')

                                # If so, retrieve all verbal complexes dominated by the same simpx.
                                vcs = parent.findall('.//vc')
                                if len(vcs) == 0:
                                    logging.debug('\t\tNo verbal complex found.' + tty_reset)
                                else:
                                    logging.debug('\t\tFound ' + str(len(vcs)) + ' lk element(s).')
                                    for x, vc in enumerate(vcs):
                                        logging.debug('\t\tvc #' + str(x+1) + ': ' + words_to_string(vc))
                                    for vc in vcs:

                                        # Check if the verbal complex contains (only a) perfect aux; if so check form and increase counters.
                                        (vcwwords,vcppos,vcllemmas,vcmmpos,vcmmorph) = get_wplpm(vc)
                                        if len(vcllemmas) == 1:
                                            (add_to_perfcounter, add_to_pluperfcounter, add_to_donelist)  = get_tense(vcwwords[0], vcllemmas[0], participle)
                                            vvpp_vf_perfect_counter += add_to_perfcounter
                                            vvpp_vf_pluperfect_counter += add_to_pluperfcounter
                                            donelist = donelist + add_to_donelist
                                            if add_to_perfcounter + add_to_pluperfcounter > 0:
                                                break

                                    # Stop looking at remaining vcs.
                                    break
    return(vvpp_vf_perfect_counter, vvpp_vf_pluperfect_counter)


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
  if candidate.lower() in [u'bin', u'bist', u'ist', u'sind', u'seid', u'sind', u'sei', u'seist', u'seiest', u'seien', u'seiet',u'sein']: #add infinitive
    return(True)
  else:
    return(False)

def sein_past(candidate):
  if candidate.lower() in  [u'war', u'warst', u'waren', u'wart', u'wäre', u'wärst', u'wär', u'wären', u'wärt', u'wäret']:
    return(True)
  else:
    return(False)

def jjoin(somelist, sep, empty):
    if len(somelist) ==0:
        somelist = [empty.strip()]
    return(sep.join(somelist))



def get_tense(candidate, auxlemma, participle): #, successfully_processed):
    perfcounter = 0
    pluperfcounter = 0 
    donelist = []

    if auxlemma == u'haben':

        # Check tense.
        # Don't rely on Marmot morph annotations:
        # there will be no annotation if Marmot thinks it is 'VAINF'.
        if haben_pres(candidate):
            perfcounter += 1
            donelist.append(participle)
            logging.debug('\t\tFinite perfect aux (pres) found: ' + candidate)
            logging.debug('\t\t\t' + tty_green + '=> PERFECT' + tty_reset)

        elif haben_past(candidate):
            pluperfcounter += 1 
            donelist.append(participle)
            logging.debug('\t\tFinite perfect aux (past) found: ' + candidate)
            logging.debug('\t\t\t' + tty_green + '=> PLUPERFECT' + tty_reset)

    elif auxlemma == u'sein':

        # Check if participle is among those that take 'sein' as perfect tense auxiliary.
        if participle in sein_part_set or  sein_part_re.match(participle):
            if sein_pres(candidate):
                perfcounter += 1 
                donelist.append(participle)
                logging.debug('\t\tFinite perfect aux (pres) found: ' + candidate)
                logging.debug('\t\t\t' + tty_green + '=> PERFECT' + tty_reset)
            elif sein_past(candidate):
                pluperfcounter += 1 
                donelist.append(participle)
                logging.debug('\t\tFinite perfect aux (past) found: ' + candidate)
                logging.debug('\t\t\t' + tty_green + '=> PLUPERFECT' + tty_reset)
    else:
        logging.debug('\t\t\t' + "Not a suitable perfect aux for participle '" + participle + "': " + candidate)

    return (perfcounter, pluperfcounter, donelist) #, successfully_processed)


# Returns tokens tagged as 'V.PP'.
def participles2tokens(wwords, ttttpos, llemmas, mmpos):

    # TODO Maybe add VMPP?
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


def perfect(doc, fh):
  doc_perfcounter = 0
  doc_pluperfcounter = 0

  for s in doc.iter('s'):
    logging.debug('')
    logging.debug(tty_cyan + words_to_string(s) + tty_reset)
    sent_perfcounter = 0
    sent_pluperfcounter = 0
    successfully_processed = []
    vce = False

    # vc is not always a direct child of simpx (e.g. in coordination).
    vcs = s.findall('.//vc')
    logging.debug('Total number of VCs: ' + str(len(vcs)))

    for num, vc in enumerate(vcs):
        logging.debug('\tVC #' + str(num+1) + ": " +  words_to_string(vc))
    
   
    for num, vc in enumerate(vcs):
      this_vc_words = words_to_string(vc)
      logging.debug(tty_magenta + 'VC #' + str(num+1) + ': '  + this_vc_words + tty_reset)
      (wwords,ttttpos,llemmas,mmpos,mmorph) = get_wplpm(vc)

      # Basic case: verbal complex contains a participle.
      participles = participles2tokens(wwords, ttttpos, llemmas, mmpos)
      infinitives = infinitives2tokens(wwords, ttttpos)
      ersatzcandidates = ersatzinfinitives_candidates(wwords, ttttpos, llemmas)
      participles_and_ersatzinfs = participles + ersatzcandidates

      # when not dealing with coordinated participles,
      # use only the last participle/ersatzinfinitiv in verbal complex
      # (i.e., do not count both 'geschenkt and 'bekommen' as participles in 
      # "soll es geschenkt bekommen haben")
      
      if not u'und' in llemmas and not u'oder' in llemmas and not 'aber' in llemmas:
          participles_and_ersatzinfs = participles_and_ersatzinfs[-1:]


      logging.debug('\tAll tokens:\t' + jjoin(wwords, ", ", "NONE"))
      logging.debug('\tAll tags:\t' + jjoin(ttttpos, ", ", "NONE"))
      logging.debug('\tAll lemmas:\t' + jjoin(llemmas, ", ", "NONE"))
      logging.debug('\tAll part.:\t' + jjoin(participles, ", ", "NONE"))
      logging.debug('\tAll inf.:\t' + jjoin(infinitives, ", ", "NONE"))
      logging.debug('\tAll poss. ersatzinf.:\t' + jjoin(ersatzcandidates, ", ", "NONE"))
      logging.debug('\tPart. + ers.Inf.:\t' + jjoin(participles_and_ersatzinfs, ", ", "NONE"))



      if len(participles_and_ersatzinfs) == 0:
          logging.debug('\t\tNo past participle or infinitive found in verbal complex.')

      else:

        logging.debug('\tTotal participles in this VC: ' + str(len(participles_and_ersatzinfs)))
        donelist = []

        for n, participle in enumerate(participles_and_ersatzinfs):

          logging.debug('\t' + tty_blue + 'Searching for perfect aux in the verbal complex (participle #' + str(n+1) + ": " + participle + ")" + tty_reset)
           # Check if verbal complex ends with a potential perfect aux:
           # also include non-finite aux ("Er soll es gelesen haben." "Er wird gekommen sein.")
          #if  ttttpos[-1] == 'VAFIN':
          if ttttpos[-1].startswith('VA'): # ttttpos[-1] == 'VAFIN':
            candidate = wwords[-1]
            logging.debug('\t\tLast word in VC: ' + candidate)
            (add_to_perfcounter, add_to_pluperfcounter, add_to_donelist)  = get_tense(candidate, llemmas[-1], participle)
            sent_perfcounter += add_to_perfcounter
            sent_pluperfcounter += add_to_pluperfcounter
            donelist = donelist + add_to_donelist

          else:
            logging.debug('\t\tVerbal complex does not end with a perfect aux.')

        # Make sure we do not process a participle twice:
        participles_and_ersatzinfs = [participle for participle in participles_and_ersatzinfs if not participle in donelist]


        if len(participles_and_ersatzinfs) > 0:
            logging.debug('\t\tRemaining participles this VC: ' + jjoin(participles_and_ersatzinfs, ",", "NONE"))
            logging.debug('\t' + tty_blue + 'Trying to find a perfect aux in the left bracket.' + tty_reset)
      

#        for participle in  participles_and_ersatzinfs[-1:]:
        for participle in  participles_and_ersatzinfs:


         logging.debug('\t\tParticiple:\t' + participle)
         logging.debug('\t\tLocating left bracket...')
         found_aux = False
         lks = get_dominating_lk(vc)
         element = "left bracket: "

         if lks == []:
          logging.debug('\t\tFound no left bracket.')

          vces = get_neighbouring_vce(vc)
          if vces == []:
           logging.debug('\t\tFound no vce.')
          else:
           logging.debug('\t\tFound vce.')
           element = "vce: " 
           lks = vces
           vce = True

         for lk in lks:
              (lkwwords,lkttttpos,lkllemmas,lkmmpos,lkmmorph) = get_wplpm(lk)
              logging.debug('\t\t' + element + ' '.join(lkwwords))

              # Check if the first word is a finite auxiliary verb.
              if not lkttttpos[0] == u'VAFIN':
                  logging.debug('\t\t\t\tNo finite perfect aux in left bracket.')
              else:
                  candidate =  lkwwords[0]
                  logging.debug("\t\tFound a potential perfect aux: '" + candidate + "'")
                
                  # Check if aux is appropriate for participle; if so: get tense and stop searching through remaining lks.
                  (add_to_perfcounter, add_to_pluperfcounter, add_to_donelist)  = get_tense(candidate, lkllemmas[0], participle)
                  sent_perfcounter += add_to_perfcounter
                  sent_pluperfcounter += add_to_pluperfcounter
                  donelist = donelist + add_to_donelist
                  if add_to_perfcounter + add_to_pluperfcounter > 0:
                      successfully_processed.append(jjoin([candidate] + wwords, " ", "NONE"))
                      logging.debug("\t\tStop searching for more LKs/vces.")
                      found_aux = True
                      break
         if not found_aux:
             logging.debug('\t\t\t\tNo finite perfect aux in any left left bracket.')

     
    # OBERFELDUMSTELLUNG:
    if vce:
        logging.debug(tty_blue + 'NOT checking for Oberfeldumstellung with REGEX because there was a vce-element.' + tty_reset)
    else:
        logging.debug(tty_blue + 'Checking for Oberfeldumstellung (entire sentence, ignoring vc-tags)' + tty_reset)
        (sent_perfcounter, sent_pluperfcounter, successfully_processed) = oberfeld2(s, successfully_processed, sent_perfcounter, sent_pluperfcounter)

    # BARE PARTICIPLES IN VF:
    logging.debug(tty_blue + 'Checking for participles in vf' + tty_reset)
    (sent_perfcounter, sent_pluperfcounter) = vvpp_in_vf(s, sent_perfcounter, sent_pluperfcounter)

    logging.debug(tty_yellow + 'Total perfect in this sentence:' + str(sent_perfcounter) + tty_reset)
    logging.debug(tty_yellow + 'Total pluperfect in this sentence:' + str(sent_pluperfcounter) + tty_reset)

    s.set('perfects', str(sent_perfcounter))
    s.set('pluperfects', str(sent_pluperfcounter))

    doc_perfcounter = doc_perfcounter + sent_perfcounter
    doc_pluperfcounter = doc_pluperfcounter + sent_pluperfcounter

  # Unit of reference is 1 simpx (including subtypes of simpx).
  c_simpx = len(doc.findall('.//simpx'))
  c_psimpx = len(doc.findall('.//psimpx'))
  c_rsimpx = len(doc.findall('.//rsimpx'))
  add_per(doc, 'crx_perf', doc_perfcounter, c_simpx + c_psimpx + c_rsimpx, fh, 1)
  add_per(doc, 'crx_plu', doc_pluperfcounter, c_simpx + c_psimpx + c_rsimpx, fh, 1)


