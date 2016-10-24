# -*- coding: utf-8 -*-

import os.path
import sys
import re
import argparse
import gzip

from langid import LanguageIdentifier, model
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

def entity_convert(s):
    s = s.replace(u'&lt;', '<')
    s = s.replace(u'&gt;', '>')
    s = s.replace(u'&quot;', '"')
    s = s.replace(u'&apos;', "'")
    s = s.replace(u'&amp;', '&')
    return s


def known_prop(toklist, wordlist):
    toksel = [i for i in toklist if len(i) >1]
    if len(toksel) > 0:
	return float(sum([(w.lower() in wordlist) for w in toksel])) / float(len(toksel))
    else:
	return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="input file (gzipped XML)")
    parser.add_argument("outfile", help="output file (gzipped XML)")
    parser.add_argument("language", help="target language; <s> structures in other languages are un-sentenced", type=str)
    parser.add_argument("token", help="column in VRT layout with token information", type=int)
    parser.add_argument("confidence", help="LangID condifence below which heuristics kicks in", type=float)
    parser.add_argument("dictionary", help="word list for heuristics", type=str)
    parser.add_argument("threshold", help="threshold (proportion) for heuristics", type=float)
    parser.add_argument("--debug", action='store_true', dest="debug", help="print debug output (accept/reject with metrics)")
    args = parser.parse_args()

    if not os.path.exists(args.infile):
	sys.exit("Input file does not exist.")
    if os.path.exists(args.outfile):
	sys.exit("Output file exists!")

    sstart = re.compile(r'^<s>$')
    sstop = re.compile(r'^</s>$')
    xmlline = re.compile(r'^<.+>$')

    inhandle = gzip.open(args.infile)
    outhandle = gzip.open(args.outfile, 'wb')

    words = set()
    for l in gzip.open(args.dictionary):
	l = l.decode('utf-8').strip()
	words.add(l)

    c = 0
    readmode = 0
    sbuffer = []
    for l in inhandle:
	l = l.decode('utf-8').strip()

	if readmode == 0:

	    if sstart.match(l):
		readmode = 1
	    else:
		outhandle.write(l.encode('utf-8') + "\n")

	elif readmode == 1:
	    if not sstop.match(l):
		sbuffer.append(l)

	    else:
		toklist = []

		for t in sbuffer:
		    if not xmlline.match(t):
			decomp = t.split('\t')
			toklist.append(decomp[args.token-1])

		lang, conf = identifier.classify(entity_convert(" ".join(toklist)))
		known_word_prop = known_prop(toklist, words)
		
		if (lang == args.language and conf >= args.confidence) or known_word_prop > args.threshold:
		    outhandle.write((u'<s>\n' + "\n".join(sbuffer) + u'\n</s>\n').encode('utf-8'))
		    if args.debug: print entity_convert(u'KEEP ' + lang + ' @ ' + str(conf) + ' / ' + str(known_prop(toklist, words)) + ' : ' + ' '.join(toklist) + '\n').encode('utf-8')
		else:
		    outhandle.write(("\n".join(sbuffer) + u'\n').encode('utf-8'))
		    if args.debug: print entity_convert(u'DELE ' + lang + ' @ ' + str(conf) + ' / ' + str(known_prop(toklist, words)) + ' : ' + ' '.join(toklist) + '\n').encode('utf-8')

		# Flush buffer for next round and start NOT reading in <s>.
		sbuffer = []
		readmode = 0

	c = c + 1

    inhandle.close()
    outhandle.close()

if __name__ == "__main__":
    main()

