#!/bin/bash

# Pass: TT-indir, SMOR-indir, outdir-upper
# ex.
# de16-join-smor.sh /scratch/rsling/decow16/05divide/fff322b4b50ba82e84c5176df2cda2c7/ /scratch/rsling/decow16/09smor/fff322b4b50ba82e84c5176df2cda2c7 /scratch/rsling/decow16/10smorjoin

#SBATCH --mem=1G
#SBATCH --time=02:30:00

set -e
set -u

odn="${3}/$(basename ${1})"
echo "CREATE ${odn}"
mkdir -p ${odn}

for f in $(find ${1} -type f)
do
  smorfn="${2}/$(basename ${f})"
  ofn="${odn}/$(basename ${f})"
  echo "JOIN ${f} + ${smorfn} => ${ofn}"
  python $pypath/de/cow16-join-tt-smor.py ${f} ${smorfn} ${ofn}
done
