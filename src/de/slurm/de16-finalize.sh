#!/bin/bash

# Pass: list-file, indir-upper, outdir-upper (like /scratch/rsling/decow16/13final), offset in list

# Normally 55:
#SBATCH --mem=128M

# Normally 00:45:00
#SBATCH --time=01:30:00

set -e
set -u

# For testing.
#SLURM_ARRAY_TASK_ID=1

# Create true in file name from 
input="`cat ${1} | tail -n +${4} | sed -n ${SLURM_ARRAY_TASK_ID},${SLURM_ARRAY_TASK_ID}p`"

odn="${3}/$(dirname ${input})"
echo "CREATE ${odn}"
mkdir -p ${odn}

ifn="${2}/${input}"
ofn="${odn}/$(basename ${input})"
echo "FINALIZE ${ifn} => ${ofn}"
python /home/rsling/usr/local/cow/src/de/cow16-finalize-de.py ${ifn} ${ofn} --ngrams ${SCR_DE}/boilergrams --blank '\t|\t_\t_\t_\t_\t_\t|\t_\t|\t_\t|\t|\t|\t_\t_\t_\t_\t|' --erase 

