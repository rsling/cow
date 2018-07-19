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
  global tty_magenta
  global tty_blue
  global tty_reset
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

# Returns tokens tagged as 'V.PP'.
def vvparticiples2tokens(wwords, ttttpos, llemmas, mmpos):

  # TODO Maybe add VMPP?
  part_set = set([u'VVPP']) 
  words_pos_lemmas_mmpos = zip(wwords, ttttpos, llemmas, mmpos)

  # Sometimes, Marmot gets the pos tag V.PP correct when TreeTagger thinks its V.FIN.
  # Check if the verbal complex ends with a perfect aux
  # ("Da sie alles gesehen hatten, wurden sie nicht eingeladen.")
  # Otherwise passive_corex will search for (and find) a passive aux in the left bracket
  # ("wurden") and will count two passives: "wurden ... gesehen"  and "wurden ...eingeladen".
  
  if (llemmas[-1] == "haben" or llemmas[-1] == "sein") and (ttttpos[-1].startswith('VA') or mmpos[-1].startswith('VA')) and not "werden" in llemmas:
      participletokens = []
  else:
      participletokens = [word for (word, pos, lemma, mpos) in words_pos_lemmas_mmpos if (pos in part_set or mpos in part_set)]
  return(participletokens)


def jjoin(somelist, sep, empty):
    if len(somelist) ==0:
        somelist = [empty.strip()]
    return(sep.join(somelist))


def get_dominating_simpx(element):
  while True:
    parent = element.getparent()
    if parent is not None:

      # TODO Maybe 'fkonj' also?
      if parent.tag in ['simpx', 'rsimpx', 'psimpx']:
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
#  logging.debug('\tNumber of LK found: ' + str(len(lks)))

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


# Try to find bare participles in the vorfeld ("Angemalt wurde es nicht.").
# These are typically not annotated as <vc> ...</vc> and we will thus miss them
# if we only look for participles within <vc> ... </vc>:
def vvpp_in_vf(s):
    vvpp_vf_passive_counter = 0 
    
    # retrieve all vf elements:

    vfs = s.findall('.//vf')
    logging.debug(tty_red + '\tNumber of vf in this s: ' + str(len(vfs)) +tty_reset)

    vxinf_list = []

    for vf in vfs:
        vxinf_list = vxinf_list + vf.findall('./vxinf')
    
    if len(vxinf_list) == 0:
         logging.debug('\t\t\tNo participle found in any vf.')    
   
