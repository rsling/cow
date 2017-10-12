#!/bin/bash

# Pass: inDIR, outdir-upper
# ex.
# de16-smor /scratch/rsling/decow16/05divide/fff322b4b50ba82e84c5176df2cda2c7/ /scratch/rsling/decow16/09smor

#SBATCH --mem=1G
#SBATCH --time=6:00:00

set -e
set -u

odn="${2}/$(basename ${1})"
echo "CREATE ${odn}"
mkdir -p ${odn}

for f in $(ls ${1}/*)
do
  ofn="${odn}/$(basename ${f})"
  echo "TAG ${f} => ${ofn}"
  cow16-smor ${f} ${ofn}
done
