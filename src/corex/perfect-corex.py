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
from corexreader import outify
import codecs
import re


sein_part_re = re.compile('.*ge(gangen|fallen|laufen|flogen|wachsen|fahren|reist|schritten|geblieben|sprungen|kommen|blieben|drungen|wichen|stiegen|worden|stehen|taucht|storben|rutscht|rannt)')

sein_part_restdic = {u'geboren': '', u'gelungen': '', u'verhungert': '', u'zusammengebrochen': '', u'verklungen': '', u'passiert': '', u'weggezogen': '', u'fehlgeschlagen': '', u'geschehen': '', u'verreist': '', u'geflohen': '', u'gesto\xdfen': '', u'gewandert': '', u'begegnet': '', u'verschmolzen': '', u'abgek\xfchlt': '', u'versunken': '', u'eingeschlafen': '', u'gestrandet': '', u'abgebogen': '', u'misslungen': '', u'explodiert': '', u'gekrochen': '', u'ausgetrocknet': '', u'ausgetreten': '', u'worden': '', u'zerfallen': '', u'abgehauen': '', u'gest\xfcrzt': '', u'abgewandert': '', u'geplatzt': '', u'ertrunken': '', u'erschienen': '', u'erwachsen': '', u'verschwunden': '', u'widerfahren': '', u'zerbrochen': '', u'eingetreten': '', u'gestartet': '', u'verstrichen': '', u'entkommen': '', u'zugesto\xdfen': '', u'verblieben': '', u'gelandet': '', u'gefolgt': '', u'abgest\xfcrzt': '', u'aufgesessen': '', u'geschl\xfcpft': '', u'entwachsen': '', u'abgebrannt': '', u'geraten': '', u'umgezogen': '', u'eingeschlagen': '', u'bekommen': '', u'geklettert': '', u'gereift': '', u'dagewesen': '', u'gewesen': '', u'auferstanden': '', u'zur\xfcckgetreten': '', u'gekippt': '', u'vergangen': '', u'eingebrochen': '', u'geschwommen': '', u'gelangt': '', u'erschrocken': '', u'eingest\xfcrzt': '', u'geschmolzen': '', u'verflogen': '', u'hervorgetreten': '', u'mutiert': '', u'verheilt': '', u'unterlaufen': '', u'ergangen': '', u'beigetreten': '', u'ausgezogen': '', u'ausgewandert': '', u'erwacht': '', u'aufgestanden': '', u'eingewandert': '', u'erfolgt': '', u'gescheitert': '', u'aufgewacht': '', u'gefl\xfcchtet': '', u'entsprungen': '', u'\xfcberlaufen': '', u'zugezogen': '', u'angetreten': '', u'gestolpert': '', u'eingeflossen': '', u'entstanden': '', u'gegl\xfcckt': '', u'gestanden': '', u'abgeklungen': '', u'angeschwollen': '', u'entgangen': '', u'geschrumpft': '', u'gesunken': '', u'zerrissen': '', u'verfallen': '', u'aufgetreten': '', u'ausgebrochen': '', u'verkommen': '', u'verstorben': '', u'abgezogen': '', u'erloschen': '', u'ausgeschieden': '', u'durchgebrannt': '', u'verungl\xfcckt': '', u'abgesunken': ''}

oberfeld_re = re.compile('VAFIN(?: V.INF)+')

ersatzinfinitives_dict = {u'sehen': '', u'hören': '', u'fühlen': '', u'lassen': '', u'wollen': '', u'müssen': '', u'dürfen': '', u'sollen': '', u'können': '', u'mögen': ''} # more verbs here? 

def words_to_string(parent):
	b = []
	for word in parent.findall('.//*word'):
		b.append(word.text)
	line = " ".join(b) #+ "\n"
	return(line)


def get_dominating_X(element):
	while True:
		parent = element.getparent()
		if parent.tag in ['simpx', 'rsimpx', 'fkonj', 'fkoord']:
			break
		elif parent.tag == '<s>':
			break
		else:
			element = parent
#        sys.stderr.write("\nDominating element: " + parent.tag + "\n") # debug
	return(parent)



def get_dominating_lk(v,vc,logfile):
	# check if we have a non-verb-final structure (left bracket in verb-final clauses is "c", not "lk")
	current = vc
        lks = []
        while True:
		parent = get_dominating_X(current)
		verbose(v,['\n\t\t\t\tLooking for LK in clause: ', "'", words_to_string(parent), "'", " (", parent.tag, ")"], logfile)
