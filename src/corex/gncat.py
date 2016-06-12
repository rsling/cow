# -*- coding: utf-8 -*-

# Class for reading GermaNet categories and annotating
# words/doms with them.

import os.path
import sys
import glob
from lxml import etree as ET

class GNCategorizer:
    """A class that reads GermaNet XML and provides category annotations"""

    def __init__(self, dirname):

        # Create XML file list.
        indir = dirname + '/*.xml'
        infiles = glob.glob(indir)
        if len(infiles) < 1:
            raise Exception('No XML files found in GermaNet directory.')

        # Fill the dictionary.
        self.gn_mapping = dict()
        for f in infiles:
            # Read files. Takes a few seconds.
            tree = ET.parse(f)
            for lexunit in tree.findall('.//*lexUnit'):

                # Get the synset and then info from it:
                synset = lexunit.find('..')
                pos = synset.get('category')[0]
                classs = synset.get('class')
                lemma = lexunit.find('./orthForm').text
                ident = lemma.lower() + '_' + pos

                if ident in self.gn_mapping:
                    self.gn_mapping[ident].add(classs)
                else:
                    self.gn_mapping[ident] = set()
                    self.gn_mapping[ident].add(classs)
        
    def query(self, lemma, pos):
        query = lemma.lower() + '_' + pos.lower()
        if query in self.gn_mapping:
            return self.gn_mapping[query]
        else:
            return None

    def annotate(self, dom, xpath = './/*token', lemma = './lemma', pos = './pos'):
        for t in dom.findall(xpath):
            p = t.find(pos).text.lower()
            
            if p[0] in ['a', 'n', 'v']:
                p=p[0]
                l = t.find(lemma).text.lower()

                #print(self.query(l, p))

