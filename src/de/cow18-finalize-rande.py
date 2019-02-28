# -*- coding: utf-8 -*-

# Takes COW-XML and
# 1. Adds <s id>
# 2. Guesses forum document.
# 3. Adds <s type>

import gzip
import re
import argparse
import os.path
import sys

RE_FORUM=r'.*(?:forum|/board/|/threads/|showthread|/archive/(?:index.php/)?t-[0-9]+\.html|viewtopic|ftopic|/\?topic=|(?:/threads/[A-Za-z]+(?:-[A-Za-z]+)+\.[0-9]+/$)|/thread-[0-9]+\.html$|/topic/[0-9]+(?:-[A-Za-z]+)+|/t[0-9]+(?:-[A-Za-z]\+)+\.html)'


def entity_encode(s):
  s = s.replace('&', '&amp;')
  s = s.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
  return s


def noskify(d, blank):
  i = 0
  in_sentence = False
  while i < len(d)-1:

    if not re.match(r'^<', d[i]):
      if in_sentence:
        fs = d[i].split('\t')
        lc = fs[0].lower()
        lemma_lc = fs[5].strip('|').split('|')[0].lower()
        if lc == '(unknown)':
          lempos = fs[0].lower() + '-' + fs[4]
        elif lc == '_':
          lempos = '_'
        else:
          lempos = lemma_lc + '-' + fs[4] 
        fs = fs + [lc, lemma_lc, lempos]
        d[i] = '\t'.join(fs)
      else:
        d[i] = d[i].split('\t')[0] + blank.decode('string-escape')

    if re.match('<s( |>)', d[i]):
      in_sentence = True
    elif re.match('</s>', d[i]):
      in_sentence = False

    i = i + 1
  return d


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

      # Removal of old QS annotation.
      l = re.sub(r' c_token=".+>$', r'>', l)

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


# Also puts running numbers on sentences.
def sentence_proc(doc, blank):
  sentence_start = -1
  counter = 1
  i = 0
  while i < len(doc)-1:

    # Start new sentence.
    if re.match(r'^<s( |>)', doc[i]):
      sentence_start = i
      i = i +1

    # Process and write sentence ending here.
    elif re.match(r'</s>', doc[i]):
      tokenstream = filter(lambda x: not re.match(r'^<', x), doc[sentence_start:i])
      tokens = " ".join([x.split('\t')[0] for x in tokenstream])
      tokens_lower = tokens.lower()

      # Check for "sentence type".
      tags = [x.split('\t')[4] for x in tokenstream]
      if set(tags).intersection(set(['VVFIN', 'VAFIN', 'VMFIN', 'VVIMP', 'VAIMP'])):
        attr_type = u' type="finite"'
      elif set(tags).intersection(set(['VVINF', 'VVIZU', 'VVPP', 'VAINF', 'VAPP', 'VMINF', 'VMPP'])):
        attr_type = u' type="nonfinite"'
      else:
        attr_type = u' type="noverb"'

      # Create extra dependency columns.
      tokenstream_mat = [tok.split('\t') for tok in tokenstream]
      for j in [idx for idx in range(sentence_start, i) if not re.match(r'^<', doc[idx])]:
        this_line = doc[j].split('\t')

        # First, fix incorrect _ to |.
        if this_line[7] == u'_':
          this_line[7] = u'|' 
        if this_line[3] == u'_':
          this_line[3] = u'|' 
        if this_line[8] == u'_':
          this_line[8] = u'|' 
        if this_line[9] == u'_':
          this_line[9] = u'|' 
        if this_line[14] == u'_':
          this_line[14] = u'|' 

        this_head = [lemma_strip(h[5])+'-'+this_line[12] for h in tokenstream_mat if h[10]==this_line[11]]
        this_deps = [lemma_strip(h[5])+'-'+h[12] for h in tokenstream_mat if h[11]==this_line[10]]
        this_head = '0-root' if len(this_head) < 1 else this_head[0]
        this_deps = '|' if len(this_deps) < 1 else '|' + '|'.join(this_deps) + '|'

        # Re-merge line and add dependency stuff.
        doc[j] = '\t'.join(this_line) + '\t' + this_head + '\t' + this_deps

      # Add index to sentence tag (and sentence type info.
      doc[sentence_start] = re.sub(r'> *$', r'', doc[sentence_start], re.UNICODE) + ' idx="' + str(counter) + '"' + attr_type + '>'
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
  parser.add_argument("blank", help="add this as dummy annotation outside <s/>")
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


  blank = args.blank.decode('utf-8').strip()

  # Open file handles.
  fh_in = gzip.open(args.infile, 'r')
  fh_out = gzip.open(args.outfile, 'wb')

  while True:
    doc=get_next_document(fh_in) 
    if not doc:
      break

    # Create NoSkE columns.
    noskify(doc, blank)

    # Process if doc was read.
    doc = sentence_proc(doc, blank)

    # Write doc
    for l in doc:
      fh_out.write(l.encode('utf-8') + '\n')

  # Close file handles.
  fh_in.close()
  fh_out.close()

if __name__ == "__main__":
    main()

