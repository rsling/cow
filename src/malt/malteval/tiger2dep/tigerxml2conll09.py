#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This file implements a SAX handler to parse TiGerXML and converting it to dependencies.
# Note that the conversion only works with version 2.1 of the TiGer corpus, release August 2007.
#
# author: Wolfgang Seeker
# 19/12/2012
#

import sys
import codecs
import xml.sax.handler
import psnode
import dependencyconverter
from collections import defaultdict

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

# This class is code I modified from Gerlof Bouma's tgxml2pl.py from QPL (which he modified from my code ;)
class Tiger2DepHandler( xml.sax.handler.ContentHandler ):
    """
    This class implements a handler for the sax parser that reads in the Tiger xml
    sentence by sentence and converts it to dependency format.
    """
    def __init__( self, converter, datasource ):
        self.datasource = datasource
        self.converter = converter
        self.sid = 0
        self.root = u''
        self.phrases = {}
        self.words = {}
        self.primarygraph = {}
        self.secondarygraph = defaultdict(set)
        self.secedges = []
        self.nodeid = 0
        if self.datasource == 'tiger':
            self.morphatts = ('case','number','gender','person','degree','tense','mood')
        elif self.datasource == 'smultron':
            self.morphatts = ('morph',)
        elif self.datasource == 'europarl':
            self.morphatts = ('morph',)

    def startElement( self, name, attributes ):
        "handles start elements"
        # sentence
        if name == 's':
            self.sid = int(attributes['id'][1:])
        # graph (holding the actual syntactic graph inside an <s>...</s>)
        elif name == 'graph':
            self.phrases = {}
            self.words = {}
            self.secedges = []
            self.root = attributes['root'].split('_',1)[1]
            self.primarygraph = {}
            self.secondarygraph = defaultdict(set)
        # terminals/words
        elif name == u't':
            nodeid_str = attributes['id'].split('_',1)[1]
            # virtual roots should not occur here
            if nodeid_str == u'VROOT':
                raise Exception, 'Found a VROOT terminal, at %s.' % (attributes['id'],)  
            # actual nodes in the tree
            else:
                self.nodeid = int(nodeid_str)
                kvs = ((att,attributes[att]) for att in self.morphatts)
                morphs = [(k,v) for k,v in kvs if not v == '--']
                self.words[self.nodeid] = (attributes['word'],attributes['lemma'] if self.datasource != 'europarl' else '--',attributes['pos'],morphs)
                # non-virtual roots are unrooted and attached to -1
                if nodeid_str == self.root:
                    self.primarygraph[self.nodeid] = (-1,u'--')
        # non-terminals/phrases
        elif name == u'nt':
            nodeid_str = attributes['id'].split('_',1)[1]
            # virtual roots are not node/8 facts
            if nodeid_str == u'VROOT':
                self.nodeid = -1
            # actual nodes in the tree
            else:
                self.nodeid = int(nodeid_str)
                self.phrases[self.nodeid] = (attributes['cat'],)
                # non-virtual roots are unrooted and attached under a virtual virtual root
                if nodeid_str == self.root:
                    self.primarygraph[self.nodeid] = (-1,u'--')
        # primary edges (indegree 1, pointing away from root)
        elif name == u'edge':
            daughter = int(attributes['idref'].split('_',1)[1])
            self.primarygraph[daughter] = (self.nodeid,attributes['label'])
        # secondary edges (possible indegree >1, pointing away from root)
        elif name == 'secedge':
            self.secondarygraph[self.nodeid].add((int(attributes['idref'].split(u'_',1)[1]),attributes['label']))

    def endElement(self, name):
        "handles closing elements"
	    # if a sentence was found, convert it to dependencies and print
        if name == 's':
            sentence = self.nodes2list()
    	    self.converter.convert(sentence)
            if self.datasource == 'smultron':
                self.replace_HD(sentence)
                self.remove_html(sentence)
    	    print '\n'.join(map(lambda x: x + '\t_\t_', map(unicode,sentence)))
    	    print

    def nodes2list(self):
        "converts the last sentence to a list format"
        sentence = []
        for nodeid in sorted(self.words):
            surf,lemma,pos,morph = self.words[nodeid]
            mother, edge = self.primarygraph.get(nodeid,(-1,'--'))
            node = psnode.PSNode()
            node.sid = self.sid
            node.nid = nodeid
            node.form = surf
            node.lemma = lemma if lemma else '_'
            node.pos = pos if pos else '_'
            node.morph = morph
            node.head = mother
            node.label = edge if edge else '_'
            node.leaf = True
            sentence.append(node)
            
        for nodeid in sorted(self.phrases):
            mother, edge = self.primarygraph.get(nodeid,(-1,'--'))
            pos, = self.phrases[nodeid]
            node = psnode.PSNode()
            node.sid = self.sid
            node.nid = nodeid
            node.pos = pos            
            node.head = mother
            node.label = edge
            node.leaf = False
            node.head = mother
            node.label = edge
            sentence.append(node)
            
        for i,node in enumerate(sentence):
            if node.nid > 499:
                newnid = i+1
                for d in sentence:
                    if d.head == node.nid:
                        d.head = newnid
                node.origid = node.nid
                node.nid = newnid
                
        return sentence

    def replace_HD( self, sentence ):
        for node in sentence:
            if node.label == 'HD':
                if node.pos in ['NN','NE']:
                    node.label = 'NK'
                elif node.pos in ['APPR','APZR']:
                    node.label = 'AC'

    def remove_html( self, sentence ):
        nids = [ (i,n.nid) for i,n in enumerate(sentence) if n.pos == '--' ]
        for _,nid in reversed(nids):
            for n in sentence:
                if n.nid > nid:
                    n.nid -= 1
                if n.head > nid:
                    n.head -= 1
        for i,_ in reversed(nids):
            del sentence[i]


### MAIN ###
import argparse

argpar = argparse.ArgumentParser(description='Converts TiGer to dependency format')
argpar.add_argument('-i','--input',dest='inputfile',help='the TiGerXML file version 2.1 (Release August 2006)',required=True)
argpar.add_argument('-m','--manual-heads',dest='headsfile',help='the file that specifies the heads that were selected manually',required=True)
argpar.add_argument('-p','--punctuation',dest='punctuation',choices=['deepest-common-ancestor','easy'],default='deepest-common-ancestor',help='set the way, punctuation is attached (default: highest-common-ancestor)')
argpar.add_argument('-c','--coordination',dest='coordination',choices=['chain','bush'],default='chain',help='set the way, coordination is annotated (default: chain)')
argpar.add_argument('-e','--ellipsis',dest='ellipsis',choices=['resolve','keep'],default='resolve',help='set the way, ellipsis is annotated (default: resolve)')
argpar.add_argument('-d','--data',dest='datasource',choices=['tiger','smultron','europarl'],required=True,help='define data source')
args = argpar.parse_args()

depconv = dependencyconverter.DependencyConverter(args.headsfile,punctuation=args.punctuation,coordination=args.coordination,ellipsis=args.ellipsis,datasource=args.datasource)
parser = xml.sax.make_parser()
parser.setContentHandler(Tiger2DepHandler(depconv,args.datasource))
parser.parse(args.inputfile)