#              	lks = parent.findall('lk')
		lks =  parent.findall('.//lk')
		tags = [i.tag for i in lks]
		verbose(v,["\nLKS: ", ", ".join(tags)], logfile)
		if len(lks) > 0:
			verbose(v,['\n\t\t\t\tFound LK in clause: ', "'", words_to_string(parent), "'"], logfile)
			break
                else:
			if parent.tag.endswith('simpx'):
				break
			else:
				current = parent
	return(lks)


	
def get_wplpm(enclosing_element):
	words = enclosing_element.findall('.//*word')			
	ttpos =  enclosing_element.findall('.//*ttpos')
	lemmas =  enclosing_element.findall('.//*lemma')
	mpos =  enclosing_element.findall('.//*mpos')
	morph =  enclosing_element.findall('.//*morph')

	wwords = [w.text for w in words]
	ttttpos = [p.text for p in ttpos]
  	llemmas = [l.text for l in lemmas]
       	mmpos = [p.text for p in mpos]
	mmorph =  [m.text for m in morph]

	return(wwords,ttttpos,llemmas,mmpos,mmorph)


def verbose(verbosearg,sentencelist,logfile): # debugging; remove logfile later
	if verbosearg == True:
		for s in sentencelist:
		#	sys.stderr.write(s.encode('utf-8'))
			logfile.write(s)


def haben_pres(candidate):
	if candidate.lower() in [u'habe', u'hab', u'hast', u'habest', u'hat', u'haben', u'habt', u'habet']:
		return(True)
	else:
		return(False)

def haben_past(candidate):
	if candidate.lower() in  [u'hatte', u'hätte', u'hattest', u'hättest', u'hatten', u'hätten', u'hattet', u'hättet']: 
		return(True)
	else:
		return(False)


def sein_pres(candidate):
	if candidate.lower() in [u'bin', u'bist', u'ist', u'sind', u'seid', u'sind', u'sei', u'seist', u'seiest', u'seien', u'seiet']:
		return(True)
	else:
		return(False)

def sein_past(candidate):
	if candidate.lower() in  [u'war', u'warst', u'waren', u'wart', u'wäre', u'wärst', u'wär', u'wären', u'wärt', u'wäret']: 
		return(True)
	else:
		return(False)


def participles2tokens(wwords, ttttpos, llemmas, mmpos):
# returns tokens tagged as 'V.PP'
	part_dict = {u'VVPP': '', u'VAPP':''} # plus VMPP?
	words_pos_lemmas_mmpos = zip(wwords, ttttpos, llemmas, mmpos)
	# sometimes, Marmot gets the pos tag V.PP correct when TreeTagger thinks its V.FIN:
	participletokens = [word for (word, pos, lemma, mpos) in words_pos_lemmas_mmpos if (pos in part_dict or mpos in part_dict)]
	return(participletokens)



def infinitives2tokens(wwords, ttttpos):
# returns (a list of) tokens tagged as infinitive:
	words_pos = zip(wwords, ttttpos)
	infdict =  {u'VVINF': '', u'VAINF': '', u'VMINF': ''}
	infinitivetokens = [word for (word, pos) in words_pos if pos in infdict]
	return(infinitivetokens)


def ersatzinfinitives_candidates(wwords, ttttpos, llemmas):
	# returns (a list of) tokens tagged as 'VVFIN' or 'VMINF' and that can form ersatzinfinitives:
	words_pos_lemmas = zip(wwords, ttttpos, llemmas)
	ersatzposlist = [u'VVINF', u'VMINF'] 
	ersatzcandidatetokens = [word for (word, pos, lemma) in words_pos_lemmas if pos in ersatzposlist and lemma in ersatzinfinitives_dict]
	return(ersatzcandidatetokens)


