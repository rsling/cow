#! /usr/bin/python
# -*- coding: utf-8 -*- 

# This script reads in a corpus in COW-XML format (gzipped)
# and pretty-prints selected meta data from
# <doc ...> elements. Optionally, it the attribute 'id'
# is missing, it generates an identifier
# based on the value of <doc url="...">.
# Meta data (tsv) is written to metadatafile.
#
# pass: infile metadatafile (all .gz)
# option -i requires an outfilename.
#

import sys
import re
import hashlib
import codecs
import gzip
from corex_pp_metadata import prettyprint_docattributes
from argparse import ArgumentParser


def get_url(line):
#    print(line)
    attrval = re.search(u'url="[^"]+"', line).group()
#    print(attrval)
#    print(type(attrval))
    if attrval is not None:
        url = attrval.replace('url=' , '').replace('"' , '')
#        print(url)
        return(url)
    else:
        return(None)
  
    
def mk_docid(line): 
    url = get_url(line)
    if url is not None:
        docid = hashlib.sha1(url).hexdigest()
#        print(docid)
#        print(type(docid))
        return(docid)
    else:
        sys.stderr.write("\n No URL found. Line: " + line + "\n")
        sys.exit(1)


def add_docid(line, docid):
    id_attr = 'id="' + docid + '"'
    line = line.replace('>', (' ' + id_attr + '>'))
#    print(line)
#    print(type(line))
    return(line)


def main():
    parser = ArgumentParser()                                                                                         
    parser.add_argument('infile', help='COW xml input (gzipped)')                                                                  
    parser.add_argument('metadatafile', help='document meta data will be written here (gzipped)')  
    parser.add_argument('-o', '--outfile', nargs='?', help='add missing id-attributes write modified corpus to outfile')                                                                                             
    args = parser.parse_args()
       
    try:
        infile = gzip.open(args.infile, "r")
    except:
        sys.stderr.write("\n Input file not found.\n\n")
        sys.exit(1)
    
    metadatafile =  gzip.open(args.metadatafile, "w")
    
    if args.outfile:
        outfile = gzip.open(args.outfile, "w")


#    infile = open(sys.argv[1], "r")
#    outfile = open(sys.argv[2], "w")
#    metadatafile =  open(sys.argv[3], "w")


    doccounter = 0
    reference_attrsline = "" 
    
    for line in infile:

        line = line.decode('utf8')
        if line.startswith('<doc'):
            doccounter += 1
            if not ' id="' in line:
                docid = mk_docid(line)
                line = add_docid(line, docid)
            try:
                prettyprint_docattributes(line, metadatafile, reference_attrsline, doccounter)
            except IndexError:
                sys.exit(1)
#            docheadersfile.write(line)
#            print(line)
        if args.outfile:
            outfile.write(line.encode('utf8'))
    
    sys.stderr.write("\nTotal documents: " + str(doccounter) + "\n")
    infile.close()
    metadatafile.close()
    if args.outfile:
        outfile.close()


if __name__ == "__main__":
    main()