#    for num, vf in enumerate(vfs):
    for num, vf in enumerate(vxinf_list):

        logging.debug(tty_red + '\t#' + str(num+1) + ': ' + words_to_string(vf)+ tty_reset)

    for vf in vxinf_list:
        # check if vf contains a bare participle , for each vf:
        (wwords,ppos,llemmas,mmpos,mmorph) = get_wplpm(vf)
        if len(ppos) == 1 and (ppos[0] in ["VVPP", "VMPP"] or mmpos[0] in ["VVPP", "VMPP"]):
            logging.debug(tty_red + '\t\tFound bare participle in this vf: ' + wwords[0] + tty_reset)
            # if so, retrieve the domitating simpx: 
            parent =  get_dominating_simpx(vf)
            if parent is not None:
                # retrieve all lk within the dominating simpx: 
                lks = parent.findall('.//lk')
                logging.debug(tty_red + '\t\tFound ' + str(len(lks)) + ' lk element(s).' +tty_reset)
                for n, lk in enumerate(lks):
                    logging.debug(tty_red + '\t\tlk #' + str(n+1) + ': ' + words_to_string(lk) +tty_reset)
                for lk in lks:
                    # check if lk contains a passive aux: if so keep it, increase passive counter, stop looking at remaining lk:
                    (wwords,ppos,llemmas,mmpos,mmorph) = get_wplpm(lk)
                    if len(llemmas) > 0:
                        if len(llemmas) == 1 and llemmas[0] == "werden" and (ppos[0].startswith('VA') or mmpos.startswith('VA')):
                            logging.debug(tty_red + '\t\tFound passive aux in left bracket: ' + wwords[0] + tty_reset)
                            vvpp_vf_passive_counter += 1
                            logging.debug('\t\t\t' + tty_green + '=> PASSIVE' + tty_reset)
                            # stop looking at remaining lk:
                            break
                            # if there is no passive aux in lk, or more than one item, check for modal verb(s):
                        else:
                            VM_list = [wwords[i] for i, pos in enumerate(ppos) if (ppos[i].startswith("VM") or mmpos[i].startswith("VM"))]
                            if len(VM_list) > 0:
                                logging.debug(tty_red + '\t\tFound a modal verb in the left bracket: ' + jjoin(wwords, " ", "NONE") + tty_reset)
                                logging.debug(tty_red + '\t\tLooking for a passive aux in a verbal complex.' + tty_reset)
                            # if so, retrieve all verbal complexes dominated by the same simpx:
                                vcs = parent.findall('.//vc')
                                if len(vcs) == 0:
                                    logging.debug(tty_red + '\t\tNo verbal complex found.' + tty_reset)
                                else:
                                    logging.debug(tty_red + '\t\tFound ' + str(len(vcs)) + ' lk element(s).' +tty_reset)
                                    for x, vc in enumerate(vcs):
                                        logging.debug(tty_red + '\t\tvc #' + str(x+1) + ': ' + words_to_string(vc) +tty_reset)
                                    for vc in vcs:
                                        # check if the verbal complex contains (only a) passive aux; if so, increase passive counter
                                        (wwords,ppos,llemmas,mmpos,mmorph) = get_wplpm(vc)
                                        if len(llemmas) == 1 and llemmas[0] == "werden" and (ppos[0].startswith('VA') or mmpos[0].startswith('VA')):
                                            logging.debug(tty_red + '\t\tFound passive aux in verbal complex: ' + wwords[0] + tty_reset)
                                            vvpp_vf_passive_counter += 1
                                            logging.debug('\t\t\t' + tty_green + '=> PASSIVE' + tty_reset)
                                            break
                                # stop looking at remaining vcs.
                                    break



                                        






                            

    return(vvpp_vf_passive_counter)
                                

                    

        



def passive(doc):
  doc_passcounter = 0
  successfully_analysed = []

  for s in doc.iter('s'):
    logging.debug('')
    logging.debug(tty_cyan + words_to_string(s) + tty_reset)
    sent_passcounter = 0
    sent_perfcounter = 0

    # vc is not always a direct child of simpx (e.g. in coordination).
    vcs = s.findall('.//vc')
    logging.debug('Total number of VCs: ' + str(len(vcs)))

    for num, vc in enumerate(vcs):
        logging.debug('\tVC #' + str(num+1) + ": " +  words_to_string(vc))

    for num, vc in enumerate(vcs):
      this_vc_words = words_to_string(vc)
      logging.debug(tty_magenta + 'VC #' + str(num+1) + ': '  + this_vc_words + tty_reset)
#      (wwords,ppos,llemmas) = get_wpl(vc)
      (wwords,ppos,llemmas,mmpos,mmorph) = get_wplpm(vc)

      participles = vvparticiples2tokens(wwords, ppos, llemmas, mmpos)

      logging.debug('\tAll tokens:\t' + jjoin(wwords, ", ", "NONE"))
      logging.debug('\tAll tags:\t' + jjoin(ppos, ", ", "NONE"))
      logging.debug('\tAll lemmas:\t' + jjoin(llemmas, ", ", "NONE"))
      logging.debug('\tAll VV part.:\t' + jjoin(participles, ", ", "NONE"))


      # Most general case: verbal complex contains a participle (could be perfekt or passive).
#      participles = [word for word in ppos if word == 'VVPP']