def count_perfect(doc, outfile, logfile): # outfile and logfile are for debugging and testing; remove later
	v = False
	perfcounter = 0
	pluperfcounter = 0
	for s in doc.iter('s'):
	    verbose(v,["\n=========\n", words_to_string(s)], logfile)
	    sent_perfcounter = 0
	    sent_pluperfcounter = 0
            for vc in s.findall('.//vc'): # vc is not always a direct child of simpx (e.g. in coordination)
		verbose(v,["\n\tVC: ", "'", words_to_string(vc),"'"], logfile)
		(wwords,ttttpos,llemmas,mmpos,mmorph) = get_wplpm(vc)
		# most general case: verbal complex contains a participle
		participles = participles2tokens(wwords, ttttpos, llemmas, mmpos)
		infinitives = infinitives2tokens(wwords, ttttpos)
		ersatzcandidates = ersatzinfinitives_candidates(wwords, ttttpos, llemmas)
		participles_and_ersatzinfs = participles + ersatzcandidates

		verbose(v,["\n\tAll tokens in this VC: ", ", ".join(wwords)], logfile)
		verbose(v,["\n\tAll tags in this VC: ", ", ".join(ttttpos)], logfile)
		verbose(v,["\n\tAll lemmas in this VC: ", ", ".join(llemmas)], logfile)
		verbose(v,["\n\tAll participles in this VC: ", ", ".join(participles)], logfile)
		verbose(v,["\n\tAll infinitives in this VC: ", ", ".join(infinitives)], logfile)
		verbose(v,["\n\tAll potential ersatzinfinitives: ", ", ".join(ersatzcandidates)], logfile)

		if len(participles_and_ersatzinfs) > 0:
			verbose(v,['\n\t\tpast participle(s) and infinitives found: ', ', '.join(participles_and_ersatzinfs)], logfile)
                # check if verbal complex ends with a perfect aux:   
			verbose(v,["\nParticiplelist before processing first participle: ", ", ".join(participles_and_ersatzinfs)], logfile)
			donelist = []
			for participle in participles_and_ersatzinfs:
				verbose(v,["\n\t\t\tNow processing participle: ", participle, ' (analyzing verbal complex)'], logfile)
				if ttttpos[-1] == 'VAFIN':
					candidate = wwords[-1]
					verbose(v,["Last word in VC: " + candidate + "\n"], logfile) #debug
					if llemmas[-1] == "haben":
#						# check tense (don't rely on Marmot morph annotations: there will be no annotation if Marmot thinks it is 'VAINF')
						if haben_pres(candidate):
							sent_perfcounter += 1
							donelist.append(participle)
							verbose(v,['\n\t\tA finite perfect aux (pres) found in verbal complex: ', candidate, ' \n\t\t\t=====> PERFECT'], logfile)
						elif haben_past(candidate): 
							sent_pluperfcounter += 1
							verbose(v,['\n\t\tB finite perfect aux (past) found in verbal complex: ', candidate, ' \n\t\t\t=====> PLUPERFECT'], logfile)
					elif llemmas[-1] == "sein":
					# check if participle is among those that take 'sein' as perfect tense auxiliary: 
						if sein_part_re.match(participle) or participle in sein_part_restdic: 
							if sein_pres(candidate):
								sent_perfcounter += 1
								verbose(v,['\n\t\tC finite perfect aux (pres) found in verbal complex: ', candidate, ' \n\t\t\t=====> PERFECT'], logfile)
							elif sein_past(candidate): 
								sent_pluperfcounter += 1
								verbose(v,['\n\t\tD finite perfect aux (past) found in verbal complex: ', candidate, ' \n\t\t\t=====> PLUPERFECT'], logfile)
					verbose(v,["\nParticiplelist after processing one participle (aux in vc): ", ", ".join(participles_and_ersatzinfs)], logfile)
				
     		# get the left bracket of the immediately dominating fkonj, fkord or simplex-element:
				else:
					verbose(v,['\n\t\t\t\tno perfect aux found in verbal complex'], logfile)
			verbose(v,["\nParticiplelist after processing all participles (looking for aux in vc): ", ", ".join(participles_and_ersatzinfs)], logfile)
                        
			# make sure we do not process a participle twice:
			verbose(v,["\n Donelist: ", ", ".join(donelist)], logfile)
			participles_and_ersatzinfs = [participle for participle in participles_and_ersatzinfs if not participle in donelist]
			verbose(v,["\n Remaining part_and_ersatzinfs: " , ", ".join(participles_and_ersatzinfs)], logfile)

			for participle in participles_and_ersatzinfs:
						verbose(v,["\n\t\t\tNow processing participle: ", participle, "\n\t\t\tLooking for a left bracket"], logfile)
						lks = get_dominating_lk(v,vc,logfile)
                                                if lks == []:
						#	verbose(v,['\n\t\t\t\tno left bracket filled with a verb in this clause',' \n\t\t\t\t=====> NO PERFECT'], logfile)
							pass
						else:
							for lk in lks:
								(wwords,ttttpos,llemmas,mmpos,mmorph) = get_wplpm(lk)
								verbose(v,['\n\t\t\t\tleft bracket: ', "'" , " ".join(wwords) , "'"], logfile)
	
		# check for perfect auxiliary in left bracket:	
								if  ttttpos[0] == ('VAFIN'):
									candidate =  wwords[0] 
									if llemmas[0] == 'haben': 
										if haben_pres(candidate):
											verbose(v,['\n\t\t\t\tE finite perfect aux (pres) found in left bracket: ', candidate, '\n\t\t\t\t=====> PERFECT'],  logfile)
											sent_perfcounter += 1
										elif haben_past(candidate):
											verbose(v,['\n\t\t\t\tF finite perfect aux (past) found in left bracket: ', candidate, '\n\t\t\t\t=====> PLUPERFECT'],  logfile)
											sent_pluperfcounter += 1
									elif llemmas[0] == 'sein':
										if sein_part_re.match(participle) or participle in sein_part_restdic:
											if sein_pres(candidate): 
												sent_perfcounter += 1
												verbose(v,['\n\t\t\t\tG finite perfect aux (pres) found in left bracket: ', candidate, '\n\t\t\t\t=====> PERFECT'],  logfile)
											elif sein_past(candidate): 
												sent_pluperfcounter += 1
												verbose(v,['\n\t\t\t\tH finite perfect aux (past) found in left bracket: ', candidate, '\n\t\t\t\t=====> PLUPERFECT'],  logfile)
									verbose(v,['\nFound a suitable aux: ', candidate, ', stop searching for more LKs'], logfile)
									break # stop looking for aux in further lk when one suitable aux has been found 
                                                            # no perfect auxiliary in left bracket:
								else:
									verbose(v, ["\n\t\t\t\tno finite perfect aux in left bracket", "\n\t\t\t\t"],  logfile)
			
		else:
			verbose(v, ["\n\t\tNo past participle or infinitive found in verbal complex","\n\t\t\t=====> NO PERFECT\n"],  logfile)

	    # check for Oberfeldumstellung with Ersatzinfinitiv (no point in using topo-parse information here, it's almost always incorrect)
	    #for simpx in s.findall('.//simpx'): do this once for every s, not for every simpx; will yield duplicated hits with embedded simpxs.
	    #	(wwords,ttttpos,llemmas,mmpos,mmorph) = get_wplpm(simpx)
	    
	    (wwords,ttttpos,llemmas,mmpos,mmorph) = get_wplpm(s)
	    words_and_tags_and_lemmas = zip(wwords,ttttpos,llemmas)
	    for i in range(0, len(words_and_tags_and_lemmas)):
			if words_and_tags_and_lemmas[i][1] == 'VAFIN':
				lastlemma = words_and_tags_and_lemmas[i][2]
				infcounter = 1
				while True:
					try:
						(nextword, nextpos, nextlemma) = words_and_tags_and_lemmas[i+infcounter]
						if nextpos in ['VVINF', 'VAINF', 'VMINF']:
							lastlemma = nextlemma
							infcounter += 1
						else:
							if lastlemma in ersatzinfinitives_dict:
								candidate = wwords[i]
								if haben_pres(candidate):
									verbose(v,['\n\t\t\t\tI Oberfeldumstellung, finite perfect aux (pres) found in verbal complex: ', candidate, '\n\t\t\t\t=====> PERFECT'],  logfile)
									sent_perfcounter += 1
								elif haben_past(candidate):
									verbose(v,['\n\t\t\t\tJ Oberfeldumstellung, finite perfect aux (past) found in verbal complex: ', candidate, '\n\t\t\t\t=====> PLUPERFECT'],  logfile)
									sent_pluperfcounter += 1
							break
					except IndexError:
						break

					
	 
	    ttttpos_string = " ".join(ttttpos)
	    verbose(v,["\n\tAll pos tags in this <simpx>: ", ttttpos_string], logfile) 
	    ofu = oberfeld_re.findall(ttttpos_string)
	    verbose(v,["\n\tOberfeldumstellung, sequence: ", ", ".join(ofu)], logfile)

	
