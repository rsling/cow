#!/bin/bash

# Full COW18-DE toolchain on input file ${1} to output file ${2}.

# Redefine these EXTERNALLY to the appropriate paths.
export COWTOOLS="/home/rsling/usr/local/cow/src"
export DICT_DE="${COWTOOLS}/de/data/de.lower.dict.gz"
export COWTEMP="/scratch/rsling/tmp"
export TOKCONFIG="${COWTOOLS}/de/ucto/tokconfig-de-cow"
export MATE="/home/rsling/usr/local/mateparser/transition-1.30.jar"
export MATEMODEL="/home/rsling/usr/local/mateparser/pet-ger-S2a-40-0.25-0.1-2-2-ht4-hm4-kk0"
export NER_JAR="/home/rsling/usr/local/stanford-ner/stanford-ner-3.5.2.jar"
export NER_DE="/home/rsling/usr/local/stanford-ner/classifiers/dewac_175m_600.crf.ser.gz"
export MARMOT_PATH="/home/rsling/usr/local/marmot/"
export TT_MODEL_DE="/home/rsling/usr/local/treetagger/lib/german-utf8.par"
export TT_LEXIC_DE="${COWTOOLS}/de/data/lexicon"
export TT_TMP="${COWTEMP}"
export TT_FILTER="/home/rsling/usr/local/treetagger/cmd/filter-german-tags"
export TT_TMP="${COWTEMP}"

# Do not change anything past this line.

set -u
set -e

echo "COW Toolchain: ${1} => ${2}"
echo

# Get a likely unique ID (for tmp files), plus all temp names.
id=$(echo "${1}${RANDOM}" | md5sum | grep -o '[0-9a-f]\+')
tmp_tokenised="${COWTEMP}/tokenized_${id}.xml.gz"
tmp_langfilt="${COWTEMP}/langfilt_${id}.xml.gz"
tmp_depconll="${COWTEMP}/depconll_${id}.conll"
tmp_deps="${COWTEMP}/deps_${id}.conll"
tmp_raw="${COWTEMP}/raw_${id}.vrt.gz"
tmp_ner="${COWTEMP}/ner_${id}.vrt.gz"
tmp_marmotraw="${COWTEMP}/marmotraw_${id}.vrt"
tmp_marmot="${COWTEMP}/marmot_${id}.vrt.gz"
tmp_hypertag="${COWTEMP}/hypertags_${id}.vrt.gz"
tmp_compounds="${COWTEMP}/compounds_${id}.vrt.gz"
tmp_baselemmas="${COWTEMP}/baselemmas_${id}.vrt.gz"

# Report ID.
echo
echo "Setting unique prefix to: $id..."

# Ucto.
echo
echo "Tokenising: ${1} => ${tmp_tokenised}"
gunzip -c ${1} | cow16-tokenize-de | gzip -c > ${tmp_tokenised}

# Per-sentence language detection.
echo
echo "S-Language filtering: ${tmp_tokenised} => ${tmp_langfilt}"
python ${COWTOOLS}/common/cow16-langfilter.py ${tmp_tokenised} ${tmp_langfilt} de 1 0.9 $DICT_DE 0.66

# Dependency parsing (new 2018).
echo
echo "Dependencies, getting sentences: ${tmp_langfilt} => ${tmp_depconll}"
python ${COWTOOLS}/de/cow18-get-s.py --nobrackets --conll ${tmp_langfilt} -1 > ${tmp_depconll}

echo
echo "Dependencies, parsing: ${tmp_depconll} => ${tmp_deps}"
java -Xmx3g -classpath ${MATE} is2.transitionS2a.Parser -model ${MATEMODEL} -test ${tmp_depconll} -out ${tmp_deps}

# Create s-only, token-only file.
echo
echo "Creating raw file: ${tmp_depconll} => ${tmp_raw}"
cut -f2 ${tmp_depconll} | gzip -c > ${tmp_raw}

# NER.
echo
echo "Named entities: ${tmp_raw} => ${tmp_ner}"
cow16-ner ${tmp_raw} ${tmp_ner} ${NER_DE}

# Marmot.
echo
echo "Marmot, annotation: ${tmp_raw} => ${tmp_marmotraw}"
cow16-marmot ${tmp_raw} ${tmp_marmotraw} de.marmot

echo
echo "Marmot, cleanup: ${tmp_marmotraw} => ${tmp_marmot}"
python ${COWTOOLS}/de/cow16-marmotconv-de.py ${tmp_marmotraw} ${tmp_marmot}

# Hyper-Tagging.
echo
echo "Hypertagging: ${tmp_raw} => ${tmp_hypertag}"
cow16-tag-de ${tmp_raw} ${tmp_hypertag}

# SMOR compounds.
echo
echo "Compound analysis (SMOR): ${tmp_raw} => ${tmp_compounds}"
cow16-smor ${tmp_raw} ${tmp_compounds}

# SMOR baselemma.
echo
echo "Base lemmas (SMOR): ${tmp_raw} => ${tmp_baselemmas}"
cow16-baselemma-de ${tmp_raw} ${tmp_baselemmas}

