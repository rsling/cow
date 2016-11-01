# -*- coding: utf-8 -*-

# Getting elemenatry features from COW-DOMs

import os.path
import sys
import glob
from lxml import etree as ET


def per(x, n, p = 1000):
    if n > 0:
        return x/float(n)*p
    else:
        return -1


def add_per(doc, attr, x, n, p = 1000):
    doc.attrib[attr] = str(per(x,n,p))


def parsemorphs(text):
	morphlist = []
	if len(text) > 1:
		morphlist = text.strip('|').split('|')
	return(morphlist)
	

def annotate_basic(dom):

    # Get word count.
    words = dom.findall('.//*word')
    c_word = len(words)
    dom.attrib['crx_tokc'] = str(c_word)

    # Get type/token ratio – based on lowercased tokens!
    tokens = [t.text.lower() for t in words]
    types = set(tokens)
    if len(tokens) > 0:
        r_type_token = len(types)/float(len(tokens))
    else:
        r_type_token = -1
    dom.attrib['crx_ttrat'] = str(r_type_token)

    # Get avg word length.
    if c_word > 0:
        avg_word_length = sum([len(w.text) for w in words])/float(c_word)
    else:
        avg_word_length = 0
    dom.attrib['crx_wlen'] = str(avg_word_length)

    # Get sentence count.
    sentences = dom.findall('.//s')
    c_sentences = len(sentences)
    dom.attrib['crx_sentc'] = str(c_sentences)

    # Get avg sentence length.
    if c_sentences > 0:
        avg_sentence_length = str(sum([len(s.findall('.//*token')) for s in sentences])/float(c_sentences))
    else:
        avg_sentence_length = 0
    dom.attrib['crx_slen'] = str(avg_sentence_length)

    # Get clauses:
    c_simpx = len(dom.findall('.//simpx'))
    dom.attrib['crx_simpxc'] = str(c_simpx)

    # Get coordinated clauses:
    c_psimpx = len(dom.findall('.//psimpx'))
    dom.attrib['crx_psimpxc'] = str(c_psimpx)

    # Get relative clauses:
    c_rsimpx = len(dom.findall('.//rsimpx'))
    dom.attrib['crx_rsimpxc'] = str(c_rsimpx)

    # Get verb-second sentences:
    c_vf = len(dom.findall('.//vf'))
    dom.attrib['crx_vfc'] = str(c_vf)

    # Get verb-last sentences:
    c_c = len(dom.findall('.//c'))
    dom.attrib['crx_cc'] = str(c_c)

    # Get POS counts (modal verbs etc.).
    posse = dom.findall('.//*ttpos')

    c_modals = len([p for p in posse if p.text[:2] == 'VM'])
    add_per(dom, 'crx_mod', c_modals, c_word, 1000)

    c_commonnouns = len([p for p in posse if p.text == 'NN'])
    add_per(dom, 'crx_cn', c_commonnouns, c_word, 1000)
    
    c_prepositions = len([p for p in posse if p.text[:2] == 'AP'])
    add_per(dom, 'crx_prep', c_prepositions, c_word, 1000)
    
    c_infinitives = len([p for p in posse if p.text in ['VAINF', 'VMINF', 'VVINF']])
    add_per(dom, 'crx_inf', c_infinitives, c_word, 1000)

    c_imperatives = len([p for p in posse if p.text in ['VAIMP', 'VMIMP', 'VVIMP']])
    add_per(dom, 'crx_imp', c_imperatives, c_word, 1000)

    c_adverbs = len([p for p in posse if p.text == 'ADV'])
    add_per(dom, 'crx_adv', c_adverbs, c_word, 1000)
    
    c_adjectives = len([p for p in posse if p.text[:3] == 'ADJ'])
    add_per(dom, 'crx_adj', c_adjectives, c_word, 1000)
 
    c_subjunctions_w_sentence = len([p for p in posse if p.text == 'KOUS'])
    add_per(dom, 'crx_subjs', c_subjunctions_w_sentence, c_word, 1000)

    c_subjunctions_w_infinitive = len([p for p in posse if p.text == 'KOUI'])
    add_per(dom, 'crx_subji', c_subjunctions_w_infinitive, c_word, 1000)

    c_conjunctions = len([p for p in posse if p.text == 'KON'])
    add_per(dom, 'crx_conj', c_conjunctions, c_word, 1000)

    
    # We need parents -> lemmas for article counting.
    posse_lemmas = [p.find('../lemma').text for p in posse if p.text == 'ART']
    
    c_def_article = len([a for a in posse_lemmas if a == 'd'])
    add_per(dom, 'crx_def', c_def_article, c_word, 1000)
    
    c_indef_article = len([a for a in posse_lemmas if a == 'ein'])
    add_per(dom, 'crx_indef', c_indef_article, c_word, 1000)
   
    # NER-related counts.
    nerds = dom.findall('.//*ne')
    
    c_ne_per = len([n for n in nerds if n.text == 'I-PER'])
    add_per(dom, 'crx_per', c_ne_per, c_word, 1000)
    
    c_ne_loc = len([n for n in nerds if n.text == 'I-LOC'])
    add_per(dom, 'crx_loc', c_ne_loc, c_word, 1000)
    
    c_ne_org = len([n for n in nerds if n.text == 'I-ORG'])
    add_per(dom, 'crx_org', c_ne_org, c_word, 1000)

    # Get all lemmas:
    lemmas = dom.findall('.//*lemma')

    # Emoticons:
    c_emo = len([l for l in lemmas if l.text == '(smiley)'])
    add_per(dom, 'crx_emo', c_emo, c_word, 1000)

    # Cliticized indefinite articles:
    c_clit_indef_article = len([a for a in posse_lemmas if a == 'n'])
    add_per(dom, 'crx_clitindef', c_clit_indef_article, (c_indef_article + c_clit_indef_article), 1)

 
    # Get past tense verbs:
    morphs = dom.findall('.//morph')
    morphtexts = [morph.text for morph in morphs]
    morphsets = [m.strip('|').split('|') for m in morphtexts if len(m) > 1]
   
    # Get past tense verbs:
    c_vpast = len([m for m in morphsets if 'past' in m])
    dom.attrib['crx_vpast'] = str(c_vpast)

    # Get present tense verbs:
    c_vpres = len([m for m in morphsets if 'pres' in m])
    dom.attrib['crx_vpres'] = str(c_vpres)

    # Get present tense, subjunctive mood verbs
    c_vsubj = len([m for m in morphsets if 'pres' in m and 'subj' in m])
    dom.attrib['crx_vsubj'] = str(c_vsubj)

    # Get Marmot's POS:
    mposse = dom.findall('.//*mpos')
    mposse_morphs = [parsemorphs(p.find('../morph').text) for p in mposse if p.text == 'PPER']

    # Get 1st person personal pronouns:
    c_pper_1st = len([m for m in mposse_morphs if '1' in m])
    add_per(dom, 'crx_pper_1st', c_pper_1st, c_word, 1000)


       

    







	

 
     
     

