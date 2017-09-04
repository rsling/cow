#!/bin/bash

# Pass: input file, output file, index prefix (=corpus slice number)

#SBATCH --mem=64M
#SBATCH --time=1-00:00:00

set -e
set -u

python ~/usr/local/cow/src/common/cow16-shufnum.py ${1} ${2} 1 ${3} 8 --erase
cow-xml ${2}
