#!/bin/bash

# FOR ARRAY JOB!!!
# Pass: dir (absolut corpus root, like "decow16"), LIST FILE, offset in file list

#SBATCH --mem=12000M
#SBATCH --time=01:00:00

set -e
set -u

# Create true in file name from 
input="`cat ${2} | tail -n +${3} | sed -n ${SLURM_ARRAY_TASK_ID},${SLURM_ARRAY_TASK_ID}p`"
inf="${1}/03divide/${input}"
odn_ner="${1}/04ner/$(dirname ${input})"
ofn_ner="${1}/04ner/${input}"

#echo ${input}
#echo ${inf}
#echo ${odn_ner}
#echo ${ofn_ner}
#exit

mkdir -p ${odn_ner}
\rm -f ${ofn_ner}

cow16-ner ${inf} ${ofn_ner} ${NER_DE}


