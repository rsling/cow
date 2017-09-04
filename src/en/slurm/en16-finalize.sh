#!/bin/bash

# Pass: inDIR, outdir-upper
# ex.
# de16-tag.sh /scratch/rsling/decow16/05divide/fff322b4b50ba82e84c5176df2cda2c7/ /scratch/rsling/decow16/06tag

#SBATCH --mem=64M
#SBATCH --time=18:00:00

set -e
set -u

odn="${2}/$(basename ${1})"
echo "CREATE ${odn}"
mkdir -p ${odn}

for f in $(ls ${1}/*)
do
  ofn="${odn}/$(basename ${f})"
  echo "FINALIZE ${f} => ${ofn}"
  python /home/rsling/usr/local/cow/src/en/cow16-finalize-en.py ${f} ${ofn} --ngrams ${SCR_EN}/boilergrams --blank '\t_\t|\t_\t_\t|\t_\t_\t_\t_\t_\t_\t_\t_\t|' --erase 
done


