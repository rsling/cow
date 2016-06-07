# -*- coding: utf-8 -*-

# COW + IDS topic modeling helpers based on gensim.

import re
import xml.etree.ElementTree as ET

class CORexReader:
    """A class that reads COW-XML document by document and represents it as DOM"""


    def __init__(self, filename):
        self.infilename = filename
        self.infile = open(self.infilename)

        self.count = 0

        self.docstart = re.compile(r'^<doc .+> *$')
        self.docend = re.compile(r'^</doc> *$')

    # ITERATOR STUFF

    def __iter__(self):
        return self

    def next(self):

        while True:
            # At first, document is empty.
            b = list()

            # Find doc start.
            while True: 
                l = self.sread()
                if l:
                    if self.docstart.match(l):
                        b.append(l)
                        break
                else:
                    raise StopIteration
            
            # If doc start was found, buffer until end of doc.
            while True:
                l = self.sread()
                
                if l:
                    b.append(l)
                    if self.docend.match(l):
                        break
                else:
                    raise StopIteration
            

            # There was a document. Increase counter.
            self.count = self.count+1

            b = ' '.join(b).encode('utf-8')
            b = ET.fromstring(b)
            return b

    # FUNCTIONALITY

    # Read a line and make ready to use.
    def sread(self):
        return self.infile.readline().decode('utf-8').strip()

