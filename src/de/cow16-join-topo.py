# -*- coding: utf-8 -*-

# This merges topological parses into <s> regions in a master COW XML file.

import gzip
import re
import argparse
import os.path
import sys



class Eof(Exception):
  pass

def advance(h):
  l = h.readline()
  if not l:
    raise Eof
  l = l.decode('utf-8')
  l = l.strip()
  return l


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("xml", help="master COW XML file (gzip)")
  parser.add_argument("parse", help="transformed parser output file (gzip)")
  parser.add_argument("output", help="output file (gzip)")
  parser.add_argument("--erase", action='store_true', help="erase outout files if present")
  args = parser.parse_args()

  # Check input files.
  infiles = [args.xml, args.parse]
  for fn in infiles:
      if not os.path.exists(fn):
          sys.exit("Input file does not exist: " + fn)

  # Check (potentially erase) output files.
  outfiles = [args.output]
  for fn in outfiles:
    if fn is not None and os.path.exists(fn):
      if args.erase:
        try:
          os.remove(fn)
        except:
          sys.exit("Cannot delete pre-existing output file: " + fn)
      else:
        sys.exit("Output file already exists: " + fn)

  fh_xml = gzip.open(args.xml, 'r')
  fh_parse = gzip.open(args.parse, 'r')
  fh_out = gzip.open(args.output, 'wb')

  in_sentence = False 
  i = -1
  j = -1
  while True:

    # Within a sentence, the parse file is advanced first to see whether XML must be written.
    if in_sentence:
      try:
        p = advance(fh_parse)
      except Eof:
        sys.exit('Premature end of parse file at line: ' + str(j+1))
      j = j + 1
      if re.match(r'^</s>', p):
        in_sentence = False

        # Also consume line from XML file and see whether sentence starts there, too.
        if not re.match(r'^</s>', advance(fh_xml)):
          sys.exit('Sentence not closed in XML for lines ' + str(i) + ',' + str(j))
        i = i + 1
        fh_out.write(u'</s>\n')

      # In-sentence handling when sentence does NOT end.
      else:

        # Tags from parse are just written, XML line NOT consumed.
        if re.match(r'^<', p):
          fh_out.write(p.encode('utf-8') + '\n')
        else:
          l = advance(fh_xml)
          i = i +1
          ls = l.split('\t')
          ps = p.split('\t')
          if ls[0] == ps[0] or ls[0] == ps[0].replace('[', '(') or ls[0] == ps[0].replace(']', ')'):
            fh_out.write(l.encode('utf-8') + '\n')
          else:
            mess = 'Inconsistent annotations in lines ' + str(i) + ',' + str(j) + ':' + l.encode('utf-8') + ':' + p.encode('utf-8')
            sys.exit(mess)
        

    # Just write line from XML and check whether new sentence begins.
    else:
      try:
        l = advance(fh_xml)
        i = i + 1
      except Eof:
        break

      if re.match(r'^<s( |>)', l):
        in_sentence = True

        # Also consume line from parse file and see whether sentence starts there, too.
        try:
          p = advance(fh_parse)
        except Eof:
          sys.exit('Premature end of parse file at line: ' + str(j+1))
        j = j + 1
        if not re.match(r'^<s( |>)', p):
          sys.exit('Sentence not opened in parse for line ' + str(i) + ',' + str(j))

      # Regardless of whether a sentence started, write this line to output.
      fh_out.write(l.encode('utf-8') + '\n')

  fh_xml.close()
  fh_parse.close()
  fh_out.close()

if __name__ == "__main__":
    main()


