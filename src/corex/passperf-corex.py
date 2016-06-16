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
#import xml.etree.ElementTree as ET
#import lxml.etree as ET
import codecs


def words_to_string(parent):
	b = []
	for word in parent.findall('.//*word'):
		b.append(word.text)
	line = " ".join(b) + "\n"
	return(line)

def get_dominating_simpx(element):
	while True:
		parent = element.getparent()
		if parent.tag == 'simpx':
			break
		elif parent.tag == '<s>':
			break
		else:
			element = parent
	return(parent)
	

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='COW-XML input file')
    parser.add_argument('outfile', help='output file name')
    parser.add_argument('--annotations', type=str, help='comma-separated names for token annotations')
    #parser.add_argument("--minlength", type=int, default=-1, help="minimal token length of documents")
    parser.add_argument('--erase', action='store_true', help='erase existing output files')
    parser.add_argument('--verbose', action='store_true', help='print debugging output')

    args = parser.parse_args()
 
 
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
 
    # This is just an example output.
    for doc in corpus_in:
    	passcounter = 0
	perfcounter = 0
	#tree = ET.ElementTree(doc)
	#tree.write("thedoc.xml")
	for s in doc.iter('s'):
	    if args.verbose == True:
		sys.stderr.write("\n=========\n")
		line = words_to_string(s)
		sys.stderr.write(line.strip())
	    sent_passcounter = 0
	    sent_perfcounter = 0	
	  #  for simpx in s.iter('simpx'):
            for vc in s.findall('.//vc'): # vc is not always a direct child of simpx (e.g. in coordination)
		if args.verbose == True:
			sys.stderr.write("\n\tVC: ")
			sys.stderr.write(words_to_string(vc))
	    	words = vc.findall('.//*word')			
	    	pos =  vc.findall('.//*pos')
	    	lemmas =  vc.findall('.//*lemma')
	    	wwords = [w.text for w in words]
	    	ppos = [p.text for p in pos]
  	    	llemmas = [l.text for l in lemmas]
#		print(ppos) # debug
		# most general case: verbal complex contains a participle (could be perfekt or passive)
        	if 'VVPP' in ppos:
			has_passive = False
			if args.verbose == True:
				sys.stderr.write('\t\t past participle found')
		# check if verbal complex ends in a passive auxiliary:
		    	if llemmas[-1] == "werden" and ppos[-1].startswith('VA'):
				# we have to keep track of this: if there is another form of 'werden' in
				# lk, thenthis must be future-werden, not the passive auxiliary 
				has_passive = True 
				sent_passcounter += 1
				if args.verbose == True:
					sys.stderr.write('\n\t\t passive aux found in verbal complex\n\t\t\t=====> PASSIVE')
#                       	line = words_to_string(s)
#				outfile.write("1 pass:\t")
#				outfile.write(line)                                                                            			
		# check if verbal complex ends in a 'haben' or 'sein' auxiliary:
	    		if llemmas[-1] in ["haben", "sein"] and ppos[-1].startswith('VA'):
				sent_perfcounter += 1
				if args.verbose == True:
					sys.stderr.write('\n\t\t perfect aux found in verbal complex\n\t\t\t=====> PERFEKT')
			
     		# get the left bracket of the immediately dominating <simplex>-element:
			else:
				if args.verbose == True:
					sys.stderr.write('\n\t\t no aux found in verbal complex')
				vcparent = get_dominating_simpx(vc)
			#	print("Parent: "),
			#	print(vcparent)
				if vcparent.tag == 'simpx': 
				    for lk in vcparent.findall('lk'):
					for vxfin in lk.findall('vxfin'):
						words = vxfin.findall('.//*word')
					    	pos =  vxfin.findall('.//*pos')
	    					lemmas =  vxfin.findall('.//*lemma')
						wwords = [w.text for w in words]
	    					ppos = [p.text for p in pos]
  	    					llemmas = [l.text for l in lemmas]
		# check for passive axuiliary:
						if llemmas[0] == 'werden' and ppos[0].startswith('VA'):
							if has_passive == False:
								sent_passcounter += 1					
							#for word in simpx.findall('.//*word'):                                                                                    				print(word.text),
		# check for perfect auxiliaries:
						if llemmas[0] in ['haben', 'sein'] and ppos[0].startswith('VA'):
							sent_perfcounter += 1
#							
		else:
		# Ersatzinfinitiv: no participle at all in the verb cluster; instead infinitive of a modal verb: 
			#if 'VMINF' in ppos:
			if ppos[-1] == 'VMINF':
		# Oberfeldumstellung: "weil er das hat essen müssen"
				if llemmas[0] == 'haben':
					sent_perfcounter += 1
				else:
		# get the left bracket of the immediately dominating <simplex>-element:
					vcparent = get_dominating_simpx(vc)
					if vcparent.tag == 'simpx': 
						for lk in vcparent.findall('lk'):
							for vxfin in lk.findall('vxfin'):
								words = vxfin.findall('.//*word')
					    			pos =  vxfin.findall('.//*pos')
	    							lemmas =  vxfin.findall('.//*lemma')
								wwords = [w.text for w in words]
	    							ppos = [p.text for p in pos]
  	    							llemmas = [l.text for l in lemmas]
		
							if llemmas[0]  == 'haben' and ppos[0].startswith('VAFIN'):
								sent_perfcounter += 1
		 # ACIs: er hat sie singen hören, er hat sie singen hören müssen, weil er sie singen hören hat, weil er sie hat singen hören 
#			elif len(ppos) >= 2 and ppos[0] in ['VVINF', 'VMINF'] and ppos[1] == 'VVINF' and llemmas[1] in ['lassen', 'sehen', 'hören', 'spüren', 'fühlen', 'lehren']:
#				if llemmas[-1] == 'haben' and ppos[-1] == 'VAFIN'  


	
	    line = words_to_string(s).strip()
	    line = line + "\t" + str(sent_passcounter) + "\t" + str(sent_perfcounter)	
	 #   print(line.strip().encode('utf-8'))	
	    outfile.write(line + "\n")
	    passcounter = passcounter + sent_passcounter
	    perfcounter = perfcounter + sent_perfcounter	
	doc.set('passive', str(passcounter))
	doc.set('perfect', str(perfcounter))
#	sys.stderr.write(str(passcounter) + "\t")
#	sys.stderr.write(str(perfcounter) + "\n")
#	tree = ET.ElementTree(doc)
#	tree.write("thedoc.xml")
				



			

 
	   
if __name__ == "__main__":
    main()
