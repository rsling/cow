#!/bin/bash

# Full COW18-DE toolchain on input file ${1} to output file ${2}.

# Assumes that the COW toolchain directories are in PATH.

# Redefine these IN ENVIRONMENT to the appropriate paths.
# DO NOT MESS WITH THESE SETTINGS HERE. We rely on them on SLURM/Soroban.
[ -z ${COWTOOLS} ]    && export COWTOOLS="/home/rsling/usr/local/cow/src"
[ -z ${DICT_DE} ]     && export DICT_DE="${COWTOOLS}/de/data/de.lower.dict.gz"
[ -z ${COWTEMP} ]     && export COWTEMP="/scratch/rsling/tmp"
[ -z ${TOKCONFIG} ]   && export TOKCONFIG="${COWTOOLS}/de/ucto/tokconfig-de-cow"
[ -z ${MATE} ]        && export MATE="/home/rsling/usr/local/mateparser/transition-1.30.jar"
[ -z ${MATEMODEL} ]   && export MATEMODEL="/home/rsling/usr/local/mateparser/pet-ger-S2a-40-0.25-0.1-2-2-ht4-hm4-kk0"
[ -z ${NER_JAR} ]     && export NER_JAR="/home/rsling/usr/local/stanford-ner/stanford-ner-3.5.2.jar"
[ -z ${NER_DE} ]      && export NER_DE="/home/rsling/usr/local/stanford-ner/classifiers/dewac_175m_600.crf.ser.gz"
[ -z ${MARMOT_PATH} ] && export MARMOT_PATH="/home/rsling/usr/local/marmot/"
[ -z ${TT_MODEL_DE} ] && export TT_MODEL_DE="/home/rsling/usr/local/treetagger/lib/german-utf8.par"
[ -z ${TT_LEXIC_DE} ] && export TT_LEXIC_DE="${COWTOOLS}/de/data/lexicon"
[ -z ${TT_TMP} ]      && export TT_TMP="${COWTEMP}"
[ -z ${TT_FILTER} ]   && export TT_FILTER="/home/rsling/usr/local/treetagger/cmd/filter-german-tags"
[ -z ${TT_TMP} ]      && export TT_TMP="${COWTEMP}"
[ -z ${PARSERHOME} ]  && export PARSERHOME="/home/rsling/usr/local/cow/src/de/berkeley"
[ -z ${PARSER_TMP} ]  && export PARSER_TMP="${COWTEMP}"
[ -z ${XMX} ]         && export XMX="7g"

set -u
set -e

echo -e "\n=== COW Toolchain: ${1} => ${2} ===\n"

# Get a likely unique ID (for tmp files), plus all temp names.
id=$(echo "${1}${RANDOM}" | md5sum | grep -o '[0-9a-f]\+')
tmp_tokenised="${COWTEMP}/${id}_tokenized.xml.gz"
tmp_langfilt="${COWTEMP}/${id}_langfilt.xml.gz"
tmp_depconll="${COWTEMP}/${id}_depconll.conll"
tmp_deps="${COWTEMP}/${id}_deps.conll"
tmp_raw="${COWTEMP}/${id}_raw.vrt.gz"
tmp_ner="${COWTEMP}/${id}_ner.vrt.gz"
tmp_marmotraw="${COWTEMP}/${id}_marmotraw.vrt"
tmp_marmot="${COWTEMP}/${id}_marmot.vrt.gz"
tmp_hypertag="${COWTEMP}/${id}_hypertags.vrt.gz"
tmp_compounds="${COWTEMP}/${id}_compounds.vrt.gz"
tmp_baselemmas="${COWTEMP}/${id}_baselemmas.vrt.gz"
tmp_tokanno="${COWTEMP}/${id}_tokanno.xml.gz"
tmp_topo="${COWTEMP}/${id}_topo.xml.gz"

ANNOTATIONS="word,ne,mpos,morph,ttpos,lemma,comp,hcomp,nhcomp,f,depind,dephd,deprel,imspos,imsmorph"

# Ucto.
echo -e "\nTokenising: ${1} => ${tmp_tokenised}\n"
gunzip -c ${1} | cow16-tokenize-de | gzip -c > ${tmp_tokenised}

# Per-sentence language detection.
echo -e "\nS-Language filtering: ${tmp_tokenised} => ${tmp_langfilt}\n"
python ${COWTOOLS}/common/cow16-langfilter.py ${tmp_tokenised} ${tmp_langfilt} de 1 0.9 $DICT_DE 0.66

# Dependency parsing (new 2018).
echo -e "\nDependencies, getting sentences: ${tmp_langfilt} => ${tmp_depconll}\n"
python ${COWTOOLS}/de/cow18-get-s.py --nobrackets --conll ${tmp_langfilt} -1 > ${tmp_depconll}

echo -e "\nDependencies, parsing: ${tmp_depconll} => ${tmp_deps}\n"
java -Xmx${XMX} -classpath ${MATE} is2.transitionS2a.Parser -model ${MATEMODEL} -test ${tmp_depconll} -out ${tmp_deps}

