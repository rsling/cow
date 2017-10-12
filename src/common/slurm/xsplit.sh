#!/bin/bash

# Pass: infile, outdir, prefix for split, prefix for divide, fields (eg 0,1,2 for EN, 0 for DE)

#SBATCH --mem=16M
#SBATCH --time=2-00:00:00

set -e
set -u

h=`echo ${1} | md5sum | grep -o '^.\{32\}'`
dn1="${2}/${h}"
dn2="${3}/${h}"

mkdir -p ${dn1}
mkdir -p ${dn2}

# Split & zip.

# cowsplit -i ${1} -o "${dn1}/${h}" -r '^<doc ' -s 2500000
cowsplit -i ${1} -o "${dn1}/${h}" -r '^<doc ' -s 500000
gzip ${dn1}/*

# Divide.

for f in $(ls ${dn1}/*)
do
  fn="`echo ${f} | md5sum | grep -o '^.\{32\}'`.gz"
  newf="$(dirname ${f})/${fn}"
  mv ${f} ${newf}
  python /home/rsling/usr/local/cow/src/common/cow16-divider.py ${newf} "${dn2}/$(basename ${fn})" ${4}
done
