#!/bin/bash

# Pass: inDIR, outdir-upper
# ex.
# de16-tag.sh /scratch/rsling/decow16/05divide/fff322b4b50ba82e84c5176df2cda2c7/ /scratch/rsling/decow16/06tag

#SBATCH --mem=1G
#SBATCH --time=02:30:00

set -e
set -u

odn="${2}/$(basename ${1})"
echo "CREATE ${odn}"
mkdir -p ${odn}

for f in $(ls ${1}/*)
do
  ofn="${odn}/$(basename ${f})"
  echo "TAG ${f} => ${ofn}"
  cow16-tag-de ${f} ${ofn}
done
