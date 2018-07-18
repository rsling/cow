#!/usr/bin/python

import re
from lxml import etree as ET
from argparse import ArgumentParser
import gzip
import sys


class CowReader:
    """A class that reads COW-XML document by document"""

    def __init__(self, filename, infileencoding='utf-8'):
         # constructor accepts a filename or a handle of an already opened file;

        if type(filename) == file or type(filename) == gzip.GzipFile:                 
            self.infile = filename               
        elif type(filename) == str:
            if filename.endswith('.gz'):
                self.infile = gzip.open(filename)
                 # if filename is "-", read from stdin
            elif filename == "-":
                self.infile = sys.stdin
            else:
                self.infile = open(filename)
        self.infileencoding = infileencoding

        self.count = 0

        self.docstart = re.compile('<doc ')
        self.docend = re.compile('</doc>')

    # ITERATOR STUFF

    def __iter__(self):
        return self

    def next(self):

        # At first, document is empty.
        b = list()


        # Find doc start.
        while True:
            l = self.sread(self.infileencoding)
            if l:
                if self.docstart.match(l.lstrip()):
                    b.append(l)
                    break
            else:
                raise StopIteration

        # If doc start was found, buffer until end of doc.
        while True:
            l = self.sread(self.infileencoding)

            if l:
                b.append(l)
                if self.docend.match(l.lstrip()):
                    break
            else:
                raise StopIteration

        # There was a document. Increase counter.
        self.count = self.count+1

        return b



# Read a line and make ready to use.
    def sread(self,infileencoding):
        line = self.infile.readline().decode(self.infileencoding)
        if not re.match(u'^<(?:[a-z]+(?: [^>]*)?|/[a-z]+)>$', line):
            line = line.replace("&", "&amp;").replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", "&apos;")
        return(line)


   
def arguments():
    parser = ArgumentParser(description="Reads COW-XML, finds sentences (<s ...> ... </s>) that have no further XML-elements as children.")
    parser.add_argument('-i', '--infile', help='input file (gzip optional); if omitted, read from stdin')
    parser.add_argument('--idattr', help='identifier attribute of <doc ...> elements (default: "sigle"', default='sigle')
    parser.add_argument('--indexattr', help='index attribute of <s ...> elements')
    parser.add_argument('--type', help='only check sentences matching type="TYPE"')
    parser.add_argument('--complete', action='store_true', default=False, help='print summary for all documents (default: only broken documents)"')
    parser.add_argument('--dump', action='store_true', help='dump sentences without anootations')
    args = parser.parse_args()
    return(args)


def print_output(id, docHasPhrases, docHasCompletePhrases, noPhraseSentenceCount, noanno, indexattr):
    line = "\t".join([id, str(docHasPhrases), str(docHasCompletePhrases), str(noPhraseSentenceCount)])
    if indexattr:
        line = line + "\t" + ",".join(noanno)       
    print(line.encode('utf-8'))




def main():

    args = arguments()

    if args.infile is not None:
        if args.infile.endswith('.gz'):
            fh_in = gzip.open(args.infile)
        else:
            fh_in = open(args.infile)
    else:
        fh_in = sys.stdin


    myReader = CowReader(fh_in)

    totalDocs = 0
    partiallyBrokenDocs = 0
    totallyBrokenDocs = 0 

    header = "Doc-ID\tContains-some-annotation\tContains-complete-topo-annotation\t#Non-annotated sentences"
    if args.indexattr:
        header = header + "\t" + "s.idx"

    print(header)

    for doc in myReader:
        totalDocs += 1
        doc = "".join(doc)
        dom = ET.fromstring(doc)
        docid = dom.attrib[args.idattr]
        lastDocWithTopo = ""

        sentences = dom.findall('.//s')

        if args.type:
            sentences = [s for s in sentences if s.attrib["type"] == args.type]

        totalSentences = len(sentences)

        docHasPhrases = False
        docHasCompletePhrases = False

        noPhraseSentenceCount = 0
        noanno = list()

        for s in sentences:
            phrases = s.findall('.//*')
            if len(phrases) == 0:
                noPhraseSentenceCount += 1

                # Dump sentence.
                if args.dump:
                  sys.stderr.write('\n')
                  sys.stderr.write(docid + '\n')
                  sys.stderr.write(ET.tostring(s))
                  sys.stderr.write('\n')

                if args.indexattr:
                    noanno.append(str(s.attrib[args.indexattr]))
                
        if noPhraseSentenceCount > 0:
            if noPhraseSentenceCount == totalSentences:
                totallyBrokenDocs += 1
            else:
                partiallyBrokenDocs += 1
                docHasPhrases = True
        else:
            docHasPhrases = True
            docHasCompletePhrases  = True

        if len(noanno) == 0:
            noanno.append("-")


        if args.complete:
            print_output(docid, docHasPhrases, docHasCompletePhrases, noPhraseSentenceCount, noanno, args.indexattr)
        else:
            if not docHasPhrases or not docHasCompletePhrases:
                print_output(docid, docHasPhrases, docHasCompletePhrases, noPhraseSentenceCount, noanno, args.indexattr)



    sys.stderr.write("Total docs:\t" +  str(totalDocs) + "\n")
    sys.stderr.write("Partially broken docs (some but not all sentences missing annotation):\t" + str(partiallyBrokenDocs) + "\n")
    sys.stderr.write("Totally broken docs (all sentences missing annotation):\t" + str(totallyBrokenDocs) + "\n")


    if args.infile:
        fh_in.close()


   

if __name__ == '__main__':
    main()
