# -*- coding: utf-8 -*-

# This tool reads a COW-XML corpus and runs the COReX feature
# extraxction "algorithm". Output is an annotated COW XML
# corpus.

# If test.xml is a DECOW14A (sample) file, try calling:
# python corex.py test.xml test_out.xml --annotations "word,pos,lemma,ne,morph"

import argparse
import os.path
import sys
from corexreader import CORexReader as CX
#import xml.etree.ElementTree as ET
import lxml.etree as ET



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='COW-XML input file')
    parser.add_argument('outfile', help='output file name')
    parser.add_argument('--annotations', type=str, help='comma-separated names for token annotations')
    #parser.add_argument("--minlength", type=int, default=-1, help="minimal token length of documents")
    parser.add_argument('--erase', action='store_true', help='erase existing output files')

    args = parser.parse_args()

    fn_out = args.outfile
    fn_in = args.infile

    # Check input files.
    infiles = [fn_in]
    for fn in infiles:
        if not os.path.exists(fn):
            sys.exit("Input file does not exist: " + fn)

    # Check (potentially erase) output files.
    outfiles = [fn_out]
    for fn in outfiles:
        if fn is not None and os.path.exists(fn):
            if args.erase:
                try:
                    os.remove(fn)
                except:
                    sys.exit("Cannot delete pre-existing output file: " + fn)
            else:
                sys.exit("Output file already exists: " + fn)

    # Split annos
    annos = list()
    if args.annotations:
        annos = args.annotations.split(',')

    # Create corpus iterator. 
    corpus_in = CX(fn_in, annos=annos)

    # This is just an example output.
    for doc in corpus_in:
        for t in doc.findall('.//*word'):
            print t.text

if __name__ == "__main__":
    main()
