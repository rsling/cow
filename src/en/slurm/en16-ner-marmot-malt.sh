#!/bin/bash

# FOR ARRAY JOB!!!
# Pass: dir (absolut corpus root, like "encow16"), LIST FILE, offset in file list

#SBATCH --mem=18000M
#SBATCH --time=00:50:00

set -e
set -u

# Create true in file name from 
input="`cat ${2} | tail -n +${3} | sed -n ${SLURM_ARRAY_TASK_ID},${SLURM_ARRAY_TASK_ID}p`"

inf="${1}/05divide/${input}"

odn_ner="${1}06ner/$(dirname ${input})"
odn_marmot="${1}07marmot/$(dirname ${input})"
odn_malt="${1}08malt/$(dirname ${input})"

ofn_ner="${1}/06ner/${input}"
ofn_marmot="${1}/07marmot/$(echo ${input} | sed 's/\.gz$//')"
ofn_malt="${1}/08malt/$(echo ${input} | sed 's/\.gz$//')"

mkdir -p ${odn_ner}
\rm -f ${ofn_ner}

mkdir -p ${odn_marmot}
\rm -f ${ofn_marmot}
\rm -f "${ofn_marmot}.gz"

mkdir -p ${odn_malt}
\rm -f ${ofn_malt}
\rm -f "${ofn_malt}.gz"

cow16-ner ${inf} ${ofn_ner} ${NER_EN}

cow16-marmot ${inf} ${ofn_marmot} en.marmot

python /home/rsling/usr/local/cow/src/en/cow16-multextconv-en.py ${ofn_marmot} "${ofn_marmot}.gz"

\rm -f ${ofn_marmot}

cow16-malt-en ${inf} ${ofn_malt}

gzip ${ofn_malt}