echo -e "\nDependencies, zipping & renaming: ${tmp_deps} => ${tmp_deps}.gz\n"
gzip ${tmp_deps}
tmp_deps="${tmp_deps}.gz"

# Create s-only, token-only file.
echo -e "\nCreating raw file: ${tmp_depconll} => ${tmp_raw}\n"
cut -f2 ${tmp_depconll} | gzip -c > ${tmp_raw}

# NER.
echo -e "\nNamed entities: ${tmp_raw} => ${tmp_ner}\n"
cow16-ner ${tmp_raw} ${tmp_ner} ${NER_DE}

# Marmot.
echo -e "\nMarmot, annotation: ${tmp_raw} => ${tmp_marmotraw}\n"
cow16-marmot ${tmp_raw} ${tmp_marmotraw} de.marmot

echo -e "\nMarmot, cleanup: ${tmp_marmotraw} => ${tmp_marmot}\n"
python ${COWTOOLS}/de/cow16-marmotconv-de.py ${tmp_marmotraw} ${tmp_marmot}

# Hyper-Tagging.
echo -e "\nHypertagging: ${tmp_raw} => ${tmp_hypertag}\n"
cow16-tag-de ${tmp_raw} ${tmp_hypertag}

# SMOR compounds.
echo -e "\nCompound analysis (SMOR): ${tmp_raw} => ${tmp_compounds}\n"
cow16-smor ${tmp_raw} ${tmp_compounds}

# SMOR baselemma.
echo -e "\nBase lemmas (SMOR): ${tmp_raw} => ${tmp_baselemmas}\n"
cow16-baselemma-de ${tmp_raw} ${tmp_baselemmas}

# Join token annotations.
echo -e "\nJoin all token-level annotations: [many] => ${tmp_tokanno}\n"
python ${COWTOOLS}/common/cow16-join-anno.py ${tmp_tokanno} ${tmp_langfilt} '\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_' ${tmp_ner} ${tmp_marmot} --tt ${tmp_hypertag} --smor ${tmp_compounds} --bas ${tmp_baselemmas} --mate ${tmp_deps} --tag 4 --lem 5 --erase

# Topological parse.
echo -e "\nTopological parses, parsing: ${tmp_tokanno} => ${tmp_topo}\n"
cow18-topoparse-de ${tmp_tokanno} 4 ${tmp_topo}

echo -e "\nTopological parses, checking: ${tmp_topo}\n"
python ${COWTOOLS}/de/cow18-topocheck.py -i ${tmp_topo} --idattr 'id' --complete

# COReX.
echo -e "\nCOReX: ${tmp_topo} => ${2}\n"
python ${COWTOOLS}/corex/corex.py --erase --annotations ${ANNOTATIONS} ${tmp_topo} ${2}

# Final check.
echo -e "\nChecking XML: ${2}\n"
leadin='<?xml version="1.0" encoding="utf-8"?>\n<corpus>'
leadout='</corpus>'
cat <(echo -e ${leadin}) <(gunzip -c ${2}) <(echo -e ${leadout}) | xmlwf -r

echo -e "\n DONE. \n"

echo -e "\nUsed this environment:\n"
echo "   COWTOOLS    == ${COWTOOLS}"
echo "   DICT_DE     == ${DICT_DE}"
echo "   COWTEMP     == ${COWTEMP}"
echo "   TOKCONFIG   == ${TOKCONFIG}"
echo "   MATE        == ${MATE}"
echo "   MATEMODEL   == ${MATEMODEL}"
echo "   NER_JAR     == ${NER_JAR}"
echo "   NER_DE      == ${NER_DE}"
echo "   MARMOT_PATH == ${MARMOT_PATH}"
echo "   TT_MODEL_DE == ${TT_MODEL_DE}"
echo "   TT_LEXIC_DE == ${TT_LEXIC_DE}"
echo "   TT_TMP      == ${TT_TMP}"
echo "   TT_FILTER   == ${TT_FILTER}"
echo "   TT_TMP      == ${TT_TMP}"
echo "   PARSERHOME  == ${PARSERHOME}"
echo "   PARSER_TMP  == ${PARSER_TMP}"
echo "   XMX         == ${XMX}"

echo -e "\nUsed these file names:\n"
echo "   <IN>           == ${1}"
echo "   id             == ${id}"
echo "   tmp_tokenised  == ${tmp_tokenised}"
echo "   tmp_langfilt   == ${tmp_langfilt}"
echo "   tmp_depconll   == ${tmp_depconll}"
echo "   tmp_deps       == ${tmp_deps}"
echo "   tmp_raw        == ${tmp_raw}"
echo "   tmp_ner        == ${tmp_ner}"
echo "   tmp_marmotraw  == ${tmp_marmotraw}"
echo "   tmp_marmot     == ${tmp_marmot}"
echo "   tmp_hypertag   == ${tmp_hypertag}"
echo "   tmp_compounds  == ${tmp_compounds}"
echo "   tmp_baselemmas == ${tmp_baselemmas}"
echo "   tmp_tokanno    == ${tmp_tokanno}"
echo "   tmp_topo       == ${tmp_topo}"
echo "   <OUT>          == ${2}"

