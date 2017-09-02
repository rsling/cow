#!/bin/bash

# Pass just the directory hash segment (no parents, no filenames in path).

#SBATCH --mem=128M
#SBATCH --time=6:30:00

set -e
set -u

RUTH="/scratch/rsling/decow16"

XML="${RUTH}/04xsplit/"
NER="${RUTH}/06ner/"
TT="${RUTH}/08tag/"
SMO="${RUTH}/09smor/"
MAR="${RUTH}/07marmot/"
BAS="${RUTH}/10baselemma/"

OUT="${RUTH}/11join/"

subdir=${1}
d_xml="${XML}/${subdir}"
d_ner="${NER}/${subdir}"
d_tt="${TT}/${subdir}"
d_smo="${SMO}/${subdir}"
d_mar="${MAR}/${subdir}"
d_bas="${BAS}/${subdir}"

d_out="${OUT}/${subdir}"

mkdir -p ${d_out}

for f in $(find ${d_xml} -type f)
do
  fn=$(basename ${f})
  f_xml="${XML}/${subdir}/${fn}"
  f_ner="${NER}/${subdir}/${fn}"
  f_tt="${TT}/${subdir}/${fn}"
  f_smo="${SMO}/${subdir}/${fn}"
  f_mar="${MAR}/${subdir}/${fn}"
  f_bas="${BAS}/${subdir}/${fn}"

  f_out="${OUT}/${subdir}/${fn}"

  echo ${f_out}
  python /home/rsling/usr/local/cow/src/common/cow16-join-anno.py ${f_out} ${f_xml} '\t|\t_\t_\t_\t_\t_\t|\t_\t|\t_\t|\t|\t|' ${f_ner} ${f_mar} --tt ${f_tt} --smor ${f_smo} --bas ${f_bas} --tag 8 --lem 9 --erase
done
