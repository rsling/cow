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

    def annotate(self, dom, xpath = './/*token', lemma = './lemma', pos = './ttpos'):
        # Empty dict to store the cat => count mapping.
        sem_anno = dict()

        tokens = dom.findall(xpath)
        for t in tokens:
            p = t.find(pos).text.lower()
            
            # There are only annotations for V, A, N, so skip everything else.
            if p[0] in ['a', 'n', 'v']:
                sems = self.query(t.find(lemma).text.lower(), p[0])

                if sems:
                    sem_count = len(sems)
                    for sem in sems:
                        sem_pos = p.upper()[0] + '_' + sem
                        if sem_pos in sem_anno:
                            sem_anno[sem_pos] += 1/float(sem_count)
                        else:
                            sem_anno[sem_pos] = 1/float(sem_count)

        # Finally, convert all figures to per-thousand.
        token_count = len(tokens)
        for s in sem_anno:
            sem_anno[s] = sem_anno[s]/float(token_count)*1000

        dom.attrib['crx_sem'] = ','.join([':'.join([k,str(sem_anno[k])]) for k in sem_anno])
