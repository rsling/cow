#!/bin/bash

set -e
set -u

source 	_opts.sh

for s in ${EXPS[@]}
do
    echo
    echo "Evaluating experiment $s"
    $EVA -s "$s"fold*tested.conll -g fold*test.conll &> "$s""results.txt"
done
