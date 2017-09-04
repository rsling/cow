#!/bin/bash

# FOR ARRAY JOB!!!
# Pass: dir (absolut corpus root, like "decow16"), LIST FILE, offset in file list

#SBATCH --mem=1G
#SBATCH --time=00:20:00

set -e
set -u

# Create true in file name from 
input="`cat ${2} | tail -n +${3} | sed -n ${SLURM_ARRAY_TASK_ID},${SLURM_ARRAY_TASK_ID}p`"
inf="${1}/05divide/${input}"
odn_smor="${1}/09smor/$(dirname ${input})"
ofn_smor="${1}/09smor/${input}"

mkdir -p ${odn_smor}
\rm -f ${ofn_smor}

cow16-smor ${inf} ${ofn_smor} 

