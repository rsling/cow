#!/bin/bash

# Pass: infile, outdir

#SBATCH --mem=256M
#SBATCH --time=03:00:00

set -e
set -u

python /home/rsling/usr/local/cow/src/common/cow16-langfilter.py ${1} ${2}/$(basename ${1}) en 1 0.9 $DICT_EN 0.66
