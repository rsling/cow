#!/bin/bash

# Pass: slice list file, output dir

#SBATCH --mem=32M
#SBATCH --time=05:00:00

set -e
set -u

of="${2}/$(basename ${1} .lst).xml.gz"

echo "${1} ... ${of}"
# exit

\rm -f ${of}
gunzip -c $(cat ${1}) | gzip > ${of}
cow-xml ${of}
