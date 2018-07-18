# -*- coding: utf-8 -*-

# This merges topological parses into <s> regions in a master COW XML file.

import gzip
import re
import argparse
import os.path
import sys



class Eof(Exception):
  pass


def entity_encode(s):
  # s = s.replace('&', '&amp;')
  s = s.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
  return s


def advance(h, clean_topo = False):

  readlines = 0
  # This serves to clean topological parses from
  # XML input for DECOW16B/DECOW18 processing.
  while True:
    l = h.readline()
    readlines = readlines + 1
    if not l:
      raise Eof
    l = l.decode('utf-8')
    l = l.strip()
  
    # If we need to clean this line, just continue reading.
    if ( clean_topo
         and not re.search(r'^(?:[^<]|</{0,1}(?:doc|s|div|meta|title|dup)[ |>])', l) ):
      continue
    else:
      break

  return { 'line' : l, 'readlines' : readlines }


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("xml", help="master COW XML file (gzip)")
  parser.add_argument("parse", help="Cheung & Penn parser output file (gzip)")
  parser.add_argument("output", help="output file (gzip)")
  parser.add_argument("--cowtek18", action='store_true', help="use COWTek18 mode (discard old parses etc.)")
  parser.add_argument("--entitytolerant", action='store_true', help="ignore (but report) suspicious &amp; vs. & situations")
  parser.add_argument("--erase", action='store_true', help="erase output files if present")
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
  i = 0
  j = 0
  while True:

    # Within a sentence, the parse file is advanced first to see whether XML must be written.
    if in_sentence:
      try:
        _adv = advance(fh_parse)
      except Eof:
        sys.exit('Premature end of parse file at line: ' + str(j+1))
      p = _adv['line'] 
      j = j + _adv['readlines']

      if re.match(r'^</s>', p):
        in_sentence = False

        # Also consume line from XML file and see whether sentence starts there, too.
        _adv = advance(fh_xml, args.cowtek18) 
        if not re.match(r'^</s>', _adv['line']):
          sys.exit('Sentence not closed in XML for lines ' + str(i) + ',' + str(j))
        i = i + _adv['readlines']
        fh_out.write(u'</s>\n')

      # In-sentence handling when sentence does NOT end.
      else:

        # Tags from parse are just written, XML line NOT consumed.
        if re.match(r'^<.', p):
          fh_out.write(p.encode('utf-8') + '\n')
        else:
          _adv = advance(fh_xml, args.cowtek18)
          l = _adv['line']
          i = i + _adv['readlines']
          ls = l.split('\t')[0]
          if args.cowtek18:
            ps = entity_encode(p).split('\t')[0]
          else:
            ps = p.split('\t')[0]
          psx = ps.replace('[', '(').replace(']', ')')
          lsx = ls.replace('[', '(').replace(']', ')')
          if lsx == psx :
            fh_out.write(l.encode('utf-8') + '\n')
          elif args.entitytolerant and lsx.replace('&amp;', '&') == psx:
            sys.stderr.write('Suspicious &amp; vs. & situation in lines ' + str(i) + ',' + str(j) + ' (writing regardless b/o --entitytolerant)\n')
            fh_out.write(l.encode('utf-8') + '\n')
          else:
            mess = 'Inconsistent annotations in lines ' + str(i) + ',' + str(j) + ':\n' + l.encode('utf-8') + '\n' + p.encode('utf-8')
            sys.exit(mess)
        

    # Just write line from XML and check whether new sentence begins.
    else:
      try:
        _adv = advance(fh_xml, args.cowtek18)
        l = _adv['line']
        i = i + _adv['readlines']
      except Eof:
        break

      if re.match(r'^<s( |>)', l):
        in_sentence = True

        # Also consume line from parse file and see whether sentence starts there, too.
        try:
          _adv = advance(fh_parse)
        except Eof:
          sys.exit('Premature end of parse file at line: ' + str(j+1))
        p = _adv['line']
        j = j + _adv['readlines']
        if not re.match(r'^<s( |>)', p):
          sys.exit('Sentence not opened in parse for line ' + str(i) + ',' + str(j))

      # Regardless of whether a sentence started, write this line to output.
      fh_out.write(l.encode('utf-8') + '\n')

  fh_xml.close()
  fh_parse.close()
  fh_out.close()

if __name__ == "__main__":
    main()


