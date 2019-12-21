# -*- coding: utf-8 -*-

# Get elemenatry features from COW-DOM.

import os.path
import sys
import glob
import re
from lxml import etree as ET
from subtree import SubtreeBuilder
from anytree import Node, RenderTree, find, AnyNode, findall
import operator


stb = SubtreeBuilder(depindpos=0, dephdpos=2, deprelpos=1)


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



def feature_within_s(annolayer, list_of_s):
    """Extracts all <annolayer> from all sentence-elements in list_of_s;
    returns a flat list of <annolayer>-elements;
    """
    list_of_lists_of_feature = [s.findall('.//' + annolayer) for s in list_of_s]
    list_of_feature = [element for sublist in list_of_lists_of_feature for element in sublist]
    return(list_of_feature)


def convert(raw_tokens_annos):
        l = [(i[0],i[1].split("\t")) for i in raw_tokens_annos]
        return(l)


def mk_nodes(token_attrs):
    # create  nodes; add dependency information under separate attributes, and all other annotations under another attribute
        return([AnyNode(word=token, depind=attrs[0], dephd=attrs[2], deprel=attrs[0], annos="/".join([a for num, a in enumerate(attrs) if not num in [0, 1, 2]])) for (token, attrs) in token_attrs])


def mk_ngrams(nodelist, n):
    l = list()
    for num, item in enumerate(nodelist):
        if len(nodelist[num:]) > n-1:
            l.append(nodelist[num:num+n])
    return(l)


def depgrams(dom, fh, sentencefilter):

    docngrams = list()

    # Get word count.
    allwords = dom.findall('.//*word')
    c_allword = len(allwords)
    dom.attrib['crx_alltokc'] = str(c_allword)

    # Get sentences:

    if len(sentencefilter) > 0:
        sentences = dom.findall(".//s[" + sentencefilter + "]")
    else:
        sentences = dom.findall(".//s")

    # make dep-grams for every sentence and add to document dep-grams:
    for s in sentences:
        words = [w.text for w in s.findall('.//*word')]
        depinds = [i.text for i in s.findall('.//*depind')]
        deprels = [i.text for i in s.findall('.//*deprel')]
        dephds = [i.text for i in s.findall('.//*dephd')]


        # make input structure suitable for subtree.py:
        dep = ["\t".join(d) for d in zip(depinds, deprels, dephds)]
        tokens_annos = zip(words, dep)

        # construct dependency tree:
        stb.update(tokens_annos)

        # collect all leaves:
        leaves = findall(stb.topnode, filter_=lambda node: node.is_leaf)

        # for every leaf, get complete path from top node:
        paths = [list(l.ancestors) + [l] for l in leaves]

        # produce ngrams and store in common list:
        allngrams = list()
        for  p in paths:
            allngrams.extend(mk_ngrams(p,2))

        # Make sure every sub-path occurs only once,
        # i.e., ignore shared path prefixes:
        # E.g., paths a/b/c and a/b/d give ngrams [a/b, b/c, a/b, b/d],
        # but we only want [a/b, b/c, b/d].
        # (Must convert lists to tuples first because lists are
        # not hashable; then convert back to list.)
        allngramsuniq  = [list(x) for x in set(tuple(x) for x in allngrams)]

        # add depgrams from this sentence to document depgrams:
        for ngram in allngramsuniq:
            docngrams.append((" ".join([n.deprel for n in ngram])))


    # count depgrams at the document level:
    d = dict()
    for n in docngrams:
        if not n in d:
            d[n] = 1
        else:
            d[n] += 1


    # for debugging: reverse-sort and print doc-level depgram freauencies:
    sorted_d = sorted(d.items(), key=operator.itemgetter(1), reverse=True)

    for i in sorted_d:
        print(i[0]),
        print(i[1])
    print("\n\n")



















