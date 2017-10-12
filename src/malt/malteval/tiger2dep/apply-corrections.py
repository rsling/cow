#!/bin/python
# -*- coding: utf-8 -*-

#
# This file implements a class that applies changes to the annotation of the TiGer corpus.
# Note that the conversion only works with version 2.1 of the TiGer corpus, release August 2007.
#
# author: Wolfgang Seeker
# 19/12/2012
#

import bs4
import fileinput

class TigerXMLFormatter:
    def __init__( self, indent = '  ' ):
        self.indent = indent

    def format_sentence( self, sentence ):
        fstrs = []
        fstrs.append('<s id="%s">' % (sentence['id'],))
        discontinuous = ' discontinuous="true"' if sentence.graph.has_attr('discontinuous') else ''
        fstrs.append('%s<graph root="%s"%s>' % (self.indent,sentence.graph['root'],discontinuous))
        fstrs.append('%s<terminals>' % (2*self.indent,))
        for terminal in sentence.find_all('t'):
            has_secedge = '' if terminal.find('secedge') else ' /'
            
            word = ' word="%s"' % (terminal['word']).replace('&','&amp;').replace('"','&quot;').replace('">','&quot;&gt;').replace('<','&lt;') if terminal.has_key('word') else ''
            lemma = ' lemma="%s"' % (terminal['lemma'].replace('&','&amp;')) if terminal.has_key('lemma') else ''
            pos = ' pos="%s"' % (terminal['pos']) if terminal.has_key('pos') else ''
            morph = ' morph="%s"' % (terminal['morph']) if terminal.has_key('morph') else ''

            case = ' case="%s"' % (terminal['case']) if terminal.has_key('case') else ''
            number = ' number="%s"' % (terminal['number']) if terminal.has_key('number') else ''
            gender = ' gender="%s"' % (terminal['gender']) if terminal.has_key('gender') else ''
            person = ' person="%s"' % (terminal['person']) if terminal.has_key('person') else ''
            degree = ' degree="%s"' % (terminal['degree']) if terminal.has_key('degree') else ''
            tense = ' tense="%s"' % (terminal['tense']) if terminal.has_key('tense') else ''
            mood = ' mood="%s"' % (terminal['mood']) if terminal.has_key('mood') else ''

            type_ = ' type="%s"' % (terminal['type']) if terminal.has_key('type') else ''

            fstrs.append('%s<t id="%s"%s%s%s%s%s%s%s%s%s%s%s%s%s>'
                         % (3*self.indent,terminal['id'],word,lemma,pos,morph,case,number,gender,person,degree,tense,mood,type_,has_secedge))
            if has_secedge == '':
                for secedge in terminal.find_all('secedge'):
                    fstrs.append('%s<secedge label="%s" idref="%s" />' % (4*self.indent,secedge['label'],secedge['idref']))
                fstrs.append('%s</t>' % (3*self.indent,))            
        fstrs.append('%s</terminals>' % (2*self.indent,))
        nonterminals = sentence.find_all('nt')
        if nonterminals:
            fstrs.append('%s<nonterminals>' % (2*self.indent,))
            for nonterminal in nonterminals:
                fstrs.append('%s<nt id="%s" cat="%s">' % (3*self.indent,nonterminal['id'],nonterminal['cat']))
                for edge in nonterminal.find_all('edge'):
                    fstrs.append('%s<edge label="%s" idref="%s" />' % (4*self.indent,edge['label'],edge['idref']))
                for secedge in nonterminal.find_all('secedge'):
                    fstrs.append('%s<secedge label="%s" idref="%s" />' % (4*self.indent,secedge['label'],secedge['idref']))
                fstrs.append('%s</nt>' % (3*self.indent,))
            fstrs.append('%s</nonterminals>' % (2*self.indent,))
        else:
            fstrs.append('%s<nonterminals />' % (2*self.indent,))
        fstrs.append('%s</graph>' % (1*self.indent,))
        fstrs.append('</s>')

        return '\n'.join(fstrs)

    def format_header( header ):
        pass