#	    line = words_to_string(s).strip()
#	    line = line + "\t" + str(sent_perfcounter) + "\t" + str(sent_pluperfcounter)	
#	    outfile.write(line + "\n")
            verbose(v,["\n", 'Total perfect in this sentence:\t\t', str(sent_perfcounter)], logfile)
	    verbose(v,["\n", 'Total plu-perfect in this sentence:\t', str(sent_pluperfcounter), '\n'], logfile)
	
	    if sent_perfcounter > 0:
		s.set('crx_perf', "yes")
	    else:
		s.set('crx_perf', "no")
	    if sent_pluperfcounter > 0:
		s.set('crx_plu', "yes")
	    else:
		s.set('crx_plu', "no")
	
	    perfcounter = perfcounter + sent_perfcounter
	    pluperfcounter = pluperfcounter + sent_pluperfcounter

	return((str(perfcounter), str(pluperfcounter)))



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
#    outfile = codecs.open(fn_out, 'w', 'utf-8')
    outfile = open(fn_out, 'w')

    # open log file (debugging only; remove later):
    logfile = codecs.open('perfect_logfile.txt', 'w', 'utf-8')
   
    for doc in corpus_in:
	(perfect, pluperfect) = count_perfect(doc,outfile,logfile)
	doc.set('crx_perf', perfect)
	doc.set('crx_plu', pluperfect)	
	outfile.write(outify(doc) + "\n")



	   
if __name__ == "__main__":
    main()
