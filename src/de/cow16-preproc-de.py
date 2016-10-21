# -*- coding: utf-8 -*-

# Preprocesses IMS version for COW16 transformation.

import argparse
import os.path
import sys
import gzip
import re

def entity_encode(s):
  r = s.replace('&', '&amp;')
  r = r.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
  return r

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('infile', help='input DECOW14 IMS version file (gzip)')
  parser.add_argument('outfile', help='output file name (gzip)')
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

  # state variable: Reading sentence or not.
  insentence = False   
  
  # Read line by line.
  f = open(args.infile)

  for l in f:
    l = l.decode('utf-8')
    l = l.strip()

    if not l:
      continue

    if (insentence and (l == '</s>')):
      insentence = False
   
    # Conversion of lines.
    if (insentence and (not l[0] == '<')):
      annos = l.split('\t')

      # Keep SMOR morphology.
      if (annos[7] == '_'):
        morph = '|'
      else:
        morph = '|' + re.sub(r'[^|]+=', '', annos[7]) + '|'

      # Output.
      new_annos = [entity_encode(annos[1]), morph] + [annos[i] for i in [0,9,11]]
      outfile_skel.write('\t'.join(new_annos).encode('utf-8') + '\n')

    if (not insentence):

      # Outside sentences, we clean up the skeleton.
      if (not l[0] == '<'):
        l = l.split('\t')[0] + '\t|\t_\t_\t_'
      outfile_skel.write(l.encode('utf-8') + '\n')

      # Change mode if this line starts a sentence.
      if (l == '<s>'):
        insentence = True

  f.close()
  outfile_skel.close()

if __name__ == "__main__":
    main()