#      logging.debug('\tParticiples: ' + ', '.join(participles))
      if len(participles) > 0:
        donelist = []
        has_passive = False
        logging.debug('\tTotal participles in this VC: ' + str(len(participles)))

        for n, participle in enumerate(participles):
          logging.debug('\t' + tty_blue + 'Searching for perfect aux in the verbal complex (participle #' + str(n+1) + ": " + participle + ")" + tty_reset)

          if u'werden' in llemmas:
            for i in range(0,len(llemmas)):

              # Experimental: 'sein' must not occur before werden
              # ('dass der Schaden auch bei rechtzeitiger Leistung eingetreten sein würde').
              if llemmas[i] == u'werden' and ppos[i].startswith('VA') and llemmas[i-1] != u'sein':
                has_passive = True
                sent_passcounter += 1
                logging.debug('\t\tPassive aux found in verbal complex.')
                logging.debug('\t\t\t' + tty_green + '=> PASSIVE' + tty_reset)
                successfully_analysed.append(" ".join([participle, wwords[i]]))
                donelist.append(participle)
                print(successfully_analysed)
                break

 
        # Get the left bracket of the immediately dominating <simplex>-element.
        if has_passive == False:
           logging.debug('\t\tNo passive aux found in verbal complex.')
           if llemmas[-1] == "sein":
               logging.debug("\t\tVerbal complex ends with lemma 'sein'.")
               logging.debug('\t\t\t' + tty_red + '=> NO PASSIVE' + tty_reset)

           else: # avoid treating "er wird bemüht sein" as passive
            participles = [participle for participle in participles if not participle in donelist]

            if len(participles) > 0:
                logging.debug('\t\tRemaining participles in this VC: ' + str(len(participles)))
                logging.debug('\t' + tty_blue + 'Trying to find a passive aux in the left bracket.' + tty_reset)
      
            for participle in participles:
             vcparent = get_dominating_simpx(vc)
             logging.debug('\t\tParticiple:\t' + participle)
             logging.debug('\t\tLocating left bracket...')

             if vcparent is not None:
              lks = get_dominating_lk2(vcparent)
              if lks == []:
                logging.debug('\t\t\tNo left bracket filled with a verb in this clause.')
                logging.debug('\t\t\t' + tty_red + '=> NO PASSIVE' + tty_reset)

              else:
                for lk in lks:
#                  (wwords,ppos,llemmas) = get_wpl(lk)
                  (wwords,ppos,llemmas,mmpos,mmorph) = get_wplpm(lk)
                  logging.debug('\t\tLeft bracket: ' + ' '.join(wwords))


                  # Check for passive axuiliary.
                  if llemmas[0] == 'werden' and (ppos[0].startswith('VA') or mmpos.startswith('VA')):
                    logging.debug('\t\t\tFound passive aux in left bracket: ' + wwords[0])
                    logging.debug('\t\t\t\t' + tty_green + '=> PASSIVE' + tty_reset)
                    sent_passcounter += 1
                    successfully_analysed.append(" ".join([wwords[0], participle]))
                  else:
                    logging.debug('\t\t\tFound no passive aux in left bracket.')
                    logging.debug('\t\t\t\t' + tty_red + '=> NO PASSIVE' + tty_reset)

      else:
        logging.debug('\t\tFound no past participle in verbal complex.')
        logging.debug('\t\t\t' + tty_red + '=> NO PASSIVE' + tty_reset)

    
    sent_passcounter += vvpp_in_vf(s)

    doc_passcounter = doc_passcounter + sent_passcounter
    logging.debug(tty_yellow + 'Total passive count: ' + str(sent_passcounter) + tty_reset)
    s.set('passives', str(sent_passcounter))

  # Unit of reference is 1 simpx (including subtypes of simpx).
  c_simpx = len(doc.findall('.//simpx'))
  c_psimpx = len(doc.findall('.//psimpx'))
  c_rsimpx = len(doc.findall('.//rsimpx'))
  add_per(doc, 'crx_pass', doc_passcounter, c_simpx + c_psimpx + c_rsimpx, 1)



