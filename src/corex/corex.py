# -*- coding: utf-8 -*-

# This tool reads a COW-XML corpus and runs the COReX feature
# extraxction "algorithm". Output is an annotated COW XML
# corpus.

# If test.xml is a DECOW14A (sample) file, try calling:
# python corex.py test.xml test_out.xml --annotations "word,pos,lemma,ne,morph"

import argparse
import os.path
import sys
from corexreader import flatten_tokens, CORexReader as CX
from lxml import etree as ET


def entify(s):
    s = s.replace('"', '&quot;')
    s = s.replace("'", '&apos;')
    return s

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='COW-XML input file')
    parser.add_argument('outfile', help='output file name')
    parser.add_argument("--erase", action='store_true', help="erase outout files if present")
    parser.add_argument('--annotations', type=str, help='comma-separated names for token annotations')
    #parser.add_argument("--minlength", type=int, default=-1, help="minimal token length of documents")
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

    # open out file
    outf = open(fn_out, 'w')

    # Create corpus iterator. 
    corpus_in = CX(fn_in, annos=annos)

    for doc in corpus_in:
        # Here, do what you want with this DOM...
        print type(doc)
        # Save the (potentially modified) DOM:
        flat = outify(doc)
        outf.write(flat + '\n' )

if __name__ == "__main__":
    main()
