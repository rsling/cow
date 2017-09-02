#!/bin/bash

# FOR ARRAY JOB!!!
# Pass: dir (absolut corpus root, like "decow16"), LIST FILE, offset in file list

#SBATCH --mem=12000M
#SBATCH --time=01:30:00

set -e
set -u

# Create true in file name from 
input="`cat ${2} | tail -n +${3} | sed -n ${SLURM_ARRAY_TASK_ID},${SLURM_ARRAY_TASK_ID}p`"

inf="${1}/05divide/${input}"

odn_ner="${1}/06ner/$(dirname ${input})"
odn_marmot="${1}/07marmot/$(dirname ${input})"

ofn_ner="${1}/06ner/${input}"
ofn_marmot="${1}/07marmot/$(echo ${input} | sed 's/\.gz$//')"

mkdir -p ${odn_ner}
\rm -f ${ofn_ner}

mkdir -p ${odn_marmot}
\rm -f ${ofn_marmot}
\rm -f "${ofn_marmot}.gz"

cow16-ner ${inf} ${ofn_ner} ${NER_DE}

cow16-marmot ${inf} ${ofn_marmot} de.marmot

python /home/rsling/usr/local/cow/src/de/cow16-marmotconv-de.py ${ofn_marmot} "${ofn_marmot}.gz"

\rm -f ${ofn_marmot}

