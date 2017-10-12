#!/bin/bash

# Pass: infile, outdir

#SBATCH --mem=16M
#SBATCH --time=02:00:00

set -e
set -u

python /home/rsling/usr/local/cow/src/de/cow16-preproc-de.py ${1} "${2}/$(basename ${1})" --erase
