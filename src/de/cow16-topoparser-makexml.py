# -*- coding: utf-8 -*-

import sys
import re
import gzip
import argparse
import os


def entity_encode(s):
  s = s.replace('&','&amp;') 
  s = s.replace('"','&quot;').replace("'","&apos;").replace('<', '&lt;').replace('>', '&gt;')
  return s


def sattrify(line):
  r = ['<s>']
  stack = []
  for e in line:
    if e.startswith('('):
      tagname = e.lstrip('(').lower()
      optag = '<' + tagname + '>'
      r = r + [optag]
      stack.append(tagname) 
    elif e == ')':
      try:
        tagname = stack.pop()
        cltag = '</' + tagname + '>'
        r = r + [cltag]
      except IndexError as err:
        raise Exception('Pop from empty stack.')
    else:
      r = r + process_tokens(e)

  r = r + ['</s>']

  # Remove some useless markup.
  r = filter(lambda x: not re.match(r'<>|</>|<pseudo>|</pseudo>', x) , r)

  if len(stack) > 0:
    raise Exception("Stack not empty.")

  return r



def process_tokens(s):
  postokens = s.split('~#~ ~#~') 
  postokens = [e.replace('~#~','') for e in postokens]
  tokenposes = [e.split(' ')[1] for e in postokens]
  return(tokenposes)



def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('infile', help='parser input (gzip)')
  parser.add_argument('outfile', help='output file name (gzip)')
  parser.add_argument("--erase", action='store_true', help="erase outout files if present")
  args = parser.parse_args()

  # Check input files.
  infiles = [args.infile]
  for fn in infiles:
      if not os.path.exists(fn):
          sys.exit("Input file does not exist: " + fn)

  # Check (potentially erase) output files.
  outfiles = [args.outfile]
  for fn in outfiles:
      if fn is not None and os.path.exists(fn):
          if args.erase:
              try:
                  os.remove(fn)
              except:
                  sys.exit("Cannot delete pre-existing output file: " + fn)
          else:
              sys.exit("Output file already exists: " + fn)

  ifh = gzip.open(args.infile, 'r')
  ofh = gzip.open(args.outfile, 'wb')

  for line in ifh:
    line = line.decode('utf-8')
    line = line.strip()
  
    # If not a parse, just write to outfile OTL.
    if not line.startswith('('):
      ofh.write('\n'.join(line.split(' ')).encode('utf-8') + '\n')
 
    else:   
      line = entity_encode(line)
      line = re.sub(r'\(([^ ]+ (?:[^ )]+|\)))\)', r'~#~\g<1>~#~', line)
      line = re.split(r'(\([^()~]+|\) *(?=(?:[^~]|$)))', line)
      line = [e.strip() for e in line if not e == '']
      ofh.write('\n'.join(sattrify(line)).encode('utf-8') + '\n')

  ifh.close()
  ofh.close()


if __name__ == "__main__":
    main()
