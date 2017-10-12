#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This file implements a node representation for nodes in a syntactic graph structure.
#
# author: Wolfgang Seeker
# 19/12/2012
#
    
class PSNode:
    def __init__( self ):
        self.sid = -1
        self.nid = -1
        self.form = None
        self.lemma = None
        self.pos = None
        self.morph = None
        self.head = -1
        self.label = None
        self.leaf = True
        self.origid = -1
        
    def __str__( self ):
        morphstr = '|'.join(map(lambda (x,y): '%s=%s' % (x,y.lower()), self.morph)) if self.morph else '_'
        id = ( self.sid != -1 and str(self.sid)+'_'+str(self.nid) or str(self.nid) )
        return '\t'.join([id,unicode(self.form),unicode(self.lemma),'_',self.pos,'_',morphstr,'_',str(self.head),'_',self.label,'_','_'])

