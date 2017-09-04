# -*- coding: utf-8 -*-

# Takes COW-XML and
# 1. Adds <s id="">
# 2. Guesses forum document.

import gzip
import regex as re
import argparse
import os.path
import sys

RE_FORUM=r'.*(?:forum|/board/|/threads/|showthread|/archive/(?:index.php/)?t-[0-9]+\.html|viewtopic|ftopic|/\?topic=|(?:/threads/[A-Za-z]+(?:-[A-Za-z]+)+\.[0-9]+/$)|/thread-[0-9]+\.html$|/topic/[0-9]+(?:-[A-Za-z]+)+|/t[0-9]+(?:-[A-Za-z]\+)+\.html)'


def entity_encode(s):
  s = s.replace('&', '&amp;')
  s = s.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
  return s


# Read from file handle h a COW-XML document.
# If eof, return None. Also detect forum status.
def get_next_document(h):
  while True:
    l = h.readline()
    if not l:
      doc = None
      break
    l = l.decode('utf-8').strip()
    if not l:
      continue
  
    if re.match(u'^<doc ', l, re.UNICODE):

      # Fix _unk_.
      l = re.sub(r'_unk_', 'unknown', l)

      # Forum detection.
      if re.match(RE_FORUM, l, re.UNICODE):
        l = re.sub(u'>$', r' forum="1">', l, re.UNICODE)
      else:
        l = re.sub(u'>$', r' forum="0">', l, re.UNICODE)

      # Host and tld extraction.
      l = re.sub(r'( url="https{0,1}://)([^/]+)\.([a-z]{2,4})(|/|%)([^"]*")', r'\1\2.\3\4\5 urldomain="\2.\3" tld="\3"', l)

      # Fix some known problems in doc attr values.
      l = re.sub(r'=" +"', r'="unknown"', l)          # fix: attr=" "
      l = re.sub(r'="([^"]+)\\" ', r'="\1" ', l)   # fix: attr="val\"

      doc = [l]
    else:
      doc = doc + [l]
      if re.match(u'^</doc>', l, re.UNICODE):
        break
  return doc


def lemma_strip(s):
  return s.strip('|').split('|')[0]


def sentence_proc(doc, blank):
  sentence_start = -1
  counter        = 1
  i              = 0
  in_title       = False
  in_keywords    = False
  current_bpv    = 0

  while i < len(doc)-1:

    # Check whether we are in non-sentence territory.
    if in_title and re.match(r'^<\/title>', doc[i]):
      in_title = False
    elif not in_title and re.match(r'^<title>$', doc[i]):
      in_title = True
    if in_keywords and re.match(r'^<\/keywords>', doc[i]):
      in_keywords = False
    elif not in_keywords and re.match(r'^<keywords>$', doc[i]):
      in_keywords = True

    # Check whether we need to update boilerplate class.
    divbpv = re.match('<div .*bpv="([^"]+)".*>', doc[i])
    if divbpv:
      current_bpv = float(divbpv.group(1))

    # Start new sentence.
    if re.match(r'^<s[> ]', doc[i]):
      sentence_start = i
      i = i +1

    # Process and write sentence ending here.
    elif re.match(r'</s>', doc[i]):
      tokenstream  = filter(lambda x: not re.match(r'^<', x), doc[sentence_start:i])
      tokenlist    = [x.split('\t')[0] for x in tokenstream]
      tokens       = " ".join(tokenlist)
      tokens_lower = tokens.lower()

      # Check minimal criteria for sentence-hood (forgotten in ESCOW quasi-pre-COW16).
      words      = [re.match(r'^\p{script=Latin}+$', t, re.UNICODE) is not None for t in tokenlist]
      wordcount  = sum(words)
      unsentence = in_title or in_keywords or wordcount < 3 or (wordcount < 5 and not re.match(r'^([.?!]{1,3}|[)"\'»]|&quot;|&apos;)', tokenlist[-1], re.UNICODE)) or current_bpv > 0.6



      if unsentence:
        doc = doc[0:sentence_start] + [x+blank for x in tokens.split(' ')] + doc[i+1:]

        # We need to fix the runnning index.
        i = sentence_start + len(tokenstream) - 1

      else:

        # Annotate sentence type.
        tags = [x.split('\t')[2] for x in tokenstream]
        if True in [re.match(r'^V.[ISM]', t) is not None for t in tags]:
          attr_type = u' type="finite"'
        elif True in [re.match(r'^V.[PGN]', t) is not None for t in tags]:
          attr_type = u' type="nonfinite"'
        else:
          attr_type = u' type="noverb"'

        # Add index to sentence tag (and sentence type info.
        doc[sentence_start] = '<s idx="' + str(counter) + '"' + attr_type + '>'
        counter = counter + 1
        i = i + 1

    # Neither sentence end nor beginning.
    else:
      i = i +1

  return doc


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("infile", help="COW-XML input file (gzip)")
  parser.add_argument("outfile", help="COW-XML output (gzip)")
  parser.add_argument("blank", help="comma-separated blanks to be used outside sentences")
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

  # Create real blank string.
  blank = '\t' + '\t'.join([a.strip() for a  in args.blank.split(',')])

  # Open file handles.
  fh_in = gzip.open(args.infile, 'r')
  fh_out = gzip.open(args.outfile, 'wb')

  while True:
    doc=get_next_document(fh_in) 
    if not doc:
      break

    # Process if doc was read.
    doc = sentence_proc(doc, blank)

    # Write doc
    for l in doc:
      fh_out.write(l.encode('utf-8') + '\n')
#      print(l.encode('utf-8'))

  # Close file handles.
  fh_in.close()
  fh_out.close()

if __name__ == "__main__":
    main()