class Changes:
    def __init__( self, files ):
        self.attachments = {}
        self.poscat = {}
        self.edgelabels = {}
        self.secedgelabels = {}
        self.lemmata = {}
        self.deletenodes = {}
        self.deletesecedges = {}
        self.morphology = {}
        self.newnodes = {}
        self.newsecedges = {}
        self.newforms = {}
        self.newroots = {}
        
        for line in fileinput.input(files,openhook=fileinput.hook_encoded('iso-8859-1')):
            line = line.partition('%')[0].strip().replace("'",'') # to get rid of prolog comments and string markers
            if line.startswith('correct_attachment'):
                rule = self.make_rule(line)
                self.add_rule(rule,self.attachments)
            elif line.startswith('correct_poscat'):
                rule = self.make_rule(line)
                self.add_rule(rule,self.poscat)
            elif line.startswith('correct_edge_label'):
                rule = self.make_rule(line)
                self.add_rule(rule,self.edgelabels)
            elif line.startswith('correct_lemma'):
                rule = self.make_rule(line)
                self.add_rule(rule,self.lemmata)
            elif line.startswith('correct_surf'):
                rule = self.make_rule(line)
                self.add_rule(rule,self.newforms)
            elif line.startswith('correct_secedge_label'):
                fields = line.partition('(')[2].rpartition(')')[0].split(',')
                rule = tuple([fields[0],fields[1],','.join(fields[2:])])
                self.add_rule(rule,self.secedgelabels)
            elif line.startswith('unnecessary_node'):
                fields = line.partition('(')[2].rpartition(')')[0].split(',')
                fields.append('')
                rule = tuple(fields)
                self.add_rule(rule,self.deletenodes)
            elif line.startswith('unnecessary_secedge'):
                rule = self.make_rule(line)
                self.add_rule(rule,self.deletesecedges)
            elif line.startswith('new_root'):
                fields = line.partition('(')[2].rpartition(')')[0].split(',')
                fields.append('')
                rule = tuple(fields)
                self.add_rule(rule,self.newroots)
            elif line.startswith('correct_morph'):
                fields = line.partition('(')[2].rpartition(')')[0].split(',')
                rule = tuple([fields[0],fields[1],','.join(fields[2:])[1:-1]])
                self.add_rule(rule,self.morphology)
            elif line.startswith('additional_node'):
                newnodestr = line.partition('(')[2].rpartition(')')[0]
                if newnodestr.startswith('node'):
                    fields = newnodestr.partition('(')[2].rpartition(')')[0].split(',')
                    rule = tuple([fields[0],fields[1],','.join(fields)])
                    self.add_rule(rule,self.newnodes)
                if newnodestr.startswith('secondary'):
                    fields = newnodestr.partition('(')[2].rpartition(')')[0].split(',')
                    rule = tuple([fields[0],fields[1],','.join(fields)])
                    self.add_rule(rule,self.newsecedges)

        self.morphcombinations = { 'ART' : ['case','number','gender'],
                                   'APPRART' : ['case','number','gender'],
                                   'ADJA' : ['degree','case','number','gender'],
                                   'ADJD' : ['degree'],
                                   'NE' : ['case','number','gender'],
                                   'NN' : ['case','number','gender'],
                                   'PDAT' : ['case','number','gender'],
                                   'PDS' : ['case','number','gender'],
                                   'PIAT' : ['case','number','gender'],
                                   'PIS' : ['case','number','gender'],
                                   'PPER' : ['person','case','number','gender'],
                                   'PPOSAT' : ['case','number','gender'],
                                   'PPOSS' : ['case','number','gender'],
                                   'PRELAT' : ['case','number','gender'],
                                   'PRELS' : ['case','number','gender'],
                                   'PRF' : ['person','case','number'],
                                   'PWAT' : ['case','number','gender'],
                                   'PWS' : ['case','number','gender'],
                                   'VVFIN' : ['number','person','tense','mood'] }

    def apply_changes( self, sentence, corpus ):
        sid = sentence['id'][1:].partition('_')[0] # example: 's3_501' -> '3'
        # introduce new nodes
        for _,nid,newnode in self.newnodes.get(sid,[]):
            fields = newnode.split(',')
            nodeid = self.make_id(sid,fields[1])
            headid = self.make_id(sid,fields[2])
            new_node = corpus.new_tag('nt',id=nodeid, cat=fields[6].upper())
            sentence.find('nonterminals').append(new_node)
            new_edge = corpus.new_tag('edge',label=fields[5].upper(),idref=nodeid)
            sentence.find('nt',id=headid).append(new_edge)
            
        for _,nid,newsecedge in self.newsecedges.get(sid,[]):
            fields = newsecedge.split(',')
            nodeid = self.make_id(sid,fields[1])
            headid = self.make_id(sid,fields[2])
            parent = 't' if int(fields[1]) < 500 else 'nt'
            new_edge = corpus.new_tag('secedge',label=fields[3].upper(),idref=headid)
            sentence.find(parent,id=nodeid).append(new_edge)
        
        # correct attachments
        for _,nid,newhead in self.attachments.get(sid,[]):
            headid = self.make_id(sid,newhead)
            nodeid = self.make_id(sid,nid)
            old_edge = sentence.find('edge',idref=nodeid)
            new_label = old_edge['label'] if old_edge else '--'
            new_edge = corpus.new_tag('edge',label=new_label,idref=nodeid)
            sentence.find('nt',id=headid).append(new_edge)
            if old_edge: old_edge.decompose()
            
        # delete nodes
        for _,nid,_ in self.deletenodes.get(sid,[]):
            nodeid = self.make_id(sid,nid)
            sentence.find('nt',id=nodeid).decompose()
            if not sentence.find('graph',root=nodeid):
                sentence.find('edge',idref=nodeid).decompose()
            
        for _,nid,hid in self.deletesecedges.get(sid,[]):
            nodeid = self.make_id(sid,nid)
            headid = self.make_id(sid,hid)
            name = 't' if int(nid) < 500 else 'nt'
            sentence.find(name,id=nodeid).find('secedge',idref=headid).decompose()
            
        # new root
        for _,nid,_ in self.newroots.get(sid,[]):
            headid = self.make_id(sid,nid)
            sentence.find('graph')['root'] = self.make_id(sid,nid)
            old_edge = sentence.find('edge',idref=headid)
            if old_edge: old_edge.decompose()
            
        # correct all other stuff
        for _,nid,newpos in self.poscat.get(sid,[]):
            nodeid = self.make_id(sid,nid)
            name = 't' if int(nid) < 500 else 'nt'
            attr = 'pos' if int(nid) < 500 else 'cat'
            sentence.find(name,id=nodeid)[attr] = newpos.upper()

        for _,nid,newword in self.newforms.get(sid,[]):
            nodeid = self.make_id(sid,nid)
            sentence.find('t',id=nodeid)['word'] = newword
        
        for _,nid,newlemma in self.lemmata.get(sid,[]):
            nodeid = self.make_id(sid,nid)
            sentence.find('t',id=nodeid)['lemma'] = newlemma

        for _,nid,newlabel in self.edgelabels.get(sid,[]):
            nodeid = self.make_id(sid,nid)
            sentence.find('edge',idref=nodeid)['label'] = newlabel.upper()

        for _,nid,headnewlabel in self.secedgelabels.get(sid,[]):
            fields = headnewlabel.split(',')
            nodeid = self.make_id(sid,nid)
            headid = self.make_id(sid,fields[0])
            name = 't' if int(nid) < 500 else 'nt'
            sentence.find(name,id=nodeid).find('secedge',idref=headid)['label'] = fields[1].upper()
            
        for _,nid,morphstr in self.morphology.get(sid,[]):
            nodeid = self.make_id(sid,nid)
            node = sentence.find('t',id=nodeid)
            # delete previous annotation, than annotate new one
            for attr in ['case','number','gender','mood','tense','degree','person']:
                node[attr] = '--'
            if morphstr:
                for attr,val in map(lambda x: tuple(x.split('-')),morphstr.split(',')):
                    node[attr] = val.capitalize()
                # fix morph attribute accordingly
                node['morph'] = self.make_morph(node)

                
    def make_rule( self, line ):
        return tuple(line.partition('(')[2].rpartition(')')[0].replace("'",'').split(','))

    def add_rule( self, rule, dict ):
        if rule[0] not in dict:
            dict[rule[0]] = []
        dict[rule[0]].append(rule)

    def make_id( self, sid, nid ):
        nodeid = nid if nid != '-1' else 'VROOT'
        return 's%s_%s' % (sid,nodeid)

    def make_morph( self, node ):
        return '.'.join(map(lambda x: node[x], self.morphcombinations[node['pos']]))


        

### MAIN ###
if __name__ == "__main__":
    import sys
    import codecs

    encoding = 'iso-8859-1' if sys.argv[1] == 'latin1' else 'utf-8'

    sys.stdout = codecs.getwriter(encoding)(sys.stdout)

    corpus = bs4.BeautifulSoup(open(sys.argv[2],'r'),'lxml')

    # copy the header
    for line in codecs.open(sys.argv[2],'r',encoding):
        if line.strip().startswith('<body>'):
            break
        print line,
    
    # apply changes to sentences
    print '<body>'
    changes = Changes(sys.argv[3:])
    f = TigerXMLFormatter()
    for sentence in corpus.find_all('s'):        
        print >> sys.stderr, 'applying correction to sentence', sentence['id'][1:].partition('_')[0], '\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b',
        changes.apply_changes(sentence,corpus)
        print f.format_sentence(sentence)
    print >> sys.stderr
    print '</body>'
    print '</corpus>'
        
    
