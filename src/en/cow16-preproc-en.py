# -*- coding: utf-8 -*-

# Preprocesses ENCOW14 version for COW16 transformation.

import argparse
import os.path
import sys
import gzip
import re

CHUNK_TAGS = set(['<adjc>', '</adjc>', '<advc>', '</advc>', '<conjc>', '</conjc>', '<intj>', '</intj>', '<lst>', '</lst>', '<nc>', '</nc>', '<pc>', '</pc>', '<prt>', '</prt>', '<vc>', '</vc>'])


def entity_to_character(s):
  r = s.replace('&quot;', '"').replace('&apos;', "'").replace('&lt;', '<').replace('&gt;', '>')
  r = r.replace('&amp;', '&')
  return r

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='input ENCOW14 file')
    parser.add_argument('outfile', help='output file name')
    parser.add_argument("--erase", action='store_true', help="erase outout files if present")
    args = parser.parse_args()

    # Check input files.
    infiles = [args.infile]
    for fn in infiles:
        if not os.path.exists(fn):
            sys.exit("Input file does not exist: " + fn)

    # Check (potentially erase) output files.
    ofn_skel = args.outfile
    outfiles = [ofn_skel]
    for fn in outfiles:
        if fn is not None and os.path.exists(fn):
            if args.erase:
                try:
                    os.remove(fn)
                except:
                    sys.exit("Cannot delete pre-existing output file: " + fn)
            else:
                sys.exit("Output file already exists: " + fn)

    outfile_skel = gzip.open(ofn_skel, 'wb')

    insentence = False   # state variable: Reading sentence or not.

    # Read line by line.
    f = gzip.open(args.infile)
    linecount = 0
    for l in f:
      l = l.decode('utf-8')
      l = l.strip()

      linecount = linecount + 1

      if not l or (l[0] == u"\u200B"):
        continue

      if (insentence):

        # Cleanup an old processing error.
        l = l.replace('&amp;gt;', '&gt;').replace('&amp;lt;', '&lt;')

        # First, decide whether sentence ends.
        if (l == '</s>'):
          insentence = False
          outfile_skel.write('</s>\n')
        
        # Sentence does not end and this is a tag.
        elif (l[0] == '<'):
          outfile_skel.write(l.encode('utf-8') + '\n')

        # Normal token line.
        else:
          annos = l.split('\t')
          if not len(annos) == 3:
            print  'l. ' + str(linecount) + ': ' + l.encode('utf-8')
            continue
          outfile_skel.write('\t'.join( [annos[0]] + [annos[1]] + ['|' + annos[2] + '|'] ).encode('utf-8') + '\n')

      # NOT in sentence.
      else:

        # Outside sentences, we clean up the skeleton.
        if (not l[0] == '<'):
          outfile_skel.write( l.split('\t')[0].encode('utf-8') + '\t_\t|\n' )
        
        # And we remove the chunk tags.
        elif (not l.split('\t')[0] in CHUNK_TAGS):
            outfile_skel.write(l.encode('utf-8') + '\n')

        # Change mode if this line starts a sentence.
        if (l == '<s>'):
          insentence = True

    f.close()
    outfile_skel.close()

if __name__ == "__main__":
    main()






