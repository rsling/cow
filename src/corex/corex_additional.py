# -*- coding: utf-8 -*-

# Get elemenatry features from COW-DOM.

import os.path
import sys
import glob
import re
from lxml import etree as ET


# add a lists of "communication verbs" here:

COGNITION_VERBS = set([u'wissen', u'kennen', u'glauben', u'vermuten', u'ahnen',
                           u'annehmen', u'zweifeln', u'erfahren', u'kennenlernen',
                           u'erkennen', u'vergessen', u'meinen', u'denken',
                           u'bezweifeln', u'beschließen'])

VERBA_DICENDI = set([u'sagen', u'sprechen', u'behaupten', u'sprechen', u'reden', u'äußern'])

REPRESENTATIVES = set([u'argumentieren', u'behaupten', u'beteuern', u'bekräftigen',
                           u'bekunden', u'beschwören', u'garantieren', u'schwören',
                           u'verbürgen', u'versichern', u'wetten', u'feststellen',
                           u'konstatieren', u'lügen', u'anlügen', u'belügen', u'erlügen',
                           u'rumlügen', u'vorlügen', u'anflunkern', u'anschwindeln',
                           u'beschwindeln', u'erschwindeln', u'flunkern', u'rumflunkern',
                           u'rumschwindeln', u'vorflunkern', u'vorschwindeln', u'abstreiten',
                           u'bestreiten', u'leugnen', u'verneinen', u'widersprechen',
                           u'kontern', u'widerlegen', u'entkräften', u'dementieren',
                           u'zustimmen', u'beipflichten', u'bejahen', u'bestätigen',
                           u'anzweifeln', u'bezweifeln', u'beharren', u'insistieren',
                           u'eingestehen', u'zugeben', u'zugestehen'])

DIRECTIVES = set([u'abkommandieren', u'abberufen', u'anleiten', u'anweisen',
                      u'instruieren', u'einweisen', u'anweisen', u'auffordern',
                      u'auftragen', u'mahnen', u'ermahnen', u'gemahnen', u'beauftragen',
                      u'autorisieren', u'berechtigen', u'ermächtigen', u'fordern',
                      u'verlangen', u'flehen', u'anbetteln', u'anflehen', u'beschwören',
                      u'betteln', u'erflehen', u'verweisen', u'vorschlagen', u'befragen',
                      u'erfragen', u'nachfragen', u'fragen', u'herumfragen', u'raten',
                      u'beraten'])

COMMISSIVES = set([u'drohen', u'androhen', u'bedrohen', u'vereinbaren', u'absprechen',
                       u'aushandeln', u'ablehnen', u'zurückweisen', u'protestieren',
                       u'einwilligen', u'zusagen', u'geloben', u'schwören', u'versichern',
                       u'versprechen'])

EXPRESSIVES = set([u'prahlen', u'protzen', u'schönreden', u'beschuldigen',
                       u'beurteilen', u'einschätzen', u'urteilen', u'beschimpfen',
                       u'anschimpfen', u'anbrüllen', u'anscheißen', u'anschnauzen',
                       u'anschreien', u'meckern', u'schimpfen', u'fluchen',
                       u'verfluchen', u'danken', u'gratulieren', u'beglückwünschen',
                       u'klagen', u'bedauern', u'beklagen', u'jammern', u'lamentieren',
                       u'kondolieren', u'diffamieren', u'anschwärzen', u'diskreditieren',
                       u'verleumden', u'beleidigen', u'herabsetzen', u'herabwürdigen',
                       u'lästern', u'mosern', u'motzen', u'murren', u'nörgeln',
                       u'tadeln', u'anprangern', u'kritisieren', u'monieren',
                       u'beanstanden', u'bemängeln', u'missbilligen', u'vorwerfen',
                       u'loben', u'huldigen', u'ehren', u'würdigen', u'honorieren',
                       u'preisen', u'lobpreisen', u'rühmen', u'schwärmen',
                       u'rechtfertigen'])

DECLARATIVES = set([u'bestätigen', u'anerkennen', u'beglaubigen', u'ratifizieren',
                        u'definieren', u'festsetzen', u'bestimmen', u'festlegen',
                        u'entlassen', u'freilassen', u'erklären', u'verkünden',
                        u'kundtun', u'bekanntgeben', u'proklamieren', u'festlegen',
                        u'vorschreiben', u'anberaumen', u'feststellen', u'kündigen',
                        u'taufen', u'nennen', u'einweihen', u'degradieren',
                        u'ernennen', u'nominieren', u'melden', u'segnen',
                        u'lossprechen', u'aberkennen', u'beichten', u'gestehen'])



# Just for rounding. StringHandler etc. maybe?
class FloatHandler:
    def __init__(self, digits):
        self.digits = digits

    def act(self, d):
        return str(round(d, self.digits))


