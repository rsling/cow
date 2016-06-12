# -*- coding: utf-8 -*-

# COW + IDS topic modeling helpers based on gensim.

import re
from lxml import etree as ET


def entify(s):
    return s.replace('"', '&quot;').replace("'", '&apos;')

def outify(doc):
    """prepares a doc DOM for export to a COW XML file"""

    flat = ET.tostring(flatten_tokens(doc), encoding='utf-8').replace('>','>\n')
    # clean up whitespace at beginning/end of line
    listed = flat.split('\n')
    # remove blank lines and '<token>' markings
    listed = [y for y in [x.strip() for x in listed] if y and not y=='<token>' and not y=='</token>']
    # make " and ' conform
    listed = [entify(x) if not x.startswith('<') else x for x in listed]
    flat = ('\n').join(listed)
    return flat

def flatten_tokens(dom):
    """Flattens <token> nodes in DOM"""

    # Modify the DOM, flattening <token>s
    for node in dom.findall('.//*token'):

        # Flatten the children of <token> with \t
        flat = "\t".join(node.itertext())

        # Clean the children
        for child in list(node):
            node.remove(child)

        node.text = flat +  '\n'

    # Flatten DOM and return:
    return dom


class CORexReader:
    """A class that reads COW-XML document by document and represents it as DOM"""


    def __init__(self, filename, annos = list()):
        self.infilename = filename
        self.infile = open(self.infilename)
        self.annos = annos
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
                        self.sappend(l, b)
                        break
                else:
                    raise StopIteration
            
            # If doc start was found, buffer until end of doc.
            while True:
                l = self.sread()
                
                if l:
                    self.sappend(l, b)
                    if self.docend.match(l):
                        break
                else:
                    raise StopIteration
            

            # There was a document. Increase counter.
            self.count = self.count+1

            b = ' '.join(b)

            b = ET.fromstring(b)
            return b

    # FUNCTIONALITY

    # Read a line and make ready to use.
    def sread(self):
        return self.infile.readline().decode('utf-8').strip()

    # Instead of messing with ET later, we XMLify the token stream
    # while reading.
    def sappend(self, line, lisst):
        if line[0] == '<':
            lisst.append(line)
        else:
            lline = line.split('\t')
            if not len(lline) == len(self.annos):
                print "Line with incorrect no. of fileds: " + line + "\n"
            else:
                outl = list()
                outl.append('<token>')
                for i in range(0, len(lline), 1):
                    outl.append('<' + self.annos[i] + '>')
                    outl.append(lline[i])
                    outl.append('</' + self.annos[i] + '>')
                outl.append('</token>')
                lisst.append("".join(outl))