# Get tokens:
#    words = feature_within_s('word', sentences)
#
#    c_word = len(words)
#    dom.attrib['crx_tokc'] = str(c_word)
#
#
#    # Get type/token ratio based on lowercased tokens.
#    tokens = [t.text.lower() for t in words]
#
#    types = set(tokens)
#    if len(tokens) > 0:
#        r_type_token = len(types)/float(len(tokens))
#    else:
#        r_type_token = -1
#    dom.attrib['crx_ttrat'] = fh.act(r_type_token)
#
#    # Get avg word length.
#    if c_word > 0:
#        avg_word_length = sum([len(w.text) for w in words])/float(c_word)
#    else:
#        avg_word_length = 0
#    dom.attrib['crx_wlen'] = fh.act(avg_word_length)
#
#    # Get sentence count.
#    c_sentences = len(sentences)
#    dom.attrib['crx_sentc'] = str(c_sentences)
#
#    # Get avg sentence length.
#    if c_sentences > 0:
#        avg_sentence_length = fh.act(sum([len(s.findall('.//*token')) for s in sentences])/float(c_sentences))
#    else:
#        avg_sentence_length = 0
#    dom.attrib['crx_slen'] = fh.act(float(avg_sentence_length))
#
#    # Get POS counts (modal verbs etc.).
#    posse = feature_within_s('ttpos', sentences)
#
#
#    # Number of modal verbs.
#    c_modals = len([p for p in posse if p.text[:2] == 'VM'])
#    add_per(dom, 'crx_mod', c_modals, c_word, fh)
#
#    # Number of full verbs.
#    c_verbs = len([p for p in posse if p.text[:2] == 'VV'])
#    add_per(dom, 'crx_vv', c_verbs, c_word, fh)
#
#    # Numer of auxiliaries.
#    c_aux = len([p for p in posse if p.text[:2] == 'VA'])
#    add_per(dom, 'crx_vaux', c_aux, c_word, fh)
#
#    # Number of finite verbs.
#    vfin = [p for p in posse if p.text in ['VAFIN', 'VMFIN', 'VVFIN']]
#    c_vfin = len(vfin)
#    add_per(dom, 'crx_vfin', c_vfin, c_word, fh)
#
#    # Number of common nouns.
#    c_commonnouns = len([p for p in posse if p.text == 'NN'])
#    add_per(dom, 'crx_cn', c_commonnouns, c_word, fh)
#
#
#    # Number of prepositions.
#    c_prepositions = len([p for p in posse if p.text[:2] == 'AP'])
#    add_per(dom, 'crx_prep', c_prepositions, c_word, fh)
#
#    # Number of infinitives.
#    c_infinitives = len([p for p in posse if p.text in ['VAINF', 'VMINF', 'VVINF']])
#    add_per(dom, 'crx_inf', c_infinitives, c_word, fh)
#
#    # Number of imperatives.
#    c_imperatives = len([p for p in posse if p.text in ['VAIMP', 'VMIMP', 'VVIMP']])
#    add_per(dom, 'crx_imp', c_imperatives, c_word, fh)
#
#    # Number of adverbs.
#    c_adverbs = len([p for p in posse if p.text == 'ADV'])
#    add_per(dom, 'crx_adv', c_adverbs, c_word, fh)
#
#    # Number of adjectives.
#    c_adjectives = len([p for p in posse if p.text[:3] == 'ADJ'])
#    add_per(dom, 'crx_adj', c_adjectives, c_word, fh)
#
#    # Number of subordinators.
#    c_subjunctions_w_sentence = len([p for p in posse if p.text == 'KOUS'])
#    add_per(dom, 'crx_subjs', c_subjunctions_w_sentence, c_word, fh)
#
#    # Number of infinitive-embedders.
#    c_subjunctions_w_infinitive = len([p for p in posse if p.text == 'KOUI'])
#    add_per(dom, 'crx_subji', c_subjunctions_w_infinitive, c_word, fh)
#
#    # Number of coordinators.
#    c_conjunctions = len([p for p in posse if p.text == 'KON'])
#    add_per(dom, 'crx_conj', c_conjunctions, c_word, fh)
#
#    # Number of wh pronouns.
#    c_wh = len([p for p in posse if p.text[:2] == 'PW'])
#    add_per(dom, 'crx_wh', c_wh, c_word, fh)
#
#    # Demonstratives.
#    c_dem = len([p for p in posse if p.text[:2] == 'PD'])
#    add_per(dom, 'crx_dem', c_dem, c_word, fh)
#
#    # Possessives.
#    c_poss =  len([p for p in posse if p.text[:4] == 'PPOS'])
#    add_per(dom, 'crx_poss', c_poss, c_word, fh)
#
#    c_neg =  len([p for p in posse if p.text == 'PTKNEG'])
#    add_per(dom, 'crx_neg', c_neg, c_word, fh)
#
#    c_answ = len([p for p in posse if p.text == 'PTKANT'])
#    add_per(dom, 'crx_answ', c_answ, c_word, fh)
#
#    c_zuinf = len([p for p in posse if p.text == 'PTKZU'])
#    add_per(dom, 'crx_zuinf', c_zuinf, c_word, fh)
#
#    c_parta = len([p for p in posse if p.text == 'PTKA'])
#    add_per(dom, 'crx_parta', c_parta, c_word, fh)
#
#    c_card = len([p for p in posse if p.text == 'CARD'])
#    add_per(dom, 'crx_card', c_card, c_word, fh)
#
#    c_itj = len([p for p in posse if p.text == 'ITJ'])
#    add_per(dom, 'crx_itj', c_itj, c_word, fh)
#
#    c_nonwrd = len([p for p in posse if p.text == 'XY'])
#    add_per(dom, 'crx_nonwrd', c_nonwrd, c_word, fh)
#
#    # We need parents -> lemmas for article counting.
#    posse_lemmas = [firstlemma(p.find('../lemma').text) for p in posse if p.text == 'ART']
#
#    c_def_article = len([a for a in posse_lemmas if a == 'die'])
#    add_per(dom, 'crx_def', c_def_article, c_word, fh)
#
#    c_indef_article = len([a for a in posse_lemmas if a in ['n', 'eine']])
#    add_per(dom, 'crx_indef', c_indef_article, c_word, fh)
#
#    # NER-related counts.
#    # Count only within regular sentences:
#
#    nerds = feature_within_s('ne', sentences)
#
#    c_ne_per = len([n for n in nerds if n.text == 'I-PER'])
#    add_per(dom, 'crx_neper', c_ne_per, c_word, fh)
#
#    c_ne_loc = len([n for n in nerds if n.text == 'I-LOC'])
#    add_per(dom, 'crx_neloc', c_ne_loc, c_word, fh)
#
#    c_ne_org = len([n for n in nerds if n.text == 'I-ORG'])
#    add_per(dom, 'crx_neorg', c_ne_org, c_word, fh)
#
#    # Get all lemmas, count only within regular sentences:
#    lemmas = feature_within_s('lemma', sentences)
#
#
#    # Emoticons:
#    c_emo = len([l for l in lemmas if firstlemma(l.text) == '(smiley)'])
#    add_per(dom, 'crx_emo', c_emo, c_word, fh)
#
#    # Quotes:
#    c_doublequote = len([t for t in tokens if t == '"'])
#    add_per(dom, 'crx_dq', c_doublequote, c_word, fh)
#
#    # Cliticized indefinite articles:
#    c_clit_indef_article = len([a for a in posse_lemmas if a == 'n'])
#    add_per(dom, 'crx_clitindef', c_clit_indef_article, (c_indef_article + c_clit_indef_article), fh)
#
#    # Counts using morphological information.
#
#    # Get Marmot's morphological annotation
#    morphs = dom.findall('.//morph')
#    morphtexts = [morph.text for morph in morphs]
#    morphsets = [m.strip('|').split('|') for m in morphtexts if len(m) > 1]
#
#    # Get past tense verbs:
#    c_vpast = len([m for m in morphsets if 'past' in m])
#    add_per(dom, 'crx_vpast', c_vpast, c_word, fh)
#
#    # Get present tense verbs:
#    c_vpres = len([m for m in morphsets if 'pres' in m])
#    add_per(dom, 'crx_vpres', c_vpres, c_word, fh)
#
#    # Get present tense, subjunctive mood verbs
#    c_vpressubj = len([m for m in morphsets if 'pres' in m and 'subj' in m])
#    add_per(dom, 'crx_vpressubj', c_vpressubj, c_word, fh)
#
#    # Get count for all verbs, subjunctive & past tense:
#    past_subj = [m for m in morphs if 'past' in parsemorphs(m.text) and 'subj' in parsemorphs(m.text)]
#    c_past_subj = len(past_subj)
#
#    # Get count for 'werden', subjunctive & past tense:
#    wpast_subj =  [m for m in past_subj if firstlemma(m.findall('../lemma')[0].text) == 'werden']
#    c_wpast_subj = len(wpast_subj)
#    add_per(dom, 'crx_wpastsubj', c_wpast_subj, c_word, fh)
#
#    # The difference is the count for non-'werden' subjunctive & past tense:
#    add_per(dom, 'crx_vvpastsubj', (c_past_subj - c_wpast_subj), c_word, fh)
#
#
#    # Get Marmot's morphological annotation for personal pronouns:
#    mposse_pp_morphs = [parsemorphs(p.find('../morph').text) for p in posse if p.text in ['PPER', 'PRF']]
#
#    # Get 1st person personal pronouns:
#    c_pper_1st = len([m for m in mposse_pp_morphs if '1' in m])
#    add_per(dom, 'crx_pper_1st', c_pper_1st, c_word, fh)
#
#    # Get 2nd person personal pronouns:
#    c_pper_2nd = len([m for m in mposse_pp_morphs if '2' in m])
#    add_per(dom, 'crx_pper_2nd', c_pper_2nd, c_word, fh)
#
#    # Get 3rd person personal pronouns:
#    c_pper_3rd = len([m for m in mposse_pp_morphs if '3' in m])
#    add_per(dom, 'crx_pper_3rd', c_pper_3rd, c_word, fh)
#
#    # Get proportion genitive NNs / all NNs
#    # (use TreeTaggers POS-tags: has extended lexicon, should be more reliable)
#    posse_n_morphs = [parsemorphs(p.find('../morph').text) for p in posse if p.text in ['NN', 'NE']]
#    c_gen = len([m for m in posse_n_morphs if 'gen' in m])
#    add_per(dom, 'crx_gen', c_gen, float(len( posse_n_morphs )), fh)
#
#
#    # Counts related to topological fields.
#
#    # Get clauses:
#    c_simpx = len(feature_within_s('simpx', sentences))
#    add_per(dom, 'crx_simpx', c_simpx, c_sentences, fh, 1)
#
#    # Get coordinated clauses:
#    c_psimpx =  len(feature_within_s('psimpx', sentences))
#    add_per(dom, 'crx_psimpx', c_psimpx, c_sentences, fh, 1)
#
#    # Get relative clauses:
#    c_rsimpx = len(feature_within_s('rsimpx', sentences))
#    add_per(dom, 'crx_rsimpx', c_rsimpx, c_sentences, fh, 1)
#
#
#    # Get prefields:
#    vfs = feature_within_s('vf', sentences)
#
#    # Get verb-second sentences:
#    c_vf = len(vfs)
#    add_per(dom, 'crx_v2', c_vf, c_sentences, fh, 1)
#
#    # Get verb-last sentences:
#    c_c = len(feature_within_s('c', sentences))
#
#    add_per(dom, 'crx_vlast', c_c, c_sentences, fh, 1)
#
#
#    # Get text in the prefield:
#    wordelements_in_vf = [vf.findall('.//word') for vf in vfs]
#    texts_in_vf = [[word.text for word in wordelement] for wordelement in wordelements_in_vf]
#
#    # Get average length of prefields:
#    if c_vf > 0:
#    	avg_vf_length = sum([len(t) for t in texts_in_vf ])/float(c_vf)
#    else:
#	avg_vf_length = 0
#    dom.attrib['crx_vflen'] = fh.act(avg_vf_length)
#
#    # Get pronoun 'es' in the prefield:
#    c_es_vf = len([t for t in texts_in_vf if t == ['Es'] or t == ['es']])
#    add_per(dom, 'crx_esvf', c_es_vf, c_vf, fh)
#
#    # Get complex prefields (containing a clause):
#    # Just look for a simpx as a child of vf; do not look for further embedded simpxs
#    c_clausal_vf = len([vfelement.findall('simpx') for vfelement in vfs if len(vfelement.findall('simpx')) > 0])
#    add_per(dom, 'crx_clausevf', c_clausal_vf, c_vf, fh)
#
#    # Get compound nouns
#    c_posse_nn_comp = len([p.find('../comp').text for p in posse if p.text == 'NN' and len(p.find('../comp').text) > 1])
#    add_per(dom, 'crx_cmpnd', c_posse_nn_comp, c_commonnouns, fh)
#
#    # Get (unknown)s. Condition: not a named entity and not a compound noun.
#    c_unknowns = len([t.text for t in words if firstlemma(t.findall('../lemma')[0].text) == '(unknown)' and t.findall('../ne')[0].text == 'O' and len(t.findall('../comp')[0].text) == 1])
#    add_per(dom, 'crx_unkn', c_unknowns, c_word, fh)
#
#
#    # dictionaries of some shortened or contracted forms (mostly from decow16 lexicon additions):
#    # "musste"?
#    contracted_verbs = {'find': '', 'findeste': '', 'finds': '', 'fänd': '', 'gabs': '', 'geh': '', 'gehn': '', 'gehts': '', 'gibbet': '', 'gibs': '', 'gibts': '', 'hab': '', 'habs': '', 'ham': '', 'hamm': '', 'hamma': '', 'haste': '', 'hats': '', 'hatt': '', 'hätt': '', 'is': '', 'isser': '', 'isses': '', 'ists': '', 'kamste': '', 'kanns': '', 'kannste': '', 'klappts': '', 'kommste': '', 'kommts': '', 'konnt': '', 'konnteste': '', 'lern': '', 'lernste': '', 'läufste': '', 'läufts': '', 'mach': '', 'machs': '', 'machts': '', 'musste': '', 'möcht': '', 'möchts': '', 'nehm': '', 'nimms': '', 'nimmste': '', 'sach': '', 'sacht': '', 'schaus': '', 'schauts': '', 'schomma': '', 'seh': '', 'siehts': '', 'sinds': '', 'sollste': '', 'tu': '', 'tuen': '', 'tuste': '', 'tuts': '', 'wars': '', 'wat': '', 'werd': '', 'werds': '', 'willste': '', 'wirds': '', 'wirste': '', 'wär': '', 'wärs': '', 'würd': '', 'würds': ''}
#
#    contracted_preps = {'aufer': '', 'aufm': '', 'aufn': '', 'aufs': '', 'auser': '', 'ausm': '', 'drauf ': '', 'drunter': '', 'drüber': '', 'fürn': '', 'fürs': '', 'innem': '', 'inner': '', 'mitem': '', 'miter': '', 'mitm': '', 'nebens': '', 'unterm': '', 'untern': '', 'unters': '', 'überm': '', 'übern': '', 'übers': ''}
#
#
#    tokens = [t.text.lower() for t in words]
#
#    c_shortform = len([t for t in tokens if t in contracted_preps or t in contracted_verbs])
#    add_per(dom, 'crx_short', c_shortform, c_word, fh)
#
#    c_qsvoc = len([t for t in tokens if t in ['nich', 'net', 'nochma', 'nochwas', 'nichtmal', 'nichtmehr', 'schonmal', 'schomma', 'ok', 'okay' ]])
#    add_per(dom, 'crx_qsvoc', c_qsvoc, c_word, fh)
#
#    c_loan_n = len([firstlemma(l.text) for l in lemmas if l.findall('../ttpos')[0].text == 'NN' and l.findall('../ne')[0].text == 'O' and re.match(u'.{3,}(or|ent|ant|iat|aph|af|ide|ast|[bcdfghjklmnpqrstvwxyz](it|a|o|u|il|us|on|um|ik|ist|ur|ar|ade|et|ip)|eur|ör|ium|ion|ve|iv|iar|ion|x|enz|ät|ette|enz|ens|ell|ee|ole|äre)$', firstlemma(l.text))])
#    add_per(dom, 'crx_cnloan', c_loan_n, c_commonnouns, fh)
#
#    # TODO: also exclude (an|be|voll)schmieren, (ge|an|be|durch|er|ein)frieren
#    c_ieren_v = len([firstlemma(l.text) for l in lemmas if l.findall('../ttpos')[0].text[:2] == 'VV' and firstlemma(l.text) != 'verlieren' and re.match(u'.{2,}[bcdfghjklmnpqrstvwxyz]ieren$', firstlemma(l.text))])
#    add_per(dom, 'crx_vvieren', c_ieren_v,  c_verbs, fh)
#
#    c_sapos = len([t for t in tokens if t == "'s"])
#    add_per(dom, 'crx_sapos', c_sapos,  c_word, fh)
