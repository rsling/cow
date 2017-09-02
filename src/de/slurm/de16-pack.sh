#!/bin/bash

# Pass nothing, only input is array ID.

#SBATCH --mem=32M
#SBATCH --time=6:00:00

set -e
set -u

# For testing.
#SLURM_ARRAY_TASK_ID=15


idx=$(printf "%02d" ${SLURM_ARRAY_TASK_ID})

echo ${idx}

gunzip -c $(cat "/scratch/rsling/decow16/files.decow16a${idx}") | gzip -c > "/scratch/rsling/decow16/14slices/decow16a${idx}.xml.gz"
