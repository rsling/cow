#!/usr/bin/python
# -*- coding: utf-8 -*-

# This tool reads a COW-XML corpus and runs the COReX feature
# extraxction "algorithm". Output is an annotated COW XML
# corpus.

# If test.xml is a DECOW14A (sample) file, try calling:
# python corex.py test.xml test_out.xml --annotations "word,pos,lemma,ne,morph"

import argparse
import os.path
import sys
from corexreader import CORexReader as CX
import codecs


def words_to_string(parent):
	b = []
	for word in parent.findall('.//*word'):
		b.append(word.text)
	line = " ".join(b) #+ "\n"
	return(line)

def get_dominating_simpx(element):
	while True:
		parent = element.getparent()
		if parent.tag in ['simpx', 'rsimpx']:
			break
		elif parent.tag == '<s>':
			break
		else:
			element = parent
	return(parent)

def get_dominating_lk(v,vcparent):
	verbose(v,['\n\t\tclause: ', "'", words_to_string(vcparent), "'"])
		# check if we have a non-verb-final structure (left bracket in verb-final clauses is "c", not "lk"):
#	lks =  vcparent.findall('.//lk') # 
	lks =  vcparent.findall('lk')
	if lks:
		if lks > 0:
			lks = lks[0]
	else:
		lks = []
		verbose(v,['\n\t\tverb-final clause','\n\t\t\t\t=====> NO PASSIVE'])
	return(lks)

	
def get_wpl(enclosing_element):
	words = enclosing_element.findall('.//*word')			
	pos =  enclosing_element.findall('.//*pos')
	lemmas =  enclosing_element.findall('.//*lemma')
	wwords = [w.text for w in words]
	ppos = [p.text for p in pos]
  	llemmas = [l.text for l in lemmas]
	return(wwords,ppos,llemmas)


def verbose(verbosearg,sentencelist):
	if verbosearg == True:
		for s in sentencelist:
			sys.stderr.write(s) 


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='COW-XML input file')
    parser.add_argument('outfile', help='output file name')
    parser.add_argument('--annotations', type=str, help='comma-separated names for token annotations')
    parser.add_argument('--erase', action='store_true', help='erase existing output files')
    parser.add_argument('--verbose', action='store_true', help='print debugging output')

    args = parser.parse_args()
    
    v = args.verbose
 
    fn_out = args.outfile
    fn_in = args.infile

    # Check input files.
    infiles = [fn_in]
    for fn in infiles:
        if not os.path.exists(fn):
            sys.exit("Input file does not exist: " + fn)

    # Check (potentially erase) output files.
    outfiles = [fn_out]
    for fn in outfiles:
        if fn is not None and os.path.exists(fn):
            if args.erase:
                try:
                    os.remove(fn)
                except:
                    sys.exit("Cannot delete pre-existing output file: " + fn)
            else:
                sys.exit("Output file already exists: " + fn)

    # Split annos
    annos = list()
    if args.annotations:
        annos = args.annotations.split(',')

    # Create corpus iterator. 
    corpus_in = CX(fn_in, annos=annos)

    # open output file:
    outfile = codecs.open(fn_out, 'w', 'utf-8')
 
   
    for doc in corpus_in:
    	passcounter = 0
	perfcounter = 0
	for s in doc.iter('s'):
	    verbose(v,["\n=========\n", words_to_string(s)])
	    sent_passcounter = 0
	    sent_perfcounter = 0
            for vc in s.findall('.//vc'): # vc is not always a direct child of simpx (e.g. in coordination)
		verbose(v,["\n\tVC: ", "'", words_to_string(vc),"'"])
		(wwords,ppos,llemmas) = get_wpl(vc)
		# most general case: verbal complex contains a participle (could be perfekt or passive)
		participles = [word for word in ppos if word == 'VVPP']
        	if len(participles) > 0:
		#	print(participles)
			has_passive = False
			verbose(v,['\n\t\tpast participle found'])
		# check if verbal complex ends in a passive auxiliary:
#		    	if llemmas[-1] == "werden" and ppos[-1].startswith('VA'):
				# werden doesn't have to be the last word in the complex
                                # ("dass die Eizelle befructet werden kann")
			for participle in participles:
				if "werden" in llemmas:
					for i in range(0,len(llemmas)):
						if llemmas[i] == "werden" and ppos[i].startswith('VA'):
							has_passive = True 
							sent_passcounter += 1
							verbose(v,['\n\t\tpassive aux found in verbal complex','\n\t\t\t=====> PASSIVE'])
							break
				break
     		# get the left bracket of the immediately dominating <simplex>-element:
			if has_passive == False:
					verbose(v,['\n\t\tno passive aux found in verbal complex'])
					for participle in participles:
						vcparent = get_dominating_simpx(vc)
						lks = get_dominating_lk(v,vcparent)
                                                if lks == []:
							verbose(v,['\n\t\t\tno left bracket filled with a verb in this clause',' \n\t\t\t=====> NO PASSIVE'])
						else:
							for lk in lks:
								(wwords,ppos,llemmas) = get_wpl(lk)
								verbose(v,['\n\t\t\tleft bracket: ', "'" , " ".join(wwords) , "'"])
	
		# check for passive axuiliary:
								if llemmas[0] == 'werden' and ppos[0].startswith('VA'):
									verbose(v,["\n\t\t\tfound finite form: '", wwords[0] , "'", "\n\t\t\t\t=====> PASSIVE"])
									sent_passcounter += 1	
																		
								else:
									verbose(v, ["\n\t\t\tfound no finite form of 'werden'", "\n\t\t\t\t=====> NO PASSIVE"])
			
		else:
			verbose(v, ["\n\t\tfound no past participle in verbal complex","\n\t\t\t=====> NO PASSIVE\n"])

	
	    line = words_to_string(s).strip()
	    line = line + "\t" + str(sent_passcounter)	
	    outfile.write(line + "\n")
	    passcounter = passcounter + sent_passcounter	
	doc.set('crx_pass', str(passcounter))
	sys.stderr.write("\nPassives in doc: " + str(passcounter) + "\n")	
	   
if __name__ == "__main__":
    main()
