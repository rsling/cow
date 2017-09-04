#!/bin/bash

# FOR ARRAY JOB!!!
# Pass:
#        LIST FILE,
#        output directory (like /scratch/rsling/escow/04stanfrod/)
#        offset in file list,

#SBATCH --mem=4G
#SBATCH --time=00:45:00
#
# Actually, 10 min is enough. 45 for failed processes.

set -e
set -u
PROPS=/home/rsling/usr/local/cow/src/es/cow.es.props
CSPTH=/home/rsling/usr/local/stanford-3.8

# For testing.
# SLURM_ARRAY_TASK_ID=1

# Create true in file name
input="`tail -n +${3} ${1} | sed -n ${SLURM_ARRAY_TASK_ID},${SLURM_ARRAY_TASK_ID}p`"
outpath="${2}/$(basename $(dirname ${input}))"

echo ${input}
echo ${outpath}

# For testing.
# exit

mkdir -p ${outpath}

# pass: input file, output path, props file, custom classpath
cow16-stanford ${input} ${outpath} ${PROPS} ${CSPTH}