def per(x, n, p = 1000):
    if n > 0:
        return x/float(n)*p
    else:
        return float(0)


def add_per(doc, attr, x, n, fh, p = 1000):
    doc.attrib[attr] = fh.act(per(x,n,p))


def parsemorphs(text):
    morphlist = []
    if len(text) > 1:
        morphlist = text.strip('|').split('|')
    return(morphlist)


def firstlemma(lemmastring):
    """ Selects the first lemma from a string denoting a set of lemmas,
     e.g. |x|y|  ==>  x"""
    lemmastring = lemmastring.strip("|")
    lemmalist = lemmastring.split("|")
    return(lemmalist[0])


def feature_within_s(annolayer, list_of_s):
    """Extracts all <annolayer> from all sentence-elements in list_of_s;
    returns a flat list of <annolayer>-elements;
    """
    list_of_lists_of_feature = [s.findall('.//' + annolayer) for s in list_of_s]
    list_of_feature = [element for sublist in list_of_lists_of_feature for element in sublist]
    return(list_of_feature)


def annotate_additional(dom, fh, sentencefilter):

    # Get word count from previous COReX run:
    c_word = int(dom.get('crx_tokc'))

    # Get sentences:

    if len(sentencefilter) > 0:
        sentences = dom.findall(".//s[" + sentencefilter + "]")
    else:
        sentences = dom.findall(".//s")

    # repair (redo) clitindef counts:

    # Get POS counts (modal verbs etc.).
    posse = feature_within_s('ttpos', sentences)

    # Get Number of full verbs (for normalizing):
    c_verbs = len([p for p in posse if p.text[:2] == 'VV'])

    # We need parents -> lemmas for article counting.
    posse_lemmas = [firstlemma(p.find('../lemma').text) for p in posse if p.text == 'ART']

    c_indef_article = len([a for a in posse_lemmas if a in ['n', 'eine']])
    add_per(dom, 'crx_indef', c_indef_article, c_word, fh)
    dom.attrib['crx_indefraw'] = str(c_indef_article)


    c_clit_indef_article = len([a for a in posse_lemmas if a == 'n'])
    add_per(dom, 'crx_clitindef', c_clit_indef_article, c_indef_article, fh)
    dom.attrib['crx_clitindefraw'] = str(c_clit_indef_article)


    # Get tokens, count only within regular sentences:

    words_str = [t.text.lower() for t in feature_within_s('word', sentences)]

    # Get all lemmas, count only within regular sentences:
    lemmas_str = [firstlemma(l.text.lower()) for l in  feature_within_s('lemma', sentences)]


    # count (sequences of) exclamation marks:
    c_exclamationmarks = len([w for w in words_str if re.match(u'^!+$', w)])
    add_per(dom, 'crx_excl', c_exclamationmarks, c_word, fh)

    # count (sequences of) question marks:
    c_questionmarks = len([w for w in words_str if re.match(u'^\?+$', w)])
    add_per(dom, 'crx_ques', c_questionmarks, c_word, fh)

    # count combinations of question marks and exclamation marks:
    c_exclques = len([w for w in words_str if re.match(u'^(?:\?+![?!]*$)|(!+\?[!?]*)$', w)])
    add_per(dom, 'crx_exclques', c_exclques, c_word, fh)


    # count "cognition" verbs:
    c_cogverbs = len([l for l in lemmas_str if l in COGNITION_VERBS])
    add_per(dom, 'crx_cogverb', c_cogverbs, c_verbs, fh)

    # Count verbs typical of different kinds of speech acts:

    # count "communication verbs":
    c_dicverbs = len([l for l in lemmas_str if l in VERBA_DICENDI])
    add_per(dom, 'crx_dicverb', c_dicverbs, c_verbs, fh)

    # count "representative verbs":
    c_reprverbs = len([l for l in lemmas_str if l in REPRESENTATIVES])
    add_per(dom, 'crx_reprverb', c_reprverbs, c_verbs, fh)

    # count "directive verbs":
    c_dirverbs = len([l for l in lemmas_str if l in DIRECTIVES])
    add_per(dom, 'crx_dirverb', c_dirverbs, c_verbs, fh)

    # count "commissive verbs":
    c_commissverbs = len([l for l in lemmas_str if l in COMMISSIVES])
    add_per(dom, 'crx_commissverb', c_commissverbs, c_verbs, fh)

    # count "expressive verbs":
    c_exprverbs = len([l for l in lemmas_str if l in EXPRESSIVES])
    add_per(dom, 'crx_exprverb', c_exprverbs, c_verbs, fh)

    # count "declarative verbs":
    c_declverbs = len([l for l in lemmas_str if l in DECLARATIVES])
    add_per(dom, 'crx_declverb', c_declverbs, c_verbs, fh)


