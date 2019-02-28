#!/usr/bin/python
#
#
# Extracts all document IDs (id="...") from a COW-XML file,
# writes them to an index file named after the input file.
#
# Pass: COW-XML file (gzip).

import sys
import os 
import gzip
import re
from argparse import ArgumentParser

def arguments():
    parser = ArgumentParser(description="""Extracts all document IDs (id="...") from a COW-XML file, writes them to an index file named after the input file. Output format (TAB separated): id    file_basename   start_pos   length""")
    parser.add_argument('infile', help='COW-XML infile: utf-8 encoded, gzipped')

    args = parser.parse_args()
    return(args)




def main():
    args = arguments()

    prefix = os.path.split(args.infile.replace('.xml.gz', ''))[-1]
    outfilename = args.infile.replace('.xml.gz', '') + ".index"


    if os.path.exists(outfilename):
        sys.exit("File exists: %s" %outfilename)
    if not os.path.exists(args.infile):
        sys.exit("Input file %s does not exist" %args.infile)


    startpos = 0
    lcount = 0

    with gzip.open(args.infile) as in_h, open(outfilename, 'w') as out_h:
        for line in in_h:
            lcount += 1
            line = line.decode('utf-8')
            if line.startswith(u'</doc>'):
                out_h.write(docid + "\t" + prefix + "\t" + str(startpos) + "\t" + str(in_h.tell() - startpos) + "\n")
                startpos = in_h.tell()
            elif line.startswith('<doc '): 
                m = re.search(u'id="([^ "]+)"', line)
                if m:
                    docid = m.group(1)
                else:
                    raise Exception("Line " + str(lcount) + ": found no 'id' attribute")



if __name__ == "__main__":
    main()

