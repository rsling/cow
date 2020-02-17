#!/usr/bin/python
# -*- coding: utf-8 -*-

# This tool reads a COW-XML corpus and runs the COReX feature
# extraxction "algorithm". Output is an annotated COW XML
# corpus.


import argparse
import os.path
import sys
import gzip
import logging
import re

from lxml import etree as ET
from gncat import GNCategorizer as GN

from corex_reader import outify, CORexReader as CX
from corex_basic import annotate_basic, FloatHandler #, annotate_lexicon
from corex_passive import passive, passive_enable_color
from corex_perfect import perfect, perfect_enable_color
from corex_dep import depgrams
from corex_additional import annotate_additional
from corex_csv import write_csv



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='COW-XML input file')
    parser.add_argument('outfile', help='output file name')
    parser.add_argument("--erase", action='store_true', help="erase outout files if present")
    parser.add_argument('--digits', type=int, default=3, help='round floats to this number of decimal digits')
    parser.add_argument('--annotations', type=str, help='comma-separated names for token annotations')
    parser.add_argument("--minlength", type=int, default=-1, help="minimal token length of documents")
    parser.add_argument("--germanet", type=str, help="directory path to GermaNet XML files")
    parser.add_argument("--nobasic", action="store_true", help="skip basic COReX feature counting")
    parser.add_argument("--nopassive", action="store_true", help="skip passive detection/counting")
    parser.add_argument("--noperfect", action="store_true", help="skip perfect detection/counting")
    parser.add_argument("--nodep", action="store_true", help="skip depgram counting")
    parser.add_argument("--csv", help="write raw counts to csv file")
    parser.add_argument("--noadditional", action="store_true", help="skip counting additional features")
    parser.add_argument("--verbose", action="store_true", help="emit debug messages")
    parser.add_argument("--color", action="store_true", help="use TTY colors for verbose mode")
    parser.add_argument("--sentencefilter", help="attr='val' filter for sentences (features in any sentences not satisfying <s ... attr='val' ...> will NOT be counted)")


    args = parser.parse_args()


    if args.verbose:
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
        print("verbose!")
        if args.color:
          perfect_enable_color()
          passive_enable_color()


    fn_out = args.outfile
    fn_in = args.infile
    if args.csv:
        fn_csv = args.csv

    # Check input files.
    infiles = [fn_in]
    for fn in infiles:
        if not os.path.exists(fn):
            sys.exit("Input file does not exist: " + fn)

    # Check (potentially erase) output files.
    outfiles = [fn_out]
    if args.csv:
        outfiles.append(fn_csv)

    for fn in outfiles:
        if fn is not None and os.path.exists(fn):
            if args.erase:
                try:
                    os.remove(fn)
                except:
                    sys.exit("Cannot delete pre-existing output file: " + fn)
            else:
                sys.exit("Output file already exists: " + fn)

    # Create float to string handler.
    fh = FloatHandler(args.digits)

    # Split annos passed on CL.
    annos = list()
    if args.annotations:
        annos = args.annotations.split(',')

    # Get attr-val filter for sentences:
    if args.sentencefilter:
        if re.match(u'''[a-zA-Z][a-zA-Z0-9]*=(?P<quote>['"])[^"'><]+(?P=quote)''' , args.sentencefilter.strip()):
            args.sentencefilter = '@' + args.sentencefilter.strip()
        else:
            msg = u"Invalid sentence filter: " + args.sentencefilter.strip()
            sys.exit(msg.encode('utf-8'))
    else:
        args.sentencefilter = ""


    # Open out file.
    if fn_out.endswith('.gz'):
        outf = gzip.open(fn_out, 'w')
    else:
        outf = open(fn_out, 'w')

    # Open csv file:
    if args.csv:
        if fn_csv.endswith('.gz'):
            csv_h = gzip.open(fn_csv, 'w')
        else:
            csv_h = open(fn_csv, 'w')



    # Create corpus iterator.
    corpus_in = CX(fn_in, annos=annos)

    # Create the annotator classes.
    if args.germanet and not args.nogermanet:
        Gn = GN(args.germanet)

    # Annotate the documents.
    for doc in corpus_in:

        # Minimal length filter.
        if len(doc.findall('.//*token')) < args.minlength:
            continue

        # All simple counts and more.
        if not args.nobasic:
          annotate_basic(doc, fh, args.sentencefilter)

        # Count passives.
        if not args.nopassive:
            passive(doc, fh, args.sentencefilter)

        # Count perfect and pluperfect.
        if not args.noperfect:
            perfect(doc, fh, args.sentencefilter)

        # Count depgrams:
        if not args.nodep:
            depgrams(doc, fh, args.sentencefilter)

        # Additional counts:
        if not args.noadditional:
            annotate_additional(doc, fh, args.sentencefilter)


        # Do the GermaNet semantic classes annotation.
        if args.germanet:
            Gn.annotate(doc)

        # Save the (potentially modified) DOM.
        flat = outify(doc)
        outf.write(flat + '\n' )

        # write raw counts to csv-file
        # (raw counts converted back from normalized counts)
        if args.csv:
            write_csv(doc, csv_h)


    outf.close()
    if args.csv:
        csv_h.close()



if __name__ == "__main__":
    main()
