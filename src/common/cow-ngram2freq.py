# -*- coding: utf-8 -*-

# Output:
# - raw freq
# - per mill
# - log per mill
# - rank

# DeReWo rank:
# N = hk(wort) := log2(f(häufigstes_wort )/f(wort))+0,5
# http://www1.ids-mannheim.de/fileadmin/kl/derewo/derewo-general-remarks.pdf

import os.path
import sys
import argparse
import gzip
from math import log

# Get DeReWo frequency band for frequency f and maximal frequency fmax.
def fband(f,fmax):
    return int(round(log((fmax/f), 2)+0.5, 0))

parser = argparse.ArgumentParser()
parser.add_argument("infile", help="input file from Colibri²")
parser.add_argument("outfile", help="output file to be created")
parser.add_argument("--erase", action='store_true', help="erase outfile if present")
parser.add_argument("--ftotal", help="total token frequency to use", type=int)
parser.add_argument("--thresh", help="frequency threshold", type=int, default=0)
args = parser.parse_args()

if os.path.exists(args.outfile):
    if args.erase:
	try:
	    os.remove(args.outfile)
	except:
	    sys.exit("Cannot delete pre-existing output file.")
    else:
	sys.exit("Output file already exists.")
try:
    inf=gzip.open(args.infile)
except:
    sys.exit("Could not open input file.")
try:
    outf=gzip.open(args.outfile, 'wb')
except:
    sys.exit("Could not open output file.")

# Get F(all).
if args.ftotal is None:
    F = 0
    for l in inf:
	l = l.decode("utf-8")
	l = l.strip()
	if "<s>" in l or "</s>" in l:
	    continue
	
	fs = l.split(" ")
	F = F + int(fs[0])
    inf.close()
    inf=gzip.open(args.infile)
else:
    F = args.ftotal

# Factor for per mill. and floor for log.
R = 1000000/float(F)
LF = abs(log(R, 10))

# Get threshold.
T = args.thresh

print "Using total frequency: " + str(F)
print "Using per mill. factor: " + str(R)
print "Using per mill. log floor: " + str(LF)

fmax = None
lastfreq = None
absrank = 1

outf.write( (u"f_raw\trank_abs\tf_permil\tf_logpermil+" + str(LF) + u"\tf_logpermil+10\tband\ttoken...\n").encode("utf-8") )

for l in inf:
	l = l.decode("utf-8")
	l = l.strip()
	if "<s>" in l or "</s>" in l:
	    continue
	
	fs = l.split(" ")
	f = int(fs[0])
	if f < T:
	    break

	# Increment or init absolute rank counter.
	if lastfreq is not None and lastfreq > f:
	    absrank = absrank + 1
	lastfreq = f

	# Init freq of highest ranked token.
	if fmax is None:
	    fmax = f

	fpm = f*R
	flpm = log(fpm, 10)
	flpm10 = flpm+10
	flpm = flpm+LF
	r = fband(f,fmax)

	outf.write( ( "\t".join([str(f), str(absrank), str(fpm), str(flpm), str(flpm10), str(r), "\t".join(fs[1:])]) + "\n" ).encode("utf-8") )

inf.close()
outf.close()
