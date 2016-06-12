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
    sentences = dom.findall('.//*s')
    c_sentences = len(sentences)
    dom.attrib['crx_sentc'] = str(c_sentences)

    # Get avg sentence length.
    if c_sentences > 0:
        avg_sentence_length = str(sum([len(s.findall('.//*token')) for s in sentences])/float(c_sentences))
    else:
        avg_sentence_length = 0
    dom.attrib['crx_slen'] = str(avg_sentence_length)

    # Get POS counts (modal verbs etc.).
    posse = dom.findall('.//*pos')

    c_modals = len([p for p in posse if p.text[:2] == 'VM'])
    add_per(dom, 'crx_mod', c_modals, c_word, 1000)

    c_commonnouns = len([p for p in posse if p.text == 'NN'])
    add_per(dom, 'crx_cn', c_commonnouns, c_word, 1000)
    
    c_prepositions = len([p for p in posse if p.text[:2] == 'AP'])
    add_per(dom, 'crx_prep', c_prepositions, c_word, 1000)
    
    c_infinitives = len([p for p in posse if p.text in ['VAINF', 'VMINF', 'VVINF']])
    add_per(dom, 'crx_inf', c_infinitives, c_word, 1000)
    
    c_adverbs = len([p for p in posse if p.text == 'ADV'])
    add_per(dom, 'crx_adv', c_adverbs, c_word, 1000)
    
    c_adjectives = len([p for p in posse if p.text[:3] == 'ADJ'])
    add_per(dom, 'crx_adj', c_adjectives, c_word, 1000)
    
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

    # Convert CLI and EMO score.
    c_cli = dom.attrib['c_cli']
    add_per(dom, 'crx_cli', int(c_cli), c_word, 1000)
    
    c_emo = dom.attrib['c_emo']
    add_per(dom, 'crx_emo', int(c_emo), c_word, 1000)
