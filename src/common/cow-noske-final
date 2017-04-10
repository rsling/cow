#!/bin/bash

set -e


# Check command line options.
if [ "$#" -ne 1 ]
then
    echo "Pass exactly one parameter: corpus name."
    exit
fi


CORPUS="${1}"

echo "Reading corpus configuration..."
PATH_="`corpinfo -p "$CORPUS"`"
ATTRLIST="`corpinfo -g ATTRLIST "$CORPUS"`"


# check whether the corpus is compiled
PRIMARYATTR=`corpinfo -g word.TYPE $CORPUS >&/dev/null && echo word || corpinfo -g DEFAULTATTR $CORPUS`
COMPILED_FILE="$PATH_/$PRIMARYATTR".lex
CORPUS_COMPILED=0
test -e "$COMPILED_FILE" && CORPUS_COMPILED=1

if [ $CORPUS_COMPILED = 0 ]
then
    echo "Corpus ${PATH} is not compiled (${COMPILED_FILE} is missing})."
fi

echo "Compiling frequencies..."
for ATTR in `echo $ATTRLIST | tr "," " "`; do
    for STAT in arf docf aldf; do
	echo "Making ${STAT} for attribute ${ATTR} of corpus ${CORPUS}."
	mkstats "$CORPUS" $ATTR $STAT
    done
done


echo "Making sizes."
mksizes "$CORPUS"


echo "Checking corpus."
corpcheck $CORPUS
