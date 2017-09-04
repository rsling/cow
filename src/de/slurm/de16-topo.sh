#!/bin/bash

# FOR ARRAY JOB!!!
# Pass: dir (absolut corpus root, like "decow16"), LIST FILE, offset in file list

#SBATCH --mem=12G
#SBATCH --time=05:30:00

set -e
set -u

export PARSER_TMP=/scratch/rsling/tmp/
export PARSERHOME=/home/rsling/usr/local/topoparser/

# For testing.
#SLURM_ARRAY_TASK_ID=1

# Create true in file name from 
input="`cat ${2} | tail -n +${3} | sed -n ${SLURM_ARRAY_TASK_ID},${SLURM_ARRAY_TASK_ID}p`"
in_xml="${1}/11join/${input}"
in_tokens="${1}/05divide/${input}"
odn_topo="${1}/12topo/$(dirname ${input})"
ofn_topo="${1}/12topo/${input}"

echo ${input}
echo ${in_xml}
echo ${in_tokens}
echo ${odn_topo}
echo ${ofn_topo}
# exit

mkdir -p ${odn_topo}

cow16-topoparse-de ${in_xml} ${in_tokens} ${ofn_topo}


