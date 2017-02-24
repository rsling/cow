#!/usr/bin/python
# -*- coding: utf-8 -*-

# This tool reads a COW-XML corpus and runs the COReX feature
# extraxction "algorithm". Output is an annotated COW XML
# corpus.

# If test.xml is a DECOW14A (sample) file, try calling:
# python corex.py test.xml test_out.xml --annotations "word,pos,lemma,ne,morph"

import argparse
import os.path
import sys
import gzip
import logging

from lxml import etree as ET
from corexreader import outify, CORexReader as CX
from gncat import GNCategorizer as GN
from corex_basic import annotate_basic#, annotate_lexicon
from passive_corex import passive, passive_enable_color
from perfect_corex import perfect, perfect_enable_color


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='COW-XML input file')
    parser.add_argument('outfile', help='output file name')
    parser.add_argument("--erase", action='store_true', help="erase outout files if present")
    parser.add_argument('--annotations', type=str, help='comma-separated names for token annotations')
    parser.add_argument("--minlength", type=int, default=-1, help="minimal token length of documents")
    parser.add_argument("--germanet", type=str, help="directory path to GermaNet XML files")
    parser.add_argument("--nopassive", action="store_true", help="skip passive detection/counting")
    parser.add_argument("--noperfect", action="store_true", help="skip perfect detection/counting")
    parser.add_argument("--verbose", action="store_true", help="emit debug messages")
    parser.add_argument("--color", action="store_true", help="use TTY colors for verbose mode")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
        if args.color:
          perfect_enable_color()
          passive_enable_color()


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

    # Split annos passed on CL.
    annos = list()
    if args.annotations:
        annos = args.annotations.split(',')

    # Open out file.
    outf = gzip.open(fn_out, 'w')

    # Create corpus iterator. 
    corpus_in = CX(fn_in, annos=annos)

    # Create the annotator classes.
    if args.germanet:
        Gn = GN(args.germanet)

    # Annotate the documents.
    for doc in corpus_in:

        # Minimal length filter.
        if len(doc.findall('.//*token')) < args.minlength:
            continue
        
        # All simple counts and more.
        annotate_basic(doc)

        # count passives:
        if not args.nopassive:
	    passive(doc)

	# count perfect and pluperfect:
        if not args.noperfect:
	    perfect(doc)

        # Do the GermaNet semantic classes annotation.
        if args.germanet:
            Gn.annotate(doc)


        # Save the (potentially modified) DOM.
        flat = outify(doc)
        outf.write(flat + '\n' )
      

if __name__ == "__main__":
    main()
