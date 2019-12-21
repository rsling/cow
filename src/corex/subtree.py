#!/usr/bin/python

from anytree import Node, RenderTree, find, AnyNode


class SubtreeBuilder():
    """Utility class for rebuilding dependency (sub)trees from a list of (word, annos) tuples"""
    def __init__(self, depindpos=0, dephdpos=1, deprelpos=2):
        self.depindpos = int(depindpos)
        self.dephdpos = int(dephdpos)
        self.deprelpos = int(deprelpos)
        self.nodelist = None
        self.subtree_nodes = None
        self.topnode = None
        self.target_depind = None
        self.targetnode = None



    def convert(self, raw_tokens_annos):
        l = [(i[0],i[1].split("\t")) for i in raw_tokens_annos]
        return(l)

    def mk_nodes(self, token_attrs):
    # create  nodes; add dependency information under separate attributes, and all other annotations under another attribute
        return([AnyNode(word=token, depind=attrs[self.depindpos], dephd=attrs[self.dephdpos], deprel=attrs[self.deprelpos], annos="/".join([a for num, a in enumerate(attrs) if not num in [self.depindpos, self.dephdpos, self.deprelpos]])) for (token, attrs) in token_attrs])

    def build_tree(self, nodelist):
        for n in nodelist:
            children = [x for x in nodelist if x.dephd == n.depind]
            n.children = children

    def get_targetnode(self, target_depind, rootnode):
        return(find(rootnode, lambda node: node.depind == target_depind))

    def getdepind(self, n):
        return int(n.depind)


    def get_dependents(self, targetnode, topnode):
        return(sorted([n for n in self.targetnode.descendants], key=self.getdepind))


    def get_words(self, linear="all"):
        words = None
        if linear == "all":
            words = [n.word for n in self.subtree_nodes]
        elif linear == "right":
            words = [n.word for n in self.subtree_nodes if int(n.depind) > int(self.target_depind)]
        elif linear == "left":
            words = [n.word for n in self.subtree_nodes if int(n.depind) < int(self.target_depind)]
        return(words)


    def get_deprel(self, linear):
        if linear == "right":
            deprel = next((n.deprel for n in self.subtree_nodes if int(n.depind) > int(self.target_depind) and n.dephd == self.target_depind), "")
        if linear == "left":
            deprel = next((n.deprel for n in self.subtree_nodes if int(n.depind) < int(self.target_depind) and n.dephd == self.target_depind), "")
        return(deprel)

    
    def get_annos(self, linear, positions=[]):
        positions = [int(i) for i in positions]
        
        if linear == "right":
            annos = [a for n in self.subtree_nodes for num, a in enumerate(n.annos.split("/")) if int(n.depind) > int(self.target_depind) and num in positions]   
 
        if linear == "left":
            annos = [a for n in self.subtree_nodes for num, a in enumerate(n.annos.split("/")) if int(n.depind) < int(self.target_depind) and num in positions]         
        return(annos)





    def update(self, tokens_annos):
        self.topnode = None
        tokens_annos = self.convert(tokens_annos)
        self.nodelist = sorted(self.mk_nodes(tokens_annos), key=self.getdepind)
        self.build_tree(self.nodelist)
        self.topnode = AnyNode(word="TOP", depind="TOP", deprel="_", dephd="_")
        self.topnode.children = [n for n in self.nodelist if n.dephd == "0"]


    def get_subtree(self, target_depind):
        self.subtree_nodes = None
        self.target_depind = target_depind
        self.targetnode = self.get_targetnode(self.target_depind, self.topnode)
        self.subtree_nodes = [n for n in sorted(self.get_dependents(self.targetnode, self.topnode), key=self.getdepind) if n.deprel != "--"]


    def render_fulltree(self):
        print("full tree: ")
        print(RenderTree(self.topnode))

    def render_subtree(self):
        print("subtree: ")
        print(RenderTree(self.targetnode))


