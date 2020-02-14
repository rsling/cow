# -*- coding: utf-8 -*-

# Get N-grams of dependency relations from COW-DOM.

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

    docbigrams = list()
    doctrigrams = list()

    # Get word count.
    allwords = dom.findall('.//*word')
    c_allword = len(allwords)
    dom.attrib['crx_alltokc'] = str(c_allword)

    # Get sentences:

    if len(sentencefilter) > 0:
        sentences = dom.findall(".//s[" + sentencefilter + "]")
    else:
        sentences = dom.findall(".//s")

    # try to get word count from previous corex run:
    if dom.get('crx_tokc'):
        tokc = int(dom.get('crx_tokc'))
    else:
        tokc = len(feature_within_s('word', sentences))




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

        # for every leaf, get complete path from top node (but exclude top node
        # itself)
        paths = [[i for i in list(l.ancestors) if not i.depind == "TOP"] + [l] for l in leaves]


        # produce bigrams and store in common list:
        allbigrams = list()

        for  p in paths:
            allbigrams.extend(mk_ngrams(p,2))

        # Make sure every sub-path occurs only once,
        # i.e., ignore shared path prefixes:
        # E.g., paths a/b/c and a/b/d give ngrams [a/b, b/c, a/b, b/d],
        # but we only want [a/b, b/c, b/d].
        # (Must convert lists to tuples first because lists are
        # not hashable; then convert back to list.)
        allbigramsuniq  = [list(x) for x in set(tuple(x) for x in allbigrams)]

        # add depgrams from this sentence to document depgrams:
        for ngram in allbigramsuniq:
            docbigrams.append(("~".join([n.deprel for n in ngram])))

#        # do the same for trigrams:
#        alltrigrams = list()
#
#        for  p in paths:
#            alltrigrams.extend(mk_ngrams(p,3))
#
#        alltrigramsuniq  = [list(x) for x in set(tuple(x) for x in alltrigrams)]
#
#        # add depgrams from this sentence to document depgrams:
#        for ngram in alltrigramsuniq:
#            doctrigrams.append(("~".join([n.deprel for n in ngram])))
#


    # count depgrams at the document level:
    bid = dict()
    for n in docbigrams:
        if not n in bid:
            bid[n] = 1
        else:
            bid[n] += 1



    # count depgrams at the document level:
#    trid = dict()
#   for n in doctrigrams:
#        if not n in bid:
#            trid[n] = 1
#        else:
#            trid[n] += 1




    print('<doc id="' + dom.get("id") + '" tokc="' + str(tokc) + '">')

    sorted_bid = sorted(bid.items(), key=operator.itemgetter(1), reverse=True)

    for depgram, freq in sorted_bid:
         print("\t".join(["d2\t" + depgram, str(round((freq/float(tokc))*1000, 3)), str(freq)]))


   # for n in bid:
   #     print("\t".join(["d2\t" + n, str(round((bid[n]/float(tokc))*1000, 3)), str(bid[n])]))



#    sorted_trid = sorted(trid.items(), key=operator.itemgetter(1), reverse=True)

#    for depgram, freq in sorted_trid:
#         print("\t".join(["d3\t" + depgram, str(round((freq/float(tokc))*1000, 3)), str(freq)]))


    #for n in trid:
    #     print("\t".join(["d3\t" + n, str(round((trid[n]/float(tokc))*1000, 3)), str(trid[n])]))



