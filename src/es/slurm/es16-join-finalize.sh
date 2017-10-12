#!/bin/bash

# Pass:
#        LIST FILE,
#        XML input directory (like /scratch/rsling/escow16/02xsplit)
#        Stanford input directory (like /scratch/rsling/escow16/04stanfrod/)
#        out directory (like /scratch/rsling/escow16/05join/)

#SBATCH --mem=32M
#SBATCH --time=04:00:00

# Single file takes 1 min.
# Sub-file lists were created with 175 entries,
# which will run for approx. 3 hrs.

# set -e
set -u

for f in $(cat ${1})
do
  xml="${2}/$(basename $(dirname ${f}))/$(basename ${f})"
  stanford="${3}/$(basename $(dirname ${f}))/$(basename ${f})"
  outdir="${4}/$(basename $(dirname ${f}))/"
  joinfile="${outdir}/join_$(basename ${f})"
  outfile="${outdir}/$(basename ${f})"

  echo "XML:       ${xml}"
  echo "Stanford:  ${stanford}"
  echo "Joinfile:  ${joinfile}"
  echo "Outfile:   ${outfile}"

  echo "CREATING DIRECTORY..."
  mkdir -p ${outdir}

  echo "JOINING..."
  python ~/usr/local/cow/src/common/cow16-join-stanford.py ${xml} ${stanford} ${joinfile} "3,4,0,5,6" --erase

  echo "FINALIZING..."
  python ~/usr/local/cow/src/es/cow16-finalize-es.py ${joinfile} ${outfile} "_,_,_,_,_,_,_"

  echo "DELETING..."
  \rm -f ${joinfile}

  echo "XML-CHECKING..."
  cow-xml ${outfile}

  echo -e "DONE!\n\n\n"
done
